from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from config_reader import config
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


def data_repr(data: dict, add_filename: bool = True) -> str:
    strings = []
    if add_filename and 'attached_file' in data:
        value = data['attached_file'][1]
        strings.append(f'файл: {value}')

    for key, name in (
            ('project', 'проект'),
            ('type', 'тип'),
            ('purpose', 'назначение')
    ):
        key_objs = key + 's'
        if key in data and key_objs in data:
            strings.append(f'{name}: {data[key_objs][data[key]]}')
    if 'comment' in data:
        strings.append(f'комментарий: {data["comment"]}')
    return '\n'.join(strings)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        'Прикрепите файл'
    )
    await state.set_state(AddMessage.attaching_file)


async def attached(message: Message, state: FSMContext, session: AsyncSession):
    projects = {p.id: p.name for p in await get_projects(session)}

    if not projects:
        await if_empty_list(message, 'проект')
        return

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


async def if_empty_list(event, name: str):
    if isinstance(event, CallbackQuery):
        event = event.message
    await event.answer(
        text=f'Список пуст, добавьте {name} с помощью команды /edit'
    )


@router.callback_query(AddMessage.choosing_project,
                       ItemsCallbackFactory.filter(F.name == 'projects'))
async def project_chosen(callback: CallbackQuery,
                         callback_data: ItemsCallbackFactory,
                         state: FSMContext,
                         session: AsyncSession):
    types = {p.id: p.name for p in await get_types(session)}

    if not types:
        await if_empty_list(callback, 'тип')
        return

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

    await state.set_state(AddMessage.choosing_type)


@router.callback_query(AddMessage.choosing_type,
                       ItemsCallbackFactory.filter(F.name == 'types'))
async def type_chosen(callback: CallbackQuery,
                      callback_data: ItemsCallbackFactory,
                      state: FSMContext,
                      session: AsyncSession):
    purposes = {p.id: p.name for p in await get_purposes(session)}

    if not purposes:
        await if_empty_list(callback, 'назначение')
        return

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
    await callback.answer()
    await logic_after_comment(callback.message, state)


@router.message(AddMessage.comment, F.text)
async def comment_written(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await logic_after_comment(message, state)


@router.callback_query(AddMessage.confirmation,
                       ConfirmCallbackFactory.filter(F.value == 'send'))
async def send(callback: CallbackQuery,
               callback_data: ConfirmCallbackFactory,
               state: FSMContext,
               bot: Bot):
    data = await state.get_data()

    await send_message2channel(bot, data)

    text = f'Вы отправили: \n{data_repr(data)}'
    await callback.message.edit_text(text)
    await callback.answer()
    await state.clear()


async def send_message2channel(bot: Bot, data):
    caption = data_repr(data, add_filename=False)
    if 'attached_file' in data:
        await bot.send_document(
            config.channel_id,
            data['attached_file'][0],
            caption=caption
        )
    elif 'attached_photo' in data:
        await bot.send_photo(
            config.channel_id,
            data['attached_photo'],
            caption=caption
        )
