from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData
from enum import Enum


available_projects = ["первый", "тва", "тари", "фо"]
available_types = ['type', 'тип', "tipo", "тып"]
available_purposes = ['cola', 'pepsi', 'mango', 'сто']


class Option(Enum):
    project = 'проект'
    type = 'тип'
    purpose = 'назначение'

    @classmethod
    def option2storage(cls):
        return {
            cls.project.value: available_projects,
            cls.type.value: available_types,
            cls.purpose.value: available_types
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
