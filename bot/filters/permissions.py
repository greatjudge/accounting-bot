from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.db.models import User


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, user: User) -> bool:
        return user.is_admin
