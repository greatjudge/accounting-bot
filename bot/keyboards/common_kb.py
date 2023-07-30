from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from typing import Iterable


CANCEL_BUTTON = InlineKeyboardButton(text='Отменить',
                                     callback_data='cancel')


class ItemsCallbackFactory(CallbackData, prefix='item'):
    name: str
    value: int | str


def get_keyboard_fab(items: Iterable[tuple[int, str]],
                     name: str,
                     add_cancel: bool = True,
                     value_text: bool = False):
    builder = InlineKeyboardBuilder()
    for uid, text in items:
        value = text if value_text else uid
        builder.button(
            text=text,
            callback_data=ItemsCallbackFactory(name=name, value=value)
        )

    if add_cancel:
        builder.add(CANCEL_BUTTON)
    builder.adjust(1)
    return builder.as_markup()
