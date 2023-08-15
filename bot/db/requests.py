from bot.keyboards.for_options import Option

from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from bot.db.models import (
    User,
    Project,
    Type,
    Purpose
)


async def add_admins(session, usr_ids: list[int]):
    for uid in usr_ids:
        try:
            await add_user(session, uid, is_admin=True)
        except IntegrityError:
            pass


async def add_user(
        session: AsyncSession,
        uid: int,
        is_admin: bool = False
):
    usr = User(id=uid, is_admin=is_admin)
    session.add(usr)
    await session.commit()


async def get_user(session: AsyncSession,
                   uid: int) -> User:
    result = await session.execute(select(User).where(User.id == uid))
    return result.scalar()


async def user_in_db(session: AsyncSession,
                     uid: int) -> bool:
    result = await session.execute(select(User).where(User.id == uid))
    return bool(result.scalars())


async def user_list(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars()


async def get_options(session: AsyncSession, option_cls):
    result = await session.execute(select(option_cls))
    return result.scalars()


async def get_projects(session: AsyncSession):
    return await get_options(session, Project)


async def get_types(session: AsyncSession):
    return await get_options(session, Type)


async def get_purposes(session: AsyncSession):
    return await get_options(session, Purpose)


async def add_option(session, option_cls, name: str):
    new_opt = option_cls(name=name)
    session.add(new_opt)
    await session.commit()


async def delete_option(session, option_cls, id: int):
    await session.execute(delete(option_cls).where(option_cls.id == id))
    await session.commit()


async def add_project(session, name: str):
    await add_option(session, Project, name)


async def add_type(session, name: str):
    await add_option(session, Type, name)


async def add_purpose(session, name: str):
    await add_option(session, Purpose, name)


async def save_option_value(option: str, value: str):
    Option.option2storage()[option].append(value)


async def remove_option_value(option: str, value: str):
    Option.option2storage()[option].remove(value)
