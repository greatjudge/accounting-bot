from datetime import datetime
from bot.config_reader import config

from telethon.sync import TelegramClient
from telethon.sessions import StringSession


tel_client = TelegramClient(
    StringSession(config.session_string.get_secret_value()),
    config.api_id.get_secret_value(),
    config.api_hash.get_secret_value()
)


async def forward_mes_for_month(chat_id: int, date: datetime, text: str):
    async with tel_client:
        await tel_client.send_message(
            chat_id,
            f'ВЫГРУЗКА {text}:'
        )
        msg_ids = []
        async for msg in tel_client.iter_messages(config.channel_id):
            if all((msg.message is not None,
                    msg.forward is None,
                    msg.photo or msg.file,
                    msg.date.year == date.year,
                    msg.date.month == date.month)):
                msg_ids.append(msg.id)
        await tel_client.forward_messages(
            chat_id,
            msg_ids,
            config.channel_id
        )
        await tel_client.send_message(chat_id, 'Конец выгрузки.')
