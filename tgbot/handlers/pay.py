from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from pymongo import ReturnDocument

from tgbot.db.db_api import payments, subs
from tgbot.keyboards.inline import settings_keyboard
from tgbot.services.yoomoney_api import PaymentYooMoney, NoPaymentFound

pay_router = Router()


@pay_router.callback_query(F.data.contains('check_payment'), StateFilter('check_payment'),
                           flags={'throttling_key': 'callback'})
async def check_payment(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    data = call.data.split(':')
    payment_id = data[1]

    state_data = await state.get_data()
    state_payment_id = state_data.get('payment_id')
    amount = state_data.get('amount')

    if payment_id != state_payment_id:
        await call.answer('Вы начинали новую оплату ниже.')
        return

    payment = PaymentYooMoney(id=payment_id, amount=amount)
    try:
        amount = payment.check_payment()
    except NoPaymentFound:
        await call.answer('Оплата не найдена, сначала выполните оплату.')
    else:
        date = datetime.now()
        payments.insert_one({'user_id': user_id,
                             'amount': amount,
                             'payment_type': 'YooMoney',
                             'date': date})
        sub = await subs.find_one(filter={'user_id': user_id,
                                          'end_date': {'$gt': date}})
        if sub:
            end_date = sub['end_date'] + timedelta(days=365)
            sub = await subs.find_one_and_update(filter={'user_id': user_id,
                                                         'end_date': {'$gt': date}},
                                                 update={'$set': {'end_date': end_date}},
                                                 return_document=ReturnDocument.AFTER)
            end_date = sub['end_date'].strftime('%d.%m.%Y')
            await call.message.edit_text(text='Оплата успешно произведена\n'
                                              f'<b>Срок действия:</b> до {end_date}\n\n'
                                              f''
                                              f'Ваш аккаунт автоматически продлен на год. Продолжайте пользоваться'
                                              f' сервисом без дополнительных настроек.')
        else:
            await subs.delete_many(filter={'user_id': user_id})

            start_date = datetime.now()
            end_date = start_date + timedelta(days=365)
            await subs.insert_one(document={'user_id': user_id,
                                            'start_date': start_date,
                                            'end_date': end_date})
            end_date = end_date.strftime('%d.%m.%Y')

            await call.message.edit_text(text=f'Оплата успешно произведена\n'
                                              f'<b>Срок действия:</b> до {end_date}\n\n'
                                              f''
                                              f'Перейдите в "Настройки" для подключения Вашего устройства к VPN',
                                         reply_markup=settings_keyboard)
        await state.clear()
