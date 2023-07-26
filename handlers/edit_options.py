from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup

from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.for_options import get_options_kb, Option, Action, get_actions_kb
from keyboards.common_kb import get_keyboard_fab, ItemsCallbackFactory

from db.requests import (
    add_option,
    get_option_values,
    delete_option
)

router = Router()


class EditOption(StatesGroup):
    choose_option = State()
    choose_action = State()
    adding = State()
    removing = State()


@router.message(Command("edit"))
async def cmd_edit(message: Message, state: FSMContext):
    await message.answer(
        text='Выберите, что редактировать',
        reply_markup=get_options_kb()
    )
    await state.set_state(EditOption.choose_option)


@router.message(EditOption.choose_option, F.text.in_(Option.values()), F.text.as_('option'))
async def option_choosed(message: Message, option: str, state: FSMContext):
    await state.update_data(option=option)
    await message.answer(
        text='Выберите действие',
        reply_markup=get_actions_kb()
    )
    await state.set_state(EditOption.choose_action)


@router.message(EditOption.choose_action, F.text == Action.add.value)
async def add_choosed(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        text=f'Введите {data["option"]}',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EditOption.adding)


@router.message(EditOption.adding, F.text)
async def add_option_value(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await add_option(session,
                     Option.option2storage()[data['option']],
                     message.text)
    await message.answer(
        text=f'Cохранено {data["option"]} {message.text}'
    )
    await state.clear()


@router.message(EditOption.choose_action, F.text == Action.remove.value)
async def remove_chosen(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    option_cls = Option.option2storage()[data['option']]
    option_values = await get_option_values(session, option_cls)
    option_id_name = {opt.id: opt.name for opt in option_values}
    await state.update_data(option_id_name=option_id_name)

    await message.answer(
        text='Выберите, что удалить: ',
        reply_markup=get_keyboard_fab(option_id_name.items(),
                                      data['option'], add_cancel=False)
    )
    await state.set_state(EditOption.removing)


@router.callback_query(EditOption.removing, ItemsCallbackFactory.filter())
async def remove_option(callback: CallbackQuery,
                        callback_data: ItemsCallbackFactory,
                        state: FSMContext,
                        session: AsyncSession):
    data = await state.get_data()

    await delete_option(session,
                        Option.option2storage()[data['option']],
                        callback_data.value)

    await callback.message.edit_text(
        text=f'Вы удалили {callback_data.name} {data["option_id_name"][callback_data.value]}'
    )
    await state.clear()
