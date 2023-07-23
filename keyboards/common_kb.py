from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from typing import Optional


CANCEL_BUTTON = InlineKeyboardButton(text='Отменить',
                                     callback_data='cancel')


class ItemsCallbackFactory(CallbackData, prefix='item'):
    name: str
    value: str


def get_keyboard_fab(items: list[str],
                     name: str,
                     add_cancel: bool = True):
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(
            text=item,
            callback_data=ItemsCallbackFactory(name=name, value=item)
        )

    if add_cancel:
        builder.add(CANCEL_BUTTON)
    builder.adjust(1)
    return builder.as_markup()
