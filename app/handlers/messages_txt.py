from __future__ import annotations

import os
import tempfile
from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.fsm import BotStates
from app.service.txt_utils import read_text_file
from app.service.ai_clients import get_ai_response

router = Router()

MAX_FILE_SIZE = 2 * 1024 * 1024   # 2 MB
MAX_CONTEXT   = 100_000           # ограничим контекст

def _is_text_filename(name: str | None) -> bool:
    name = (name or "").lower()
    return name.endswith(".txt") or name.endswith(".md")

@router.message(StateFilter(BotStates.ready), F.document)
async def handle_text_document(message: Message, state: FSMContext):
    doc = message.document
    if not _is_text_filename(doc.file_name):
        # Не мешаем другим обработчикам (pdf/xlsx/и т.п.) — просто выходим
        return

    if doc.file_size and doc.file_size > MAX_FILE_SIZE:
        await message.answer("Файл слишком большой. Пришлите .txt/.md до 2 МБ.")
        return

    # Скачиваем во временную папку
    tmpdir = tempfile.mkdtemp(prefix="txt_")
    filename = doc.file_name or f"{doc.file_unique_id}.txt"
    path = os.path.join(tmpdir, filename)
    await message.bot.download(doc, destination=path)

    # Читаем текст
    text = read_text_file(path, max_chars=MAX_CONTEXT)
    if not text:
        await message.answer("Файл пустой или не удалось прочитать текст.")
        return

    # Кладём в FSM
    await state.update_data(file_text=text, file_name=filename, file_ext=".txt", file_len=len(text))

    await message.answer(
        f"📄 Файл «{filename}» загружен. В контекст добавлено {len(text)} символов.\n\n"
        "Дальше:\n"
        "• /summary — краткое резюме\n"
        "• или просто задайте вопрос по тексту (если ваш общий обработчик это поддерживает)."
    )

@router.message(StateFilter(BotStates.ready), Command("summary"))
async def cmd_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("file_text")
    if not text:
        await message.answer("Сначала пришлите .txt или .md файл 📎")
        return

    user = await state.get_data()
    provider = user.get("provider")
    model = user.get("model")

    prompt = (
        "Суммаризируй следующий текст кратко и структурированно (короткие пункты, цифры сохранить):\n\n"
        f"{text}"
    )
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        resp = await get_ai_response(prompt, provider, model)
        await message.answer(resp or "Пустой ответ.")
    except Exception as e:
        await message.answer(f"Ошибка анализа: {e}")

@router.message(StateFilter(BotStates.ready), Command("clear"))
async def cmd_clear(message: Message, state: FSMContext):
    # Быстрый сброс загруженного текста
    data = await state.get_data()
    for k in ("file_text", "file_name", "file_ext", "file_len"):
        if k in data:
            data.pop(k)
    await state.set_data(data)
    await message.answer("Контекст файла очищен. Можно загружать новый .txt/.md.")
