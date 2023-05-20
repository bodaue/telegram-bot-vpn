from datetime import datetime
from typing import Union

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pymongo.errors import DuplicateKeyError

from tgbot.db.db_api import users, subs
from tgbot.services.yoomoney_api import PaymentYooMoney
from tgbot.keyboards.inline import support_keyboard, payment_keyboard, os_keyboard, profile_keyboard
from tgbot.keyboards.reply import menu_keyboard

user_router = Router()


@user_router.message(CommandStart(), flags={'throttling_key': 'default'})
async def user_start(message: Message):
    text = ('<b>Вы находитесь в главном меню</b>\n\n'

            '<b>Оплатить</b> - первичная оплата\n'
            '<b>Настроить</b> - подключение после оплаты\n'
            '<b>Профиль</b> - продление по истечении срока\n'
            '<b>Поддержка</b> - чат со службой поддержки\n')
    await message.answer(text=text,
                         reply_markup=menu_keyboard)
    _id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username
    try:
        await users.insert_one(
            {'_id': message.from_user.id,
             'name': name,
             'username': username,
             'date': message.date})
    except DuplicateKeyError:
        pass


@user_router.callback_query(F.data == 'prolong')
@user_router.message(F.text == 'Оплатить', flags={'throttling_key': 'payment'})
async def process_pay(query: Union[Message, CallbackQuery], state: FSMContext):
    user_id = query.from_user.id
    date = datetime.now()

    sub = await subs.find_one(filter={'user_id': user_id,
                                      'end_date': {'$gt': date}})
    sub_text = ''
    if sub:
        sub_text = '\n<i>У вас уже активирована подписка. При оплате подписка будет продлена на год.</i>'

    text = f'''<b>Оплата</b>
    
<b>Годовая стоимость:</b> 3 руб. {sub_text}

Оплата банковской картой через платежную систему <b>ЮМани.</b>
Все платежи идут через систему Telegram, это надёжно и удобно'''
    payment = PaymentYooMoney(amount=3)
    payment.create()

    if isinstance(query, Message):
        await query.answer(text=text,
                           reply_markup=payment_keyboard(payment_id=payment.id,
                                                         invoice=payment.invoice))
    else:
        await query.message.edit_text(text=text,
                                      reply_markup=payment_keyboard(payment_id=payment.id,
                                                                    invoice=payment.invoice))
    await state.set_state('check_payment')
    await state.update_data(payment_id=payment.id,
                            amount=payment.amount)


@user_router.callback_query(F.data == 'settings')
@user_router.message(F.text == 'Настроить')
async def process_settings(query: Union[Message, CallbackQuery]):
    user_id = query.from_user.id

    message = query if isinstance(query, Message) else query.message

    sub = await subs.find_one(filter={'user_id': user_id,
                                      'end_date': {'$gt': datetime.now()}})
    if not sub:
        await message.answer('<b>У Вас не активирована подписка.</b>')
        return

    await message.answer(text='''<b>Настройки</b>

У Вас активирована подписка, поэтому Вам доступны настройки для подключения.\n
Выберите операционную систему вашего устройства.''',
                         reply_markup=os_keyboard)


@user_router.message(F.text == 'Профиль')
async def process_profile(message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = f'<b>Юзернейм:</b> {message.from_user.username}\n' if message.from_user.username else ''

    sub = await subs.find_one(filter={'user_id': user_id,
                                      'end_date': {'$gt': datetime.now()}})
    if sub:
        end_date = sub['end_date'].strftime('%d.%m.%Y')
        sub_text = ('<b>Статус подписки:</b> активирована\n'
                    f'<b>Срок действия:</b> до {end_date}')
    else:
        sub_text = '<b>Статус подписки:</b> не активирована'

    text = ('<b>Профиль</b>\n\n'

            f'<b>Ваш ID:</b> {user_id}\n'
            f'<b>Имя:</b> {name}\n'
            f'{username}\n'
            f''
            f'{sub_text}\n'
            f'<b>Город:</b> Чехия')

    await message.answer(text=text,
                         reply_markup=profile_keyboard)


@user_router.message(F.text == 'Поддержка')
async def process_support(message: Message):
    text = '''<b>FAQ</b>
    
<b>1.</b> Кнопка не срабатывает, что делать?
<b>2.</b> Какой объем трафика в месяц?
<b>3.</b> Оплата прошла, но не отображается в профиле
<b>4.</b> Сколько устройств одновременно?
<b>5.</b> Какая скорость соединения?
'''
    await message.answer(text=text,
                         reply_markup=support_keyboard)
