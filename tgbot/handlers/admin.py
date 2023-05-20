from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())

mediagroups = {}


@admin_router.message(Command(commands='test'))
async def process_test(message: Message, state: FSMContext):
    pass
