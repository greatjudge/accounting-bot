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

    redis: Redis
    fsm_mode: FSMModeEnum

    file_directory: DirectoryPath

    db_addr: str
    db_name: str
    db_user: str
    db_password: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'


config = Settings()
