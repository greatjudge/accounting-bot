from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.for_messages import (
    get_keyboard_confirm,
    ConfirmCallbackFactory, get_comment_kb
)

from keyboards.common_kb import (
    get_keyboard_fab,
    ItemsCallbackFactory
)

from db.requests import (
    get_projects,
    get_types,
    get_purposes
)


router = Router()


class AddMessage(StatesGroup):
    attaching_file = State()
    choosing_project = State()
    choosing_type = State()
    choosing_purpose = State()
    comment = State()
    confirmation = State()


def data_repr(data: dict) -> str:
    strings = []
    if 'attached_file' in data:
        value = data['attached_file'][1]
        strings.append(f' attached_file: {value}')
    for key in ('project', 'type', 'purpose'):
        key_objs = key + 's'
        if key in data and key_objs in data:
            strings.append(f' {key}: {data[key_objs][data[key]]}')
    return '\n'.join(strings)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        'Прикрепите файл'
    )
    await state.set_state(AddMessage.attaching_file)


async def attached(message: Message, state: FSMContext, session: AsyncSession):
    projects = {p.id: p.name for p in await get_projects(session)}
    await state.update_data(projects=projects)

    await message.answer(
        text='Выберите проект:',
        reply_markup=get_keyboard_fab(
            ((uid, name) for uid, name in projects.items()),
            'projects'
        )
    )
    await state.set_state(AddMessage.choosing_project)


@router.message(AddMessage.attaching_file, F.document)
async def file_attached(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(attached_file=(message.document.file_id,
                                           message.document.file_name))
    await attached(message, state, session)


@router.message(AddMessage.attaching_file, F.photo)
async def photo_attached(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(attached_photo=message.photo[-1].file_id)
    await attached(message, state, session)


@router.callback_query(AddMessage.choosing_project,
                       ItemsCallbackFactory.filter(F.name == 'projects'))
async def project_chosen(callback: CallbackQuery,
                         callback_data: ItemsCallbackFactory,
                         state: FSMContext,
                         session: AsyncSession):
    types = {p.id: p.name for p in await get_types(session)}
    await state.update_data(project=callback_data.value, types=types)

    data = await state.get_data()
    text = f'Вы ввели: \n{data_repr(data)}\n' + 'Выберите тип:'
    await callback.message.edit_text(text)

    await callback.message.edit_reply_markup(
        reply_markup=get_keyboard_fab(
            ((uid, name) for uid, name in types.items()),
            'types'
        )
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
                      state: FSMContext,
                      session: AsyncSession):
    purposes = {p.id: p.name for p in await get_purposes(session)}
    await state.update_data(type=callback_data.value, purposes=purposes)

    data = await state.get_data()
    text = f'Вы ввели: \n{data_repr(data)}\n' + 'Выберите назначение:'
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(
        reply_markup=get_keyboard_fab(
            ((uid, name) for uid, name in purposes.items()),
            'purposes'
        )
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
    text = f'Вы ввели: \n{data_repr(data)}\n' + 'Введите комментарий:'
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(reply_markup=get_comment_kb())

    # text = f'Вы ввели \nфайл: {data["attached_file"].file_name}\nпроект: {data["project"]}' \
    #        + f'\nтип: {data["type"]}\nназначение: {data["purpose"]}'
    # await callback.message.answer(
    #     text=text,
    #     reply_markup=get_keyboard_confirm()
    # )

    await callback.answer()
    await state.set_state(AddMessage.comment)


async def logic_after_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    text = f'Вы ввели: \n{data_repr(data)}'
    await message.answer(
        text=text,
        reply_markup=get_keyboard_confirm()
    )
    await state.set_state(AddMessage.confirmation)


@router.callback_query(AddMessage.comment, F.data == 'no_comment')
async def no_comment_callback(callback: CallbackQuery,
                              state: FSMContext):
    await logic_after_comment(callback.message, state)


@router.message(AddMessage.comment, F.text)
async def comment_written(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await logic_after_comment(message, state)


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
