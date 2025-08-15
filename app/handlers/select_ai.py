# app/handlers/select_ai.py
from aiogram import Router, F                               # (1) добавили F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from app.fsm import BotStates
from app.keyboards.keybord import select_model_openai_keyboard, select_provider_ai_keyboard, change_provider_keyboard
from app.service.dist_model import OPENAI_MODELS

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Старт бота с DeepSeek по умолчанию и возможностью смены провайдера"""
    # устанавливаем дефолтное состояние
    await state.update_data(provider="deepseek", model="deepseek-chat")
    # Переводим бота в состояние ready
    await state.set_state(BotStates.ready)

    await message.answer(
        "🧠 По умолчанию в  качестве AI стоит DeepSeek! Бот готов к работе.\n"
        "Если нужно — можете сменить провайдера.",
        reply_markup=change_provider_keyboard()
    )

@router.callback_query(lambda c: c.data == "change_provider")
async def show_provider_menu(callback: CallbackQuery, state: FSMContext):
    """Показываем меню выбора провайдера по запросу"""
    await callback.message.edit_text(
        "👋 Выберите AI провайдера:",
        reply_markup=select_provider_ai_keyboard()
    )
    await state.set_state(BotStates.choosing_provider)
    await callback.answer()


# Было: @router.callback_query(lambda c: c.data.startswith("provider_"))
@router.callback_query(F.data.startswith("provider_"))      # (1) надёжный фильтр
async def process_provider_choice(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора провайдера"""
    # Получение выбранного провайдера
    provider = callback.data.split("_", 1)[1]

    if provider == "openai":
        # Переходим к выбору модели
        await callback.message.edit_text(
            "🤖 Вы выбрали OpenAI. Теперь выберите модель:",
            reply_markup=select_model_openai_keyboard(OPENAI_MODELS)
        )
        # Обновляем состояние
        await state.update_data(provider="openai")
        # Переходим в состояние выбора модели
        await state.set_state(BotStates.choosing_model)

    elif provider == "deepseek":
        """Просто меняем текст на "Бот готов к работе".
        Сохраняем в state провайдера "deepseek" и модель "deepseek-chat". 
        Переводим бота сразу в состояние ready (можно уже отправлять сообщения)."""
        await callback.message.edit_text("🧠 Вы выбрали DeepSeek! Бот готов к работе.")
        await state.update_data(provider="deepseek", model="deepseek-chat")
        await state.set_state(BotStates.ready)

    await callback.answer()

# Было: @router.callback_query(lambda c: c.data.startswith("model_"))
@router.callback_query(F.data.startswith("model_"))         # (1) надёжный фильтр
async def process_model_choice(callback: CallbackQuery, state: FSMContext):
    # Получение выбранной модели
    model = callback.data.split("_", 1)[1]
    # Извлечение названия модели
    model_name = OPENAI_MODELS.get(model, model)

    await callback.message.edit_text(
        f"✅ Настройка завершена!\n"
        f"🤖 Провайдер: OpenAI\n"
        f"🎯 Модель: {model_name}\n\n"
        f"Теперь вы можете отправлять сообщения для обработки."
    )
    # Обновляем состояние
    await state.update_data(provider="openai", model=model)
    # Переходим в состояние готовности. бот готов принимать обычные текстовые сообщения и отвечать через выбранную модель.
    await state.set_state(BotStates.ready)
    # Подтверждаем выбор
    await callback.answer()

# Было: @router.message(Command("model"), StateFilter(BotStates.ready))
# (2) разрешим /model в любом состоянии — так удобнее из меню
@router.message(Command("model"))
async def cmd_model(message: Message, state: FSMContext):
    """"смена или выбор модели" вручную, когда бот уже запущен."""
    data = await state.get_data()
    provider = data.get("provider")
    if provider == "openai":
        kb: InlineKeyboardMarkup = select_model_openai_keyboard(OPENAI_MODELS)
        await message.answer("Выберите модель OpenAI:", reply_markup=kb)
        await state.set_state(BotStates.choosing_model)
    elif provider == "deepseek":
        await message.answer("Для DeepSeek модель фиксирована: deepseek-chat")
    else:
        await message.answer("Сначала выберите провайдера:", reply_markup=select_provider_ai_keyboard())
        await state.set_state(BotStates.choosing_provider)


@router.message(Command("provider"))
async def cmd_provider(message: Message, state: FSMContext):
    await message.answer("Выберите AI провайдера:", reply_markup=select_provider_ai_keyboard())
    await state.set_state(BotStates.choosing_provider)