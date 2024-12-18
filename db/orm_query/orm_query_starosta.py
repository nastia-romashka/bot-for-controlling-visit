from sqlalchemy.ext.asyncio import AsyncSession
from db.models.student import Student
from sqlalchemy import select, update
import pandas as pd
import os

async def orm_add_starosta(session: AsyncSession, data: dict):
    # Создание старосты
    starosta = Student(
        studentTelegram_id=data['id_starosta'],
        studentSurname=data['name_starosta'][:-5],
        studentName=data['name_starosta'][-4:-3],
        studentPatronymic=data['name_starosta'][-2:-1],
        studentGroup=data['group_starosta'],
        check_Starosta=1,
        starosta_Password=data['password_starosta']
    )
    # Добавление старосты в таблицу
    session.add(starosta)
    await session.commit()

async def orm_update_starosta(session: AsyncSession, starosta_id: int):
    query = update(Student).where(Student.studentTelegram_id==starosta_id).values(check_Starosta=1)
    await session.execute(query)
    await session.commit()

async def orm_get_starosta(session: AsyncSession, id: int):
    query = select(Student).where(Student.studentTelegram_id == id)
    result = await session.execute(query)
    return result.scalar()

async def orm_add_check_starosta(session: AsyncSession, data: dict):
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

# Выгрузка по таблице студентов
async def orm_get_table_students(session: AsyncSession, group):
    # Выполняем запрос для получения всех записей
    query = select(Student).where(Student.studentGroup == group)
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
    df.to_excel("table_student_starosta.xlsx", index=False)

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