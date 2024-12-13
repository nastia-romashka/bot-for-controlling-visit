from sqlalchemy.ext.asyncio import AsyncSession
from db.models.gradebook import Gradebook
from db.models.student import Student
from db.models.lesson import Lesson
from sqlalchemy import select

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

# выводит информацию по предметам по номеру группы
async def get_lesson_details_by_group(session: AsyncSession, num_group: int):
    # Выполняем запрос для получения lessonId, lessonName и Type у определенного преподавателя
    query = select(Lesson.lessonId, Lesson.lessonName, Lesson.lessonType).where(Lesson.group == num_group)
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

#выводит дневник по id_студента и id предмета
async def get_gradebook_by_stud(session: AsyncSession, st_id: int, id_lesson: int):
    query = select(Gradebook).where(Gradebook.studentTelegram_id == st_id,  Gradebook.lessonId == id_lesson)
    result = await session.execute(query)
    return result.scalar()