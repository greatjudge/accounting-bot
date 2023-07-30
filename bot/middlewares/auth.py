from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from bot.db.requests import get_user


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            update: Update,
            data: Dict[str, Any]
    ) -> Any:
        user = await get_user(data['session'], update.event.from_user.id)
        if user is not None:
            data['user'] = user
            return await handler(update, data)
        else:
            await data['bot'].send_message(
                update.event.from_user.id,
                'У вас нет прав, обратитесь к администратору'
            )
