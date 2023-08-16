from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup

from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.for_options import (
    OPTION2CLS,
    Action,
    get_options_kb,
    get_actions_kb,
    get_confirm_kb
)


from bot.keyboards.common_kb import get_keyboard_fab, ItemsCallbackFactory

from bot.db.requests import (
    add_option,
    get_options,
    delete_option
)

router = Router()


class EditOption(StatesGroup):
    choose_option = State()
    choose_action = State()

    typing_opt_value = State()
    choose_opt_value = State()

    confirmation = State()
    adding = State()
    removing = State()


@router.message(Command("edit"))
async def cmd_edit(message: Message, state: FSMContext):
    await message.answer(
        text='Выберите, что редактировать',
        reply_markup=get_options_kb()
    )
    await state.set_state(EditOption.choose_option)


@router.message(EditOption.choose_option, F.text.in_(OPTION2CLS), F.text.as_('option'))
async def option_choosed(message: Message, option: str, state: FSMContext):
    await state.update_data(option=option)
    await message.answer(
        text='Выберите действие',
        reply_markup=get_actions_kb()
    )
    await state.set_state(EditOption.choose_action)


@router.message(EditOption.choose_action, F.text == Action.add.value)
async def add_choosed(message: Message, state: FSMContext):
    await state.update_data(action=Action.add.value)
    data = await state.get_data()
    await state.set_state(EditOption.typing_opt_value)
    await message.answer(
        text=f'Введите {data["option"]}',
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(EditOption.typing_opt_value, F.text)
async def opt_value_added(message: Message, state: FSMContext):
    await state.update_data(option_value=message.text)
    data = await state.get_data()
    await message.answer(
        text=f'Хотите добавить {data["option"]} {message.text}?',
        reply_markup=get_confirm_kb()
    )
    await state.set_state(EditOption.confirmation)


@router.message(EditOption.choose_action, F.text == Action.remove.value)
async def remove_chosen(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(action=Action.remove.value)
    data = await state.get_data()

    option_cls = OPTION2CLS[data['option']]
    option_values = await get_options(session, option_cls)

    option_id_name = {opt.id: opt.name for opt in option_values}

    if not option_id_name:
        await message.answer(
            text='Нечего удалять',
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return

    await state.update_data(option_id_name=option_id_name)

    await message.answer(
        text='Выберите, что удалить: ',
        reply_markup=get_keyboard_fab(option_id_name.items(),
                                      data['option'], add_cancel=False)
    )
    await state.set_state(EditOption.choose_opt_value)


@router.callback_query(EditOption.choose_opt_value, ItemsCallbackFactory.filter())
async def option_val_chosen(
    callback: CallbackQuery,
    callback_data: ItemsCallbackFactory,
    state: FSMContext,
):
    data = await state.get_data()
    option_value = (
        callback_data.value,
        data['option_id_name'][callback_data.value]
    )
    await state.update_data(option_value=option_value)

    await callback.message.answer(
        f'Вы действительно хотите удалить {data["option"]} {option_value[1]}?',
        reply_markup=get_confirm_kb()
    )
    await state.set_state(EditOption.confirmation)


@router.message(EditOption.confirmation, F.text == 'да')
async def confirm(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if data['action'] == Action.add.value:
        await add_option_value(message, state, session)
    elif data['action'] == Action.remove.value:
        await remove_option(message, state, session)
    await state.clear()


async def add_option_value(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await add_option(session,
                     OPTION2CLS[data['option']],
                     data["option_value"])
    await message.answer(
        text=f'Cохранено {data["option"]} {data["option_value"]}',
        reply_markup=ReplyKeyboardRemove()
    )


async def remove_option(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()

    await delete_option(
        session,
        OPTION2CLS[data['option']],
        int(data['option_value'][0])
    )

    await message.answer(
        text=f'Вы удалили {data["option"]} {data["option_value"][1]}',
        reply_markup=ReplyKeyboardRemove()
    )
