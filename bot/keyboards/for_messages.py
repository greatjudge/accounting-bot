from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData

from bot.keyboards.common_kb import CANCEL_BUTTON
from typing import Optional


class ConfirmCallbackFactory(CallbackData, prefix='confirm'):
    value: str


class BackCallbackFactory(CallbackData, prefix='back'):
    value: str


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


def get_comment_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Без комментария',
        callback_data='no_comment'
    )
    return builder.as_markup()