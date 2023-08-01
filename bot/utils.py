import logging

from aiogram import Bot
from aiogram.types import BotCommand


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


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='сформировать и отправить сообщение'
        ),
        BotCommand(
            command='edit',
            description='редактировать поля сообщения'
        ),
        BotCommand(
            command='cancel',
            description='отменить действие'
        ),
        BotCommand(
            command='upload_current',
            description='выгрузка за текущий месяц'
        ),
        BotCommand(
            command='upload_prev',
            description='выгрузка за предыдущий месяц'
        ),
        BotCommand(
            command='add_user',
            description='добавить пользователя'
        ),
        BotCommand(
            command='remove_user',
            description='удалить пользователя'
        ),
        BotCommand(
            command='add_admin',
            description='сделать пользователя админом'
        )
    ]
    await bot.set_my_commands(commands)
