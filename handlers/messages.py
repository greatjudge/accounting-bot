from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.for_messages import (
    get_keyboard_fab, available_projects,
    ItemsCallbackFactory, available_purposes,
    get_keyboard_confirm, available_types,
    ConfirmCallbackFactory
)


router = Router()


class AddMessage(StatesGroup):
    attaching_file = State()
    choosing_project = State()
    choosing_type = State()
    choosing_purpose = State()
    confirmation = State()


def data_repr(data: dict) -> str:
    strings = []
    for key, value in data.items():
        if key == 'attached_file':
            value = value.file_name
        if key == 'attached_photo':
            continue
        strings.append(f' {key}: {value}')
    return '\n'.join(strings)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        'Прикрепите файл'
    )
    await state.set_state(AddMessage.attaching_file)
    # print(type(await state.get_state()))


async def attached(message: Message, state: FSMContext):
    await message.answer(
        text='Выберите проект:',
        reply_markup=get_keyboard_fab(available_projects, 'projects')
    )
    await state.set_state(AddMessage.choosing_project)


@router.message(AddMessage.attaching_file, F.document)
async def file_attached(message: Message, state: FSMContext):
    await state.update_data(attached_file=message.document)
    await attached(message, state)


@router.message(AddMessage.attaching_file, F.photo)
async def file_attached(message: Message, state: FSMContext):
    await state.update_data(attached_photo=message.photo[-1])
    await attached(message, state)


@router.callback_query(AddMessage.choosing_project,
                       ItemsCallbackFactory.filter(F.name == 'projects'))
async def project_chosen(callback: CallbackQuery,
                         callback_data: ItemsCallbackFactory,
                         state: FSMContext):
    await state.update_data(project=callback_data.value)
    data = await state.get_data()
    # print(type(data))

    text = f'Вы ввели: \n{data_repr(data)}\n' + 'Выберите тип:'
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(
        reply_markup=get_keyboard_fab(available_types, 'types')
    )
    # await callback.message.answer(
    #     text='Выберите тип:',
    #     reply_markup=get_keyboard_fab(available_types, 'types')
    # )
    await state.set_state(AddMessage.choosing_type)


@router.callback_query(AddMessage.choosing_type,
                       ItemsCallbackFactory.filter(F.name == 'types'))
async def type_chosen(callback: CallbackQuery,
                      callback_data: ItemsCallbackFactory,
                      state: FSMContext):
    await state.update_data(type=callback_data.value)

    data = await state.get_data()
    text = f'Вы ввели: \n{data_repr(data)}\n' + 'Выберите назначение:'
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(
        reply_markup=get_keyboard_fab(available_purposes, 'purposes')
    )
    # await callback.message.answer(
    #     text='Выберите назначение:',
    #     reply_markup=get_keyboard_fab(available_purposes, 'purposes')
    # )
    await callback.answer()
    await state.set_state(AddMessage.choosing_purpose)


@router.callback_query(AddMessage.choosing_purpose,
                       ItemsCallbackFactory.filter(F.name == 'purposes'))
async def purpose_chosen(callback: CallbackQuery,
                         callback_data: ItemsCallbackFactory,
                         state: FSMContext):
    await state.update_data(purpose=callback_data.value)

    data = await state.get_data()
    text = f'Вы ввели: \n{data_repr(data)}'
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(
        reply_markup=get_keyboard_confirm()
    )

    # text = f'Вы ввели \nфайл: {data["attached_file"].file_name}\nпроект: {data["project"]}' \
    #        + f'\nтип: {data["type"]}\nназначение: {data["purpose"]}'
    # await callback.message.answer(
    #     text=text,
    #     reply_markup=get_keyboard_confirm()
    # )

    await callback.answer()
    await state.set_state(AddMessage.confirmation)


@router.callback_query(AddMessage.confirmation,
                       ConfirmCallbackFactory.filter(F.value == 'send'))
async def send(callback: CallbackQuery,
               callback_data: ConfirmCallbackFactory,
               state: FSMContext):
    data = await state.get_data()

    text = f'Вы отправили: \n{data_repr(data)}'
    await callback.message.edit_text(text)
    # await callback.message.edit_reply_markup(
    #     reply_markup=None
    # )
    # text = f'Вы отправили \nфайл: {data["attached_file"].file_name}\nпроект: {data["project"]}' \
    #        + f'\nтип: {data["type"]}\nназначение: {data["purpose"]}'
    # await callback.message.answer(text=text)
    await callback.answer()
    await state.clear()
