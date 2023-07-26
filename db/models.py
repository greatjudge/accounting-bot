from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime

from db.base import Base


class AccMessage(Base):
    __tablename__ = 'acc_messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project: Mapped[str]
    type: Mapped[str]
    purpose: Mapped[str]
    create_time: Mapped[datetime] = mapped_column(DateTime())

    def __repr__(self):
        return f'AccMessage({self.project}, {self.type}, {self.purpose}, {self.create_time})'


class Project(Base):
    __tablename__ = 'projects'

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
