from enum import Enum
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.db.models import (
    Project, Type, Purpose
)


OPTION2CLS = {
    Project.verbose_name: Project,
    Type.verbose_name: Type,
    Purpose.verbose_name: Purpose
}


def get_options_kb():
    kb = [[KeyboardButton(text=name)] for name in OPTION2CLS]
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
