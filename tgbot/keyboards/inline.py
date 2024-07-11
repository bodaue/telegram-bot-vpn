from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_support")]
    ]
)


def answer_keyboard(user_id):
    answer_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Ответить", callback_data=f"answer:{user_id}"
                ),
                InlineKeyboardButton(text="❎ Удалить", callback_data="delete"),
            ],
        ]
    )
    return answer_markup


def payment_keyboard(payment_id: str, invoice: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=invoice)],
            [
                InlineKeyboardButton(
                    text="Проверить платеж", callback_data=f"check_payment:{payment_id}"
                )
            ],
        ]
    )

    return keyboard


cancel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="cancel")]]
)

profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Продлить подписку", callback_data="prolong")]
    ]
)

os_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Iphone", callback_data="choose_os:iphone"),
            InlineKeyboardButton(text="Android", callback_data="choose_os:android"),
        ],
        [
            InlineKeyboardButton(text="MacOS", callback_data="choose_os:macos"),
            InlineKeyboardButton(text="Windows", callback_data="choose_os:windows"),
        ],
    ]
)

settings_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Настроить", callback_data="settings")]]
)
