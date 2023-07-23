import logging
import asyncio

from aiogram import Bot, Dispatcher, types, F
from config_reader import config

from handlers import common, form_messages, edit_options


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(common.router, form_messages.router, edit_options.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
