from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BIGINT
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    is_admin: Mapped[bool] = mapped_column(default=False)


class Project(Base):
    __tablename__ =  'projects'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class Type(Base):
    __tablename__ = 'types'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class Purpose(Base):
    __tablename__ = 'purposes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
