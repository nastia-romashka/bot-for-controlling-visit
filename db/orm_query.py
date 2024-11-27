from sqlalchemy.ext.asyncio import AsyncSession
from models import Teacher, Lesson, Student, Gradebook, Admin
from sqlalchemy import select
from parser import Lessons


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
        LessonName=lesson[2],
        LessontType=lesson[1],
        Group=lesson[0]
    )

    session.add(les)
    await session.commit()

# async def orm_add_student(session: AsyncSession, data: dict):
#     # Создание студента
#     stud = Student(
#         studentId=data['id'],
#         studentGroup=data['group'],
#         studentSurname=data['name'][0],
#         studentName=data['name'][1],
#         studentPatronymic=data['name'][2],
#         studentTelegram_id=data['tg_id']
#     )
#
#     # Добавление преподавателя в таблицу
#     session.add(stud)
#     await session.commit()
#
#
# async def orm_get_student(session: AsyncSession, id: int):
#     query = select(Student).where(Student.studentId == id)
#     result = await session.execute(query)
#     return result.scalar()
#
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