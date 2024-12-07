from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Integer

# Создание базового класса
class Base(DeclarativeBase):
    ...

# Создание таблицы преподавателей
class Teacher(Base):
    # Название таблицы
    __tablename__  = 'teacher'

    # Поля таблицы и их параметры
    teacherTelegram_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    teacherSurname:Mapped[str] = mapped_column(String(30), use_existing_column=False)
    teacherName:Mapped[str] = mapped_column(String(30), use_existing_column=False)
    teacherPatronymic:Mapped[str] = mapped_column(String(30))
    teacherPosition:Mapped[str] = mapped_column(String(30), use_existing_column=False)
    teacherPassword:Mapped[str] = mapped_column(String(64), use_existing_column=False)

class Lesson(Base):
    __tablename__ = 'lesson'

    lessonId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    teacherTelegram_id: Mapped[int] = mapped_column(Integer, ForeignKey('teacher.teacherTelegram_id'))
    lessonName: Mapped[str] = mapped_column(String(30), use_existing_column=False)
    lessonType: Mapped[str] = mapped_column(String(3), use_existing_column=False)
    group: Mapped[str] = mapped_column(String, use_existing_column=False)

class Student(Base):
    __tablename__ = 'student'

    studentTelegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    studentGroup: Mapped[str] = mapped_column(String, use_existing_column=False)
    studentSurname: Mapped[str] = mapped_column(String(30), use_existing_column=False)
    studentName: Mapped[str] = mapped_column(String(30), use_existing_column=False)
    studentPatronymic: Mapped[str] = mapped_column(String(30), use_existing_column=False)

class Gradebook(Base):
    __tablename__ = 'gradebook'

    gradebookId: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    lessonId: Mapped[int] = mapped_column(Integer, ForeignKey('lesson.lessonId'))
    studentTelegram_id: Mapped[int] = mapped_column(Integer, ForeignKey('student.studentTelegram_id'))
    gradebook5: Mapped[int] = mapped_column(Integer, use_existing_column=False)
    gradebook4: Mapped[int] = mapped_column(Integer, use_existing_column=False)
    gradebook3: Mapped[int] = mapped_column(Integer, use_existing_column=False)
    gradebook2: Mapped[int] = mapped_column(Integer, use_existing_column=False)
    gradebookVisits: Mapped[int] = mapped_column(Integer, use_existing_column=False)

class Admin(Base):
    __tablename__ = 'admin'
    adminTelegram_id: Mapped[int] = mapped_column(Integer,primary_key=True,use_existing_column=False)
    adminPassword: Mapped[str] = mapped_column(String(64), use_existing_column=False)
