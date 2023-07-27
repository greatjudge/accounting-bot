from telethon_app.config_reader import tel_config
from datetime import datetime

from telethon.sync import TelegramClient
from telethon.sessions import StringSession


tel_client = TelegramClient(
    StringSession(tel_config.session_string.get_secret_value()),
    tel_config.api_id.get_secret_value(),
    tel_config.api_hash.get_secret_value()
)


async def forward_mes_for_month(date: datetime, text: str):
    async with tel_client:
        await tel_client.send_message(tel_config.channel_id, f'ВЫГРУЗКА {text}:')
        msg_ids = []
        async for msg in tel_client.iter_messages(tel_config.channel_id):
            if all((msg.message is not None,
                    msg.forward is None,
                    msg.photo or msg.file,
                    msg.date.year == date.year,
                    msg.date.month == date.month)):
                msg_ids.append(msg.id)
        await tel_client.forward_messages(
            tel_config.upload_destination_id,
            msg_ids,
            tel_config.channel_id
        )
        await tel_client.send_message(tel_config.channel_id, 'Конец выгрузки.')
