import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandObject
from aiogram.filters.callback_data import CallbackData

from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_reader import config

from handlers import common, messages

from random import randint


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(common.router, messages.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
