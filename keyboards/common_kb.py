from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton


CANCEL_BUTTON = InlineKeyboardButton(text='Отменить',
                                     callback_data='cancel')
