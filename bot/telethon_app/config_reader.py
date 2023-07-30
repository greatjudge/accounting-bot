from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    channel_id: int
    upload_destination_id: int

    api_id: SecretStr
    api_hash: SecretStr
    session_string: SecretStr

    class Config:
        env_file = 'telethon_app/.env.telapp'
        env_file_encoding = 'utf-8'


tel_config = Settings()
