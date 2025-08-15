from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Главная клавиатура с бургером
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text= "☰ Модель" )
            ]
        ]
    )


def select_provider_ai_keyboard() -> InlineKeyboardMarkup:
    """
    Выбор провайдера AI
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤖 OpenAI", callback_data="provider_openai"),
            InlineKeyboardButton(text="🧠 DeepSeek", callback_data="provider_deepseek")
        ]
    ])
    return keyboard

def change_provider_keyboard() -> InlineKeyboardMarkup:
    """
    Одна кнопка для перехода к меню выбора провайдера
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Сменить провайдера", callback_data="change_provider")]
    ])

def select_model_openai_keyboard(models: dict) -> InlineKeyboardMarkup:
    """
    Выбор модели OpenAI
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=model_name, callback_data=f"model_{model_key}")]
        for model_key, model_name in models.items()
    ])
    return keyboard


