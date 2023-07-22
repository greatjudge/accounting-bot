from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData

from keyboards.common_kb import CANCEL_BUTTON
from typing import Optional


available_projects = ["первый", "тва", "тари", "фо"]
available_types = ['type', 'тип', "tipo", "тып"]
available_purposes = ['cola', 'pepsi', 'mango', 'сто']


class ItemsCallbackFactory(CallbackData, prefix='item'):
    name: str
    value: str


class ConfirmCallbackFactory(CallbackData, prefix='confirm'):
    value: str


class BackCallbackFactory(CallbackData, prefix='back'):
    value: str


def get_keyboard_fab(items: list[str],
                     name: str,
                     prev_state: Optional[str] = None):
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(
            text=item,
            callback_data=ItemsCallbackFactory(name=name, value=item)
        )

    if prev_state is not None:
        builder.button(
            text='Назад',
            callback_data=BackCallbackFactory(value=prev_state)
        )

    builder.add(CANCEL_BUTTON)
    builder.adjust(1)
    return builder.as_markup()


def get_keyboard_confirm(prev_state: Optional[str] = None):
    builder = InlineKeyboardBuilder()
    builder.add(CANCEL_BUTTON)
    builder.button(
        text='Отправить',
        callback_data=ConfirmCallbackFactory(value='send')
    )

    if prev_state is not None:
        builder.button(
            text='Назад',
            callback_data=BackCallbackFactory(value=prev_state)
        )

    builder.adjust(2)
    return builder.as_markup()
