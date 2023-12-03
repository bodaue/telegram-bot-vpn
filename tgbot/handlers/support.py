from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import answer_keyboard, cancel_keyboard, support_keyboard

support_router = Router()


@support_router.callback_query(F.data == 'ask_support')
async def ask_support(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Если Вы столкнулись с проблемами при использовании бота или Вам нужна помощь - '
                                 'напишите прямо в <b>этом чате</b>.\n\n'

                                 'Для отмены используйте кнопку <b>«Отмена»</b>',
                                 reply_markup=cancel_keyboard)
    await state.set_state('waiting_question')


@support_router.callback_query(F.data == 'cancel')
async def cancel_support(call: CallbackQuery, state: FSMContext):
    text = '''<b>FAQ</b>

<b>1.</b> Кнопка не срабатывает, что делать?
<b>2.</b> Какой объем трафика в месяц?
<b>3.</b> Оплата прошла, но не отображается в профиле
<b>4.</b> Сколько устройств одновременно?
<b>5.</b> Какая скорость соединения?
    '''
    await call.message.edit_text(text=text,
                                 reply_markup=support_keyboard)
    await state.clear()


@support_router.message(StateFilter('waiting_question'))
async def waiting_question(message: Message, state: FSMContext, config: Config, bot: Bot):
    text = message.html_text
    user_id = message.from_user.id
    name = message.from_user.mention_html()
    text = (f'<b>Новый запрос!</b>\n\n'
            f''
            f'<b>ID пользователя:</b> {user_id}\n'
            f'<b>Пользователь:</b> {name}\n\n'
            f''
            f'<b>Текст:</b>\n'
            f'{text}')

    for admin in config.tg_bot.admin_ids:
        try:
            if message.content_type == ContentType.TEXT:
                await bot.send_message(chat_id=admin,
                                       text=text,
                                       reply_markup=answer_keyboard(user_id=user_id))
            elif message.content_type == ContentType.PHOTO:
                await bot.send_photo(chat_id=admin,
                                     caption=text,
                                     photo=message.photo[-1].file_id,
                                     reply_markup=answer_keyboard(user_id=user_id))
            elif message.content_type == ContentType.VIDEO:
                await bot.send_video(chat_id=admin,
                                     caption=text,
                                     video=message.video.file_id,
                                     reply_markup=answer_keyboard(user_id=user_id))
            elif message.content_type == ContentType.DOCUMENT:
                await bot.send_document(chat_id=admin,
                                        caption=text,
                                        document=message.document.file_id,
                                        reply_markup=answer_keyboard(user_id=user_id))
        except Exception as e:
            print(e)
    await message.answer(text='<b>✅ Сообщение было отправлено</b>')
    await state.clear()


# ответ от админа
@support_router.callback_query(F.data.contains('answer'), AdminFilter())
async def process_answer_button(call: CallbackQuery, state: FSMContext):
    data = call.data.split(':')
    user_id_to = int(data[1])
    await call.message.answer('<b>Отправьте текст для ответа</b>')
    await state.set_state('waiting_answer')
    await state.update_data(user_id_to=user_id_to)


@support_router.message(StateFilter('waiting_answer'), AdminFilter())
async def waiting_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id_to = data.get('user_id_to')
    await message.copy_to(chat_id=user_id_to)
    await message.answer(text='<b>✅ Ответ был отправлен</b>')
    await state.clear()


@support_router.callback_query(F.data == 'delete', AdminFilter())
async def delete_question(call: CallbackQuery):
    await call.message.delete()
