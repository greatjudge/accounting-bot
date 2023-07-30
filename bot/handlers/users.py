from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types.message import Message

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.requests import get_user, add_user

from bot.filters.permissions import IsAdmin


router = Router()


class AddUser(StatesGroup):
    typing_id = State()


class RemoveUser(StatesGroup):
    typing_id = State()


class AddAdmin(StatesGroup):
    typing_id = State()


@router.message(Command('add_user'), IsAdmin())
async def cmd_add_user(message: Message, state: FSMContext):
    await state.set_state(AddUser.typing_id)
    await message.answer(
        text='Введите id пользователя'
    )


@router.message(F.text, AddUser.typing_id)
async def adding_user(message: Message, state: FSMContext, session: AsyncSession):
    try:
        uid = int(message.text)
        await add_user(session, uid)
    except ValueError:
        await message.answer(
            text='id должен быть целым числом'
        )
    else:
        await message.answer(
            text=f'пользователь с id {uid} успешно добавлен'
        )
        await state.clear()


@router.message(Command('remove_user'), IsAdmin())
async def cmd_remove_user(message: Message, state: FSMContext, session: AsyncSession):
    await state.set_state(RemoveUser.typing_id)
    await message.answer(
        text='Введите id добавленного пользователя, которого хотите удалить'
    )


@router.message(F.text, RemoveUser.typing_id)
async def removing_user(message: Message, state: FSMContext, session: AsyncSession):
    try:
        uid = int(message.text)
        user = await get_user(session, uid)
        if user is None:
            text = 'Такого пользователя нет'
        else:
            print(user.id, user.is_admin)
            await session.delete(user)
            await session.commit()
            text = f'пользователь с id {uid} успешно удален'
        await message.answer(text=text)
    except ValueError:
        await message.answer(text='id должен быть целым числом')
    else:
        await state.clear()


@router.message(Command('add_admin'), IsAdmin())
async def cmd_add_admin(message: Message, state: FSMContext):
    await state.set_state(AddAdmin.typing_id)
    await message.answer(
        text='Введите id добавленного пользователя, которому хотите дать права администратора'
    )


@router.message(F.text, AddAdmin.typing_id)
async def adding_admin(message: Message, state: FSMContext, session: AsyncSession):
    try:
        uid = int(message.text)
        user = await get_user(session, uid)
        if user is None:
            text = f'такого пользователя не существует'
        elif user.is_admin:
            text = f'пользователь уже является админом'
        else:
            user.is_admin = True
            await session.commit()
            text = f'пользователь с id {uid} успешно получил права администратора'
        await message.answer(text=text)
    except ValueError:
        await message.answer(text='id должен быть целым числом')
    else:
        await state.clear()

