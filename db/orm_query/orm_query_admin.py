from sqlalchemy.ext.asyncio import AsyncSession
from db.models.admin import Admin
from db.models.teacher import Teacher
from db.models.gradebook import Gradebook
from db.models.student import Student
from db.models.lesson import Lesson
from sqlalchemy import select, update
import pandas as pd
from loguru import logger
import sys
import os

logger.remove()
logger.add(sys.stderr, level="DEBUG")


#  Добавление админа в БД
async def orm_add_admin(session: AsyncSession, data: dict):
    # Создание админа
    admin = Admin(
        adminTelegram_id=data['id'],
        adminPassword=data['password']
    )

    # Добавление админа в таблицу
    session.add(admin)
    await session.commit()


# Получение данных об администраторе
async def orm_get_admin(session: AsyncSession, tg_id: int):
    query = select(Admin).where(Admin.adminTelegram_id == tg_id)
    result = await session.execute(query)
    return result.scalar()


# Выгрузка по таблице студентов
async def orm_get_table_student(session: AsyncSession):
    # Выполняем запрос для получения всех записей
    query = select(Student)
    result = await session.execute(query)
    student = result.scalars().all()  # Извлекаем объекты ORM

    # Преобразуем данные в список словарей
    data = [
        {
            'studentTelegram_id': stud.studentTelegram_id,
            'studentGroup': stud.studentGroup,
            'studentSurname': stud.studentSurname,
            'studentName': stud.studentName,
            'studentPatronymic': stud.studentPatronymic
        }
        for stud in student
    ]

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в Excel
    df.to_excel("table_student.xlsx", index=False)


# Выгрузка по таблице предметов
async def orm_get_table_lesson(session: AsyncSession):
    # Выполняем запрос для получения всех записей
    query = select(Lesson)
    result = await session.execute(query)
    lessons = result.scalars().all()  # Извлекаем объекты ORM

    # Преобразуем данные в список словарей
    data = [
        {
            "lessonId": lesson.lessonId,
            "teacherTelegram_id": lesson.teacherTelegram_id,
            "lessonName": lesson.lessonName,
            "lessonType": lesson.lessonType,
            "group": lesson.group
        }
        for lesson in lessons
    ]

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в Excel
    df.to_excel("table_lessons.xlsx", index=False)


# Выгрузка по таблице преподавателей
async def orm_get_table_teacher(session: AsyncSession):
    # Выполняем запрос для получения всех записей
    query = select(Teacher)
    result = await session.execute(query)
    teachers = result.scalars().all()  # Извлекаем объекты ORM

    # Преобразуем данные в список словарей
    data = [
        {
            'teacherTelegram_id': teacher.teacherTelegram_id,
            'teacherSurname': teacher.teacherSurname,
            'teacherName': teacher.teacherName,
            'teacherPatronymic': teacher.teacherPatronymic,
            'teacherPosition': teacher.teacherPosition,
            'teacherPassword': teacher.teacherPassword}

        for teacher in teachers
    ]

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в Excel
    df.to_excel("table_teacher.xlsx", index=False)


# Выгрузка по таблице журнала
async def orm_get_table_gradebook(session: AsyncSession):
    # Выполняем запрос для получения всех записей
    query = select(Gradebook)
    result = await session.execute(query)
    gradebook_all_items = result.scalars().all()  # Извлекаем объекты ORM
    # Преобразуем данные в список словарей
    data = [
        {
            'gradebookId': gradebook.gradebookId,
            'lessonId': gradebook.lessonId,
            'studentTelegram_id': gradebook.studentTelegram_id,
            'gradebook5': gradebook.gradebook5,
            'gradebook4': gradebook.gradebook4,
            'gradebook3': gradebook.gradebook3,
            'gradebook2': gradebook.gradebook2,
            'gradebookVisits': gradebook.gradebookVisits
        }

        for gradebook in gradebook_all_items
    ]

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в Excel
    df.to_excel("table_gradebook.xlsx", index=False)


# Загрузка данных в таблицу студентов из полученного файла
async def orm_load_table_students(session: AsyncSession, path: str):
    try:
        # Читаем файл с помощью менеджера контекста
        with pd.ExcelFile(path) as xlsx:
            sheet1_df = xlsx.parse('Sheet1')

        for row in sheet1_df.itertuples():
            query = select(Student).where(Student.studentTelegram_id == row.studentTelegram_id)
            result = await session.execute(query)
            existing_student = result.scalar()

            if existing_student:
                update_query = (
                    update(Student)
                    .where(Student.studentTelegram_id == row.studentTelegram_id)
                    .values(
                        studentGroup=row.studentGroup,
                        studentSurname=row.studentSurname,
                        studentName=row.studentName,
                        studentPatronymic=row.studentPatronymic
                    )
                )
                await session.execute(update_query)
            else:
                new_student = Student(
                    studentTelegram_id=row.studentTelegram_id,
                    studentGroup=row.studentGroup,
                    studentSurname=row.studentSurname,
                    studentName=row.studentName,
                    studentPatronymic=row.studentPatronymic
                )
                session.add(new_student)

        await session.commit()
    except Exception as e:
        print(f"Error processing file: {e}")
        await session.rollback()
    finally:
        # Удаляем файл
        if os.path.exists(path):
            os.remove(path)


