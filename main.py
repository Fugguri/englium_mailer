import asyncio
import logging


# from DB_connectors.sqlite_connection import Database
from DB_connectors.sqlite_connection import Database

from config import load_config
from keyboards.keyboards import Keyboards
from handlers.users import register_user_handlers
from handlers.admin import register_admin_handlers
from handlers.users import user_active_clients

from middlewares.environment import EnvironmentMiddleware

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
logger = logging.getLogger(__name__)


async def register_all_middlewares(dp, config, keyboards, db):

    dp.middleware.setup(EnvironmentMiddleware(
        config=config, db=db, keyboards=keyboards))


def register_all_handlers(dp, config, keyboards, db):
    register_user_handlers(dp, config, keyboards, db)
    register_admin_handlers(dp, config, keyboards, db)

    db.cbdt()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config("config.json", "texts.yml")
    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    db = Database(config.tg_bot.db_name)
    # db = Database(cfg=config)
    dp = Dispatcher(bot, storage=storage)
    kbs = Keyboards(config)

    bot['keyboards'] = kbs
    bot['config'] = config
    await register_all_middlewares(dp, config, kbs, db)
    register_all_handlers(dp, config, kbs, db)

    dp.skip_updates = False
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
