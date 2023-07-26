from datetime import datetime
from keyboards.for_options import Option

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db.models import (
    AccMessage,
    Project,
    Type,
    Purpose
)


async def add_accmessage(session, project: str,
                         type: str, purpose: str,
                         create_time: datetime):
    new_accmes = AccMessage(project=project, type=type,
                            purpose=purpose, create_time=create_time)
    session.add(new_accmes)
    await session.commit()


async def get_option_values(session: AsyncSession, option_cls):
    result = await session.execute(select(option_cls))
    return result.scalars()


async def get_projects(session: AsyncSession):
    return await get_option_values(session, Project)


async def get_types(session: AsyncSession):
    return await get_option_values(session, Type)


async def get_purposes(session: AsyncSession):
    return await get_option_values(session, Purpose)


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
