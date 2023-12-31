from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.telethon_app.forward import forward_mes_for_month

from datetime import timedelta


router = Router()


@router.message(Command('upload_current'))
async def cmd_upload(message: Message):
    await message.answer(
        text='Выгрузка началась'
    )
    await forward_mes_for_month(
        message.from_user.id,
        message.date,
        'за текущий месяц'
    )
    await message.answer(
        text='Выгрузка завершилась'
    )


@router.message(Command('upload_prev'))
async def cmd_upload(message: Message):
    date = message.date.replace(day=1) - timedelta(days=1)
    await message.answer(
        text='Выгрузка началась'
    )
    await forward_mes_for_month(
        message.from_user.id,
        date,
        'за предыдущий месяц'
    )
    await message.answer(
        text='Выгрузка завершилась'
    )
