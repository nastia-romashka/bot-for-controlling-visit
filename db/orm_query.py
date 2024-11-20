from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Teacher, Lesson
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

async def orm_add_lesson(session: AsyncSession, data: dict, lesson:Lessons):
# Создание преподавателя
        les = Lesson(
            teacherTelegram_id=data['id'],
            LessonName=lesson[2],
            LessontType=lesson[1],
            Group=lesson[0]
        )

        session.add(les)
        await session.commit()