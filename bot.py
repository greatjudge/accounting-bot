import logging
import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from config_reader import config, FSMModeEnum

from handlers import common, form_messages, edit_options, uploading_mes
from middlewares.db import DbSessionMiddleware

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from telethon_app.forward import tel_client


async def main():
    db_url = f'postgresql+psycopg://{config.db_user}:{config.db_password}' \
             f'@{config.db_addr}/{config.db_name}'
    engine = create_async_engine(db_url, echo=True)
    sessionmaker = async_sessionmaker(engine)

    if config.fsm_mode == FSMModeEnum.MEMORY:
        storage = MemoryStorage()
    else:
        storage = RedisStorage.from_url(
            url=f"{config.redis.dsn}/{config.redis.fsm_db_id}",
            connection_kwargs={"decode_responses": True}
        )

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=config.bot_token.get_secret_value())

    dp = Dispatcher(storage=storage)
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.include_routers(
        common.router, form_messages.router,
        edit_options.router, uploading_mes.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
    # tel_client.start()
