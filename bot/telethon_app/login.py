from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from config_reader import tel_config


with TelegramClient(StringSession(),
                    tel_config.api_id.get_secret_value(),
                    tel_config.api_hash.get_secret_value()) as client:
    print(client.session.save())
