from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Teacher, Lesson, Student, Gradebook, Admin
from sqlalchemy import select, update
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
async def orm_get_table_student(session: AsyncSession):
    # Выполняем запрос для получения всех записей
    query = select(Student)
    result = await session.execute(query)
    student = result.scalars().all()  # Извлекаем объекты ORM

    # Преобразуем данные в список словарей
    data = [
        {
            'studentTelegram_id':  stud.studentTelegram_id,
            'studentGroup':  stud.studentGroup,
            'studentSurname':  stud.studentSurname,
            'studentName':  stud.studentName,
            'studentPatronymic':  stud.studentPatronymic
        }
        for stud in student
    ]

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в Excel
    df.to_excel("table_student.xlsx", index=False)
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


async def orm_get_table_teacher(session: AsyncSession):
    # Выполняем запрос для получения всех записей
    query = select(Teacher)
    result = await session.execute(query)
    teachers = result.scalars().all()  # Извлекаем объекты ORM

    # Преобразуем данные в список словарей
    data = [
        {
            'teacherTelegram_id': teacher.teacherTelegram_id,
            'teacherSurname':  teacher.teacherSurname,
            'teacherName': teacher.teacherName,
            'teacherPatronymic':   teacher.teacherPatronymic,
            'teacherPosition':     teacher.teacherPosition,
            'teacherPassword':   teacher.teacherPassword}

        for teacher in teachers
    ]

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в Excel
    df.to_excel("table_teacher.xlsx", index=False)

async def orm_get_table_gradebook(session: AsyncSession):
    # Выполняем запрос для получения всех записей
    query = select(Gradebook)
    result = await session.execute(query)
    gradebooks = result.scalars().all()  # Извлекаем объекты ORM

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

        for gradebook in gradebooks
    ]

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в Excel
    df.to_excel("table_gradebook.xlsx", index=False)

async def orm_load_table_students(session: AsyncSession, path: str):
    # Читаем файл
    xlsx = pd.ExcelFile(path)
    sheet1_df = xlsx.parse('Sheet1')

    for row in sheet1_df.itertuples():
        query = update(Student).where(Student.studentTelegram_id == row.studentTelegram_id).values({
            'studentGroup':  row.studentGroup,
            'studentSurname':  row.studentSurname,
            'studentName':  row.studentName,
            'studentPatronymic':  row.studentPatronymic})

        await session.execute(query)
        await session.commit()

async def orm_load_table_lesson(session: AsyncSession, path: str):
    # Читаем файл
    xlsx = pd.ExcelFile(path)
    sheet1_df = xlsx.parse('Sheet1')

    for row in sheet1_df.itertuples():
        query = update(Lesson).where(Lesson.lessonId == row.lessonId).values({'teacherTelegram_id': row.teacherTelegram_id,
                                                                              'lessonName': row.lessonName,
                                                                              'lessonType': row.lessonType,
                                                                              'group':row.group})

        await session.execute(query)
        await session.commit()

async def orm_load_table_teacher(session: AsyncSession, path: str):
    # Читаем файл
    xlsx = pd.ExcelFile(path)
    sheet1_df = xlsx.parse('Sheet1')

    for row in sheet1_df.itertuples():
        query = update(Teacher).where(Teacher.teacherTelegram_id == row.teacherTelegram_id).values({
            'teacherSurname':  row.teacherSurname,
            'teacherName': row.teacherName,
            'teacherPatronymic':   row.teacherPatronymic,
            'teacherPosition':     row.teacherPosition,
            'teacherPassword':   row.teacherPassword})

        await session.execute(query)
        await session.commit()

async def orm_load_table_gradebook(session: AsyncSession, path: str):
    # Читаем файл
    xlsx = pd.ExcelFile(path)
    sheet1_df = xlsx.parse('Sheet1')

    for row in sheet1_df.itertuples():
        query = update(Gradebook).where(Gradebook.gradebookId == row.gradebookId).values({
            'lessonId': row.lessonId,
            'studentTelegram_id': row.studentTelegram_id,
            'gradebook5': row.gradebook5,
            'gradebook4': row.gradebook4,
            'gradebook3': row.gradebook3,
            'gradebook2': row.gradebook2,
            'gradebookVisits': row.gradebookVisits})

        await session.execute(query)
        await session.commit()


async def orm_add_gradebook(session: AsyncSession, data: dict):
    # Создание дневника
    grade_b = Gradebook(
        lessonId=data['les_id'],
        studentTelegram_id=data['st_id'],
        gradebook5=0,
        gradebook4=0,
        gradebook3=0,
        gradebook2=0,
        gradebookVisits=0
    )

    # Добавление преподавателя в таблицу
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
