import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from bot.config_reader import config, FSMModeEnum
from bot.handlers import common, form_messages, edit_options, uploading_mes, users

from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.auth import AuthMiddleware

from bot.db.requests import add_user


def config_filelog(filename: str):
    format_file = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    log_handler = logging.FileHandler(filename)
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(format_file)

    for logger_name in [
        'sqlalchemy', 'aiogram.dispatcher',
        'aiogram.event', 'aiogram.middlewares',
        'aiogram.webhook'
    ]:
        logging.getLogger(logger_name).addHandler(log_handler)


async def add_admins(session, usr_ids: list[int]):
    for uid in usr_ids:
        try:
            await add_user(session, uid, is_admin=True)
        except IntegrityError:
            pass


async def main():
    logging.basicConfig(level=logging.INFO)
    config_filelog('bot.log')

    # postgres db url
    # postgres_url = f'postgresql+psycopg://{config.db_user}:{config.db_password}' \
    #          f'@{config.db_addr}/{config.db_name}'

    sqlite_url = "sqlite+aiosqlite:///bot.db"
    engine = create_async_engine(sqlite_url, echo=True)

    sessionmaker = async_sessionmaker(engine)

    async with sessionmaker() as session:
        await add_admins(session, config.admins)

    if config.fsm_mode == FSMModeEnum.MEMORY:
        storage = MemoryStorage()
    else:
        storage = RedisStorage.from_url(
            url=f"{config.redis.dsn}/{config.redis.fsm_db_id}",
            connection_kwargs={"decode_responses": True}
        )

    bot = Bot(token=config.bot_token.get_secret_value())

    dp = Dispatcher(storage=storage)

    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.update.middleware(AuthMiddleware())

    dp.include_routers(
        common.router, form_messages.router,
        edit_options.router, uploading_mes.router,
        users.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
