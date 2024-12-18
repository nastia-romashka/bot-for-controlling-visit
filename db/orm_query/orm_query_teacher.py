from sqlalchemy.ext.asyncio import AsyncSession
from db.models.teacher import Teacher
from db.models.gradebook import Gradebook
from db.models.student import Student
from db.models.lesson import Lesson
from sqlalchemy import select, update, func
from parser import Lessons
from loguru import logger
import pandas as pd
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

async def get_student_by_group(session: AsyncSession, group: str):
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

async def get_student_visits_by_group(session: AsyncSession, group: str):
    result = await session.execute(
        select(Student.studentTelegram_id, Gradebook.gradebookVisits)
        .join(Gradebook, Student.studentTelegram_id == Gradebook.studentTelegram_id)
        .where(Student.studentGroup == group)
    )
    return result.all()

async def get_student_average_grades(session: AsyncSession, group: str):
    result = await session.execute(
        select(
            Gradebook.studentTelegram_id,
            func.avg(
                (Gradebook.gradebook5 * 5 +
                 Gradebook.gradebook4 * 4 +
                 Gradebook.gradebook3 * 3 +
                 Gradebook.gradebook2 * 2)
                / (
                    func.nullif(
                        Gradebook.gradebook5 +
                        Gradebook.gradebook4 +
                        Gradebook.gradebook3 +
                        Gradebook.gradebook2,
                        0
                    )
                )
            ).label("average_grade")
        )
        .join(Student, Student.studentTelegram_id == Gradebook.studentTelegram_id)
        .where(Student.studentGroup == group)
        .group_by(Gradebook.studentTelegram_id)
    )
    return result.all()

async def get_student_grades_count(session: AsyncSession, group: str):
    result = await session.execute(
        select(
            Gradebook.studentTelegram_id,
            Gradebook.gradebook5,
            Gradebook.gradebook4,
            Gradebook.gradebook3,
            Gradebook.gradebook2
        )
        .join(Student, Student.studentTelegram_id == Gradebook.studentTelegram_id)
        .where(Student.studentGroup == group)
    )
    return result.all()

async def create_student_dataframe(session: AsyncSession, group: str):
    visits = await get_student_visits_by_group(session, group)
    grades = await get_student_average_grades(session, group)
    grades_count = await get_student_grades_count(session, group)
    student_info = await get_student_by_group(session, group)

    visits_df = pd.DataFrame(visits, columns=["studentTelegram_id", "gradebookVisits"])
    grades_df = pd.DataFrame(grades, columns=["studentTelegram_id", "average_grade"])
    grades_count_df = pd.DataFrame(grades_count, columns=[
        "studentTelegram_id",
        "gradebook5",
        "gradebook4",
        "gradebook3",
        "gradebook2"
    ])
    student_info_df = pd.DataFrame(student_info, columns=[
        "studentTelegram_id",
        "studentSurname",
        "studentName",
        "studentPatronymic"
    ])

    result_df = pd.merge(student_info_df, visits_df, on="studentTelegram_id", how="inner")
    result_df = pd.merge(result_df, grades_count_df, on="studentTelegram_id", how="inner")
    result_df = pd.merge(result_df, grades_df, on="studentTelegram_id", how="inner")

    return result_df

