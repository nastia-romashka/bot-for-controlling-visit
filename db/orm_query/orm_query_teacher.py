from sqlalchemy.ext.asyncio import AsyncSession
from db.models.teacher import Teacher
from db.models.gradebook import Gradebook
from db.models.student import Student
from db.models.lesson import Lesson
from sqlalchemy import select, update
from parser import Lessons
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

async def orm_get_student(session: AsyncSession, id: int):
    query = select(Student).where(Student.studentTelegram_id == id)
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

async def orm_add_gradebook(session: AsyncSession, st_id: int, les_id: int):
    # Создание дневника
    grade_b = Gradebook(
        lessonId=les_id,
        studentTelegram_id=st_id,
        gradebook5=0,
        gradebook4=0,
        gradebook3=0,
        gradebook2=0,
        gradebookVisits=0
    )

    # Добавление в таблицу
    session.add(grade_b)
    await session.commit()

async def add_gradebook_visit(session: AsyncSession, st_id: int, les_id: int):
    query = update(Gradebook).where(Gradebook.studentTelegram_id == st_id and Gradebook.lessonId == les_id).values(gradebookVisits=Gradebook.gradebookVisits + 1)
    await session.execute(query)
    await session.commit()

async def add_gradebook_grade(session: AsyncSession, st_id: int, les_id: int, grade: int):

    grade_column = f'gradebook{grade}'

    query = (update(Gradebook).where(Gradebook.studentTelegram_id == st_id, Gradebook.lessonId == les_id)
             .values({grade_column: getattr(Gradebook, grade_column) + 1}))

    await session.execute(query)
    await session.commit()

    #выводит дневник по id_студента и id предмета
async def get_gradebook_by_stud(session: AsyncSession, st_id: int, id_lesson: int):
    query = select(Gradebook).where(Gradebook.studentTelegram_id == st_id,  Gradebook.lessonId == id_lesson)
    result = await session.execute(query)
    return result.scalar()




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
