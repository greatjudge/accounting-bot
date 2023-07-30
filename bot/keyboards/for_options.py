from enum import Enum
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from db.models import (
    Project, Type, Purpose
)


class Option(Enum):
    project = 'проект'
    type = 'тип'
    purpose = 'назначение'

    @classmethod
    def option2storage(cls):
        return {
            cls.project.value: Project,
            cls.type.value: Type,
            cls.purpose.value: Purpose
        }

    @classmethod
    def values(cls):
        return {item.value for item in cls}


def get_options_kb():
    kb = [[KeyboardButton(text=item.value)] for item in Option]
    return ReplyKeyboardMarkup(
        keyboard=kb
    )


class Action(Enum):
    add = 'добавить'
    remove = 'удалить'

    @classmethod
    def values(cls):
        return {item.value for item in cls}


def get_actions_kb():
    kb = [[KeyboardButton(text=item.value)] for item in Action]
    return ReplyKeyboardMarkup(
        keyboard=kb
    )


def get_confirm_kb():
    kb = [
        [KeyboardButton(text='да')],
        [KeyboardButton(text='отменить')]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb
    )
