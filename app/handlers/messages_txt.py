from __future__ import annotations

import os
import tempfile
from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Document

from app.fsm import BotStates
from app.service.txt_utils import read_text_file, is_text_filename, should_prefer_tail_by_ext
from app.service.ai_clients import get_ai_response

router = Router()

MAX_FILE_SIZE = 2 * 1024 * 1024   # 2 MB
MAX_CONTEXT   = 100_000           # ограничим контекст

def _is_text_document(doc: Document) -> bool:
    # 1) по mime типу
    if doc.mime_type and doc.mime_type.startswith("text/"):
        return True
    # 2) по расширению
    return is_text_filename(doc.file_name)

def _is_code_ext(name: str | None) -> bool:
    """Простая эвристика по названию файла, чтобы понять, что это код."""
    name = (name or "").lower()
    return name.endswith((
        ".py",".js",".ts",".tsx",".vue",".java",".kt",".rs",".go",".rb",".php",".pl",".swift",
        ".c",".cpp",".h",".hpp",".cs",".r",".sql",".sh",".bat",".ps1"
    ))

@router.message(StateFilter(BotStates.ready), F.document)
async def handle_text_document(message: Message, state: FSMContext):
    """Обработка текстовых документов, загружаемых пользователем.
    Поддерживаются файлы до 5 МБ с текстовым содержимым.
    После загрузки файл читается и его текст сохраняется в состояние.
    Пользователь может затем задавать вопросы по содержимому файла.
    """
    doc = message.document
    if not _is_text_document(doc):
        # оставляем другим обработчикам (pdf/xlsx и т.п.)
        return

    if doc.file_size and doc.file_size > MAX_FILE_SIZE:
        await message.answer("Файл слишком большой. Пришлите текстовый файл до 5 МБ.")
        return

    tmpdir = tempfile.mkdtemp(prefix="txt_")
    filename = doc.file_name or f"{doc.file_unique_id}.txt"
    path = os.path.join(tmpdir, filename)
    await message.bot.download(doc, destination=path)

    prefer_tail = should_prefer_tail_by_ext(filename)  # для логов — хвост
    text = read_text_file(path, max_chars=MAX_CONTEXT, prefer_tail=prefer_tail)

    if not text:
        await message.answer("Файл пустой или не удалось прочитать текст.")
        return

    await state.update_data(
        file_text=text,
        file_name=filename,
        file_ext=os.path.splitext(filename)[1].lower(),
        file_len=len(text),
    )

    tip = " (взяли хвост файла)" if prefer_tail else ""
    await message.answer(
        f"📄 «{filename}» загружен{tip}. В контекст добавлено {len(text)} символов.\n\n"
        "Дальше:\n"
        "• /summary — краткое резюме\n"
        "• Или задайте вопрос по содержимому файла."
    )

    await state.set_state(BotStates.ready)
    await message.answer("После работы с файлом чтобы продолжить чат введи команду /clear или выбери её из меню")

@router.message(StateFilter(BotStates.ready), Command("summary"))
async def cmd_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("file_text")
    ext  = (data.get("file_ext") or "").lower()
    name = data.get("file_name") or "файл"

    if not text:
        await message.answer("Сначала пришлите текстовый файл 📎")
        return

    provider = data.get("provider")
    model    = data.get("model")

    # Чуть разные подсказки для кода/логов/прочего
    if ext in (".log", ".out", ".err"):
        system_prompt = (
            f"Ты помощник по анализу логов. Проанализируй лог {name}: "
            "суммаризируй ключевые события, ошибки/stack traces, аномалии, последние 10-20 значимых записей, "
            "возможные причины и что проверить дальше."
        )
    elif _is_code_ext(name):
        system_prompt = (
            f"Ты помощник по обзору кода. По файлу {name} дай краткое резюме: назначение, ключевые функции/классы, "
            "основные зависимости, потенциальные проблемы/anti-patterns, TODO/комментарии."
        )
    else:
        system_prompt = "Суммаризируй текст кратко и структурированно, сохраняя факты и числа."

    prompt = f"{system_prompt}\n\n=== ФАЙЛ НАЧАЛО ===\n{text}\n=== ФАЙЛ КОНЕЦ ==="

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        resp = await get_ai_response(prompt, provider, model)
        await message.answer(resp or "Пусто.")
    except Exception as e:
        await message.answer(f"Ошибка анализа: {e}")

    await state.set_state(BotStates.ready)
    await message.answer("Можете задать новые вопросы по файлу или просто продолжить диалог с AI.")


@router.message(StateFilter(BotStates.ready), Command("clear"))
async def cmd_clear(message: Message, state: FSMContext):
    """Очистка контекста файла из состояния.
    """
    data = await state.get_data()
    for k in ("file_text", "file_name", "file_ext", "file_len"):
        data.pop(k, None)
    await state.set_data(data)
    await message.answer("Контекст файла очищен.")
