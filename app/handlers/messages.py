import openai
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from os import getenv

from app.fsm import BotStates
from app.service.ai_clients import get_ai_response

router = Router()

openai.api_key = getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = getenv("DEEPSEEK_API_KEY")

@router.message(StateFilter(BotStates.ready))
async def handle_user_message(message: Message, state: FSMContext):
    """Обработка сообщений пользователя в состоянии готовности
    (после выбора провайдера и модели)"""

    user_data = await state.get_data()
    provider = user_data.get("provider")
    model = user_data.get("model")
    file_text = user_data.get("file_text")

    if not message.text:
        await message.answer("Пожалуйста, отправьте текстовое сообщение")
        return

    # Показываем индикатор печати
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        if file_text:
            # Q&A по загруженному файлу
            prompt = (
                "Ответь на вопрос, используя ТОЛЬКО информацию из документа. "
                "Если ответа нет в документе — честно скажи что данных недостаточно и укажи, каких именно.\n\n"
                f"=== ДОКУМЕНТ НАЧАЛО ===\n{file_text}\n=== ДОКУМЕНТ КОНЕЦ ===\n\n"
                f"Вопрос: {message.text}"
            )
        else:
            # Обычный чат
            prompt = message.text
        # Используем универсальную функцию для получения ответа от любого провайдера
        response = await get_ai_response(prompt, provider, model)
        if response and response.strip():
            # Отправляем ответ пользователю
            if len(response) > 4000:
                for i in range(0, len(response), 4000):
                    await message.answer(response[i:i + 4000])
            else:
                await message.answer(response)
        else:
            await message.answer("Пустое сообщение")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")







