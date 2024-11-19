from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String

# Создание базового класса
class Base(DeclarativeBase):
    ...

# Создание таблицы преподавателей
class Teacher(Base):
    # Название таблицы
    __tablename__  = 'teacher'

    # Поля таблицы и их параметры
    teacherTelegram_id:Mapped[int] = mapped_column(primary_key=True)
    teacherSurname:Mapped[str] = mapped_column(String(30), use_existing_column=False)
    teacherName:Mapped[str] = mapped_column(String(30), use_existing_column=False)
    teacherPatronymic:Mapped[str] = mapped_column(String(30))
    teacherPosition:Mapped[str] = mapped_column(String(30), use_existing_column=False)
    teacherPassword:Mapped[str] = mapped_column(String(64), use_existing_column=False)