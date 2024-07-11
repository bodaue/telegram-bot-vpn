import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from tgbot.config import config
from tgbot.handlers.pay import pay_router
from tgbot.handlers.settings import settings_router
from tgbot.handlers.support import support_router
from tgbot.handlers.user import user_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.misc.logger import register_logger, logger
from tgbot.misc.mongostorage import MongoStorage
from tgbot.misc.set_bot_commands import set_default_commands
from tgbot.services import broadcaster


async def on_startup(bot: Bot, admin_ids: list[int]) -> None:
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен!")


def register_global_middlewares(dp: Dispatcher) -> None:
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())


def register_global_filters(dp: Dispatcher) -> None:
    dp.message.filter(F.chat.type == "private")
    dp.callback_query.filter(F.message.chat.type == "private")


async def main() -> None:
    register_logger()

    if config.common.use_mongo_storage:
        storage = MongoStorage(
            uri="mongodb://127.0.0.1:27017/",
            database="FSM_states",
            collection_states="states",
        )
    else:
        storage = MemoryStorage()

    bot = Bot(
        token=config.common.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    for router in [user_router, support_router, pay_router, settings_router]:
        dp.include_router(router)

    register_global_filters(dp)
    register_global_middlewares(dp)

    await set_default_commands(bot)

    await on_startup(bot, config.common.admins)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Stopping bot")
