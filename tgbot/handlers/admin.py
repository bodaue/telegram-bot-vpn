from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command(commands="test"))
async def process_test(message: Message):
    print(message)
