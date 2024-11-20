from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Teacher
from sqlalchemy import select


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