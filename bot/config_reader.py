from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import SecretStr, DirectoryPath, BaseModel, RedisDsn


class Redis(BaseModel):
    dsn: RedisDsn
    fsm_db_id: int
    data_db_id: int


class FSMModeEnum(str, Enum):
    MEMORY = "memory"
    REDIS = "redis"


class Settings(BaseSettings):
    bot_token: SecretStr
    channel_id: int

    admins: list[int]

    redis: Redis
    fsm_mode: FSMModeEnum

    api_id: SecretStr
    api_hash: SecretStr
    session_string: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'


config = Settings()
