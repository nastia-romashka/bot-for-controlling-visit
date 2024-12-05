from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Teacher, Lesson, Student, Gradebook, Admin
from sqlalchemy import select
from parser import Lessons
import pandas as pd
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG")



async def orm_add_teacher(session: AsyncSession, data: dict):
    # Создание преподавателя
    teach = Teacher(
        teacherTelegram_id=data['id'],
        teacherSurname=data['name_and_post'][0],
        teacherName=data['name_and_post'][1],
        teacherPatronymic=data['name_and_post'][2],
        teacherPosition=data['name_and_post'][3],
        teacherPassword=data['password']
    )

    # Добавление преподавателя в таблицу
    session.add(teach)
    await session.commit()

async def orm_get_teacher(session: AsyncSession, tg_id: int):
    query = select(Teacher).where(Teacher.teacherTelegram_id == tg_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_add_lesson(session: AsyncSession, data: dict, lesson: Lessons):
    # Создание занятия
    les = Lesson(
        teacherTelegram_id=data['id'],
        lessonName=lesson[2],
        lessonType=lesson[1],
        group=lesson[0]
    )
    session.add(les)
    await session.commit()

async def orm_add_student(session: AsyncSession, data: dict):
    # Создание студента
    stud = Student(
        studentTelegram_id=data['id_stud'],
        studentSurname=data['name_stud'][:-5],
        studentName=data['name_stud'][-4:-3],
        studentPatronymic=data['name_stud'][-2:-1],
        studentGroup=data['group']
    )
    # Добавление студента в таблицу
    session.add(stud)
    await session.commit()


async def orm_get_student(session: AsyncSession, id: int):
    query = select(Student).where(Student.studentTelegram_id == id)
    result = await session.execute(query)
    return result.scalar()


async def get_student_by_group(session: AsyncSession, group: int):
    query = select(Student.studentTelegram_id, Student.studentSurname, Student.studentName,
                   Student.studentPatronymic).where(Student.studentGroup == group)
    result = await session.execute(query)
    return result.all()

# выводит информацию по предметам препода
async def get_lesson_details(session: AsyncSession, id_teacher: int):
    # Выполняем запрос для получения lessonId, lessonName и Type у определенного преподавателя
    query = select(Lesson.lessonId, Lesson.lessonName, Lesson.lessonType, Lesson.group).where(Lesson.teacherTelegram_id == id_teacher)
    result = await session.execute(query)
    # Возвращаем список кортежей с данными уроков
    return result.all()

# выводит название и группу по id предмета
async def get_lessonName_by_id(session: AsyncSession, id_lesson: int):
    query = select(Lesson.lessonName, Lesson.lessonType, Lesson.group).where(Lesson.lessonId == id_lesson)
    result = await session.execute(query)
    return result.all()

async def orm_add_admin(session: AsyncSession, data: dict):
    # Создание админа
    admin = Admin(
        adminTelegram_id=data['id'],
        adminPassword=data['password']
    )

    # Добавление админа в таблицу
    session.add(admin)
    await session.commit()

async def orm_get_admin(session: AsyncSession, tg_id: int):
    query = select(Admin).where(Admin.adminTelegram_id == tg_id)
    result = await session.execute(query)
    return result.scalar()


# pip install openpyxl
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
    df.to_excel("table_name.xlsx", index=False)

# async def orm_add_gradebook(session: AsyncSession, data: dict):
#     # Создание дневника
#     grade_b = Gradebook(
#         lessonId=data['les_id'],
#         studentId=data['st_id'],
#         gradebook5=0,
#         gradebook4=0,
#         gradebook3=0,
#         gradebook2=0,
#         gradebookVisits=0
#     )
#
#     # Добавление преподавателя в таблицу
#     session.add(grade_b)
#     await session.commit()
#
# async def orm_add_admin(session: AsyncSession, data: dict):
#     # Создание дневника
#     adm = Admin(
#         adminTelegram_id=data['tg_id'],
#         adminPassword=data['password']
#     )
#
#     # Добавление преподавателя в таблицу
#     session.add(adm)
#     await session.commit()
