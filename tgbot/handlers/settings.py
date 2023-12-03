from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery

from tgbot.db.db_api import subs

settings_router = Router()


@settings_router.callback_query(F.data.contains('choose_os'), flags={'throttling_key': 'callback'})
async def choose_os(call: CallbackQuery):
    user_id = call.from_user.id
    date = datetime.now()

    sub = await subs.find_one(filter={'user_id': user_id,
                                      'end_date': {'$gt': date}})
    if not sub:
        await call.answer(text='<b>У Вас не активирована подписка.</b>', show_alert=True)
        return

    data = call.data.split(':')
    os = data[1]

    # дописать выдачу доступа к VPN'у
