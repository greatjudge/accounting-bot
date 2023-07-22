from pydantic_settings import BaseSettings
from pydantic import SecretStr, DirectoryPath


class Settings(BaseSettings):
    bot_token: SecretStr
    file_directory: DirectoryPath

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
