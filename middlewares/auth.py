from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from db.requests import get_user


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            update: Update,
            data: Dict[str, Any]
    ) -> Any:
        print('DIR', dir(update.event))
        user = await get_user(data['session'], update.event.from_user.id)
        if user is not None:
            data['user'] = user
            return await handler(update, data)
