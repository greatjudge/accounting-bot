from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config_reader import config
from bot.keyboards.for_messages import (
    get_keyboard_confirm,
    ConfirmCallbackFactory, get_comment_kb
)

from bot.keyboards.common_kb import (
    get_keyboard_fab,
    ItemsCallbackFactory
)

from bot.db.models import (
    Project,
    Type,
    Purpose
)

from bot.db.requests import (
    get_options
)


router = Router()


class AddMessage(StatesGroup):
    attaching_file = State()
    choosing_first = State()
    choosing_second = State()
    choosing_third = State()
    comment = State()
    confirmation = State()


def data_repr(data: dict, add_filename: bool = True) -> str:
    strings = []
    if add_filename and 'attached_file' in data:
        value = data['attached_file'][1]
        strings.append(f'файл: {value}')

    for cls in (Project, Type, Purpose):
        if cls.__name__ in data:
            strings.append(
                f'{cls.verbose_name}: {data[cls.__name__ + "s"][int(data[cls.__name__])]}'
            )
    if 'comment' in data:
        strings.append(f'комментарий: {data["comment"]}')
    return '\n'.join(strings)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        'Прикрепите файл'
    )
    await state.set_state(AddMessage.attaching_file)


async def if_empty_list(event, name: str):
    if isinstance(event, CallbackQuery):
        event = event.message
    await event.answer(
        text=f'Список пуст, добавьте {name} с помощью команды /edit'
    )


async def choose_option(
        event: Message | CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        opt_cls
):
    options = {opt.id: opt.name for opt in await get_options(session, opt_cls)}
    if not options:
        await if_empty_list(event, opt_cls.verbose_name)
        return
    data = await state.get_data()

    text = f'Выберите {opt_cls.verbose_name}:'
    data_text = data_repr(data)
    if data_text:
        text = f'Вы ввели: \n{data_text}\n' + text

    markup = get_keyboard_fab(
        ((uid, name) for uid, name in options.items()),
        opt_cls.__name__
    )

    await state.update_data({opt_cls.__name__ + 's': options})

    if isinstance(event, Message):
        await event.answer(text=text, reply_markup=markup)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text)
        await event.message.edit_reply_markup(reply_markup=markup)
        await event.answer()


async def attached(message: Message, state: FSMContext, session: AsyncSession):
    await choose_option(message, state, session, Project)
    await state.set_state(AddMessage.choosing_first)


@router.message(AddMessage.attaching_file, F.document)
async def file_attached(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(attached_file=(message.document.file_id,
                                           message.document.file_name))
    await attached(message, state, session)


@router.message(AddMessage.attaching_file, F.photo)
async def photo_attached(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(attached_photo=message.photo[-1].file_id)
    await attached(message, state, session)


@router.callback_query(AddMessage.choosing_first,
                       ItemsCallbackFactory.filter(F.name == Project.__name__))
async def first_chosen(
        callback: CallbackQuery,
        callback_data: ItemsCallbackFactory,
        state: FSMContext,
        session: AsyncSession
):
    await state.update_data({Project.__name__: callback_data.value})
    await choose_option(callback, state, session, Type)
    await state.set_state(AddMessage.choosing_second)


@router.callback_query(AddMessage.choosing_second,
                       ItemsCallbackFactory.filter(F.name == Type.__name__))
async def second_chosen(
        callback: CallbackQuery,
        callback_data: ItemsCallbackFactory,
        state: FSMContext,
        session: AsyncSession
):
    await state.update_data({Type.__name__: callback_data.value})
    await choose_option(callback, state, session, Purpose)
    await state.set_state(AddMessage.choosing_third)


@router.callback_query(
    AddMessage.choosing_third,
    ItemsCallbackFactory.filter(F.name == Purpose.__name__))
async def third_chosen(
        callback: CallbackQuery,
        callback_data: ItemsCallbackFactory,
        state: FSMContext
):
    await state.update_data({Purpose.__name__: callback_data.value})

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


@router.callback_query(AddMessage.confirmation,
                       ConfirmCallbackFactory.filter(F.value == 'send'))
async def send(callback: CallbackQuery,
               state: FSMContext,
               bot: Bot):
    data = await state.get_data()

    await send_message2channel(bot, data)

    text = f'Вы отправили: \n{data_repr(data)}'
    await callback.message.edit_text(text)
    await callback.answer()
    await state.clear()