# Загрузка данных в таблицу предметов из полученного файла
async def orm_load_table_lesson(session: AsyncSession, path: str):
    try:
        # Читаем файл с помощью менеджера контекста
        with pd.ExcelFile(path) as xlsx:
            sheet1_df = xlsx.parse('Sheet1')

        for row in sheet1_df.itertuples():
            query = select(Lesson).where(Lesson.lessonId == row.lessonId)
            result = await session.execute(query)
            existing_lesson = result.scalar()

            if existing_lesson:
                update_query = (
                    update(Lesson)
                    .where(Lesson.lessonId == row.lessonId)
                    .values(
                        teacherTelegram_id=row.teacherTelegram_id,
                        lessonName=row.lessonName,
                        lessonType=row.lessonType,
                        group=row.group
                    )
                )
                await session.execute(update_query)
            else:
                new_lesson = Lesson(
                    lessonId=row.lessonId,
                    teacherTelegram_id=row.teacherTelegram_id,
                    lessonName=row.lessonName,
                    lessonType=row.lessonType,
                    group=row.group,
                )
                session.add(new_lesson)

        await session.commit()
    except Exception as e:
        print(f"Error processing file: {e}")
        await session.rollback()
    finally:
        # Удаляем файл
        if os.path.exists(path):
            os.remove(path)


# Загрузка данных в таблицу преподавателей из полученного файла
async def orm_load_table_teacher(session: AsyncSession, path: str):
    try:
        # Читаем файл с помощью менеджера контекста
        with pd.ExcelFile(path) as xlsx:
            sheet1_df = xlsx.parse('Sheet1')

        for row in sheet1_df.itertuples():
            query = select(Teacher).where(Teacher.teacherTelegram_id == row.teacherTelegram_id)
            result = await session.execute(query)
            existing_teacher = result.scalar()

            if existing_teacher:
                update_query = (
                    update(Teacher)
                    .where(Teacher.teacherTelegram_id == row.teacherTelegram_id)
                    .values(
                        teacherSurname=row.teacherSurname,
                        teacherName=row.teacherName,
                        teacherPatronymic=row.teacherPatronymic,
                        teacherPosition=row.teacherPosition,
                        teacherPassword=row.teacherPassword
                    )
                )
                await session.execute(update_query)
            else:
                new_teacher = Teacher(
                    teacherTelegram_id=row.teacherTelegram_id,
                    teacherSurname=row.teacherSurname,
                    teacherName=row.teacherName,
                    teacherPatronymic=row.teacherPatronymic,
                    teacherPosition=row.teacherPosition,
                    teacherPassword=row.teacherPassword
                )
                session.add(new_teacher)

        await session.commit()
    except Exception as e:
        print(f"Error processing file: {e}")
        await session.rollback()
    finally:
        # Удаляем файл
        if os.path.exists(path):
            os.remove(path)


# Загрузка данных в таблицу журнала из полученного файла
async def orm_load_table_gradebook(session: AsyncSession, path: str):
    try:
        # Читаем файл с помощью менеджера контекста
        with pd.ExcelFile(path) as xlsx:
            sheet1_df = xlsx.parse('Sheet1')

        for row in sheet1_df.itertuples():
            query = select(Gradebook).where(Gradebook.gradebookId == row.gradebookId)
            result = await session.execute(query)
            existing_gradebook = result.scalar()

            if existing_gradebook:
                update_query = (
                    update(Gradebook)
                    .where(Gradebook.gradebookId == row.gradebookId)
                    .values(
                        lessonId=row.lessonId,
                        studentTelegram_id=row.studentTelegram_id,
                        gradebook5=row.gradebook5,
                        gradebook4=row.gradebook4,
                        gradebook3=row.gradebook3,
                        gradebook2=row.gradebook2,
                        gradebookVisits=row.gradebookVisits
                    )
                )
                await session.execute(update_query)
            else:
                new_gradebook = Gradebook(
                    gradebookId=row.gradebookId,
                    lessonId=row.lessonId,
                    studentTelegram_id=row.studentTelegram_id,
                    gradebook5=row.gradebook5,
                    gradebook4=row.gradebook4,
                    gradebook3=row.gradebook3,
                    gradebook2=row.gradebook2,
                    gradebookVisits=row.gradebookVisits
                )
                session.add(new_gradebook)

        await session.commit()
    except Exception as e:
        print(f"Error processing file: {e}")
        await session.rollback()
    finally:
        # Удаляем файл
        if os.path.exists(path):
            os.remove(path)

