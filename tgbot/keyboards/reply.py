from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оплатить"), KeyboardButton(text="Настроить")],
        [KeyboardButton(text="Профиль"), KeyboardButton(text="Поддержка")],
    ],
    resize_keyboard=True,
)
