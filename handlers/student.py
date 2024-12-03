from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.chat_types import ChatTypeFilter
from all_buttons.buttons import start_kb
from all_buttons import buttons
from parser import ParsingSUAIRasp

from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_add_student, orm_get_student

from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG")

pars: ParsingSUAIRasp = ParsingSUAIRasp()

student_router = Router()
student_router.message.filter(ChatTypeFilter(["private"]))

class Student_Registration(StatesGroup):
    # Шаги состояний
    id_stud: State = State()
    name_stud: State = State()
    group: State = State()

    student_registration_step = None

    student_registered = False

#начало регистрации
@student_router.message(StateFilter(None), F.text == "Студент")
async def starting_st(message: types.Message, state: FSMContext, session: AsyncSession):
    tg_id = message.chat.id
    student = await orm_get_student(session, tg_id)
    # Если студент уже есть в базе данных, передаем ему клавиатуру студента
    if student and student.studentTelegram_id:
        Student_Registration.student_registered = True
        await message.answer("Вы уже зарегистрировались", reply_markup=buttons.student_kb)
        await state.update_data(id_stude=student.studentTelegram_id,
                                name_stude=[student.studentSurname,
                                            student.studentName,
                                            student.studentPatronymic],
                                group=student.studentGroup)

    else:
        # Если студента нет в базе данных, переходим к регистрации
        await state.update_data(id_stud=message.chat.id)
        await message.answer("Введите имя в формате: <i>Иванов И.И.</i>", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Student_Registration.name_stud)

# Получение имени
@student_router.message(Student_Registration.name_stud, F.text)
async def add_name_st(message: types.Message, state: FSMContext):
    await state.update_data(name_stud=message.text)
    await message.answer("Введите номер группы")
    await state.set_state(Student_Registration.group)

# Получение группы
@student_router.message(Student_Registration.group, F.text)
async def add_group_st(message: types.Message, state: FSMContext, session: AsyncSession):
    if pars.get_groups(str(message.text)) == True:
        await state.update_data(group=message.text)
        Student_Registration.student_registration_step = None
        data = await state.get_data()

        try:
            await orm_add_student(session, data)
            await state.clear()
            await message.answer("Вы успешно зарегистрировались", reply_markup=buttons.student_kb)

        except Exception as ex:
            logger.warning('data is not add', ex)
            await message.answer("Попробуйте снова.")

        logger.debug(data['id_stud'])
        logger.debug(data['name_stud'])
        logger.debug(data['group'])
        await state.clear()
    else:
        await message.answer(f"Группы {message.text} нет. Попробуйте снова")

"""# Обработчик отметки студента
@student_router.callback_query(F.data.startswith("mark_attendance_"),)
async def mark_attendance(message: types.Message, state: FSMContext, session: AsyncSession):
    tg_id = message.chat.id
    student = await orm_get_student(session, tg_id)
    group_number = student.studentGroup

    # Добавляем студента в список отметившихся
    student_name = f"{student.studentSurname} {student.studentName}.{student.studentPatronymic}."
    if group_number in attendance_data:
        attendance_data[group_number].add(student_name)
        await callback.answer("Вы отметились!")
    else:
        await message.answer("Время вышло", reply_markup=buttons.student_kb)

@student_router.message(StateFilter("*"), Command("отмена"))
@student_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler_st(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действия отменены", reply_markup=start_kb)"""
