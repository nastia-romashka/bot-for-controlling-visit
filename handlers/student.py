from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.chat_types import ChatTypeFilter
from all_buttons import buttons
from parser import ParsingSUAIRasp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query.orm_query_student import orm_add_student, orm_get_student, get_lesson_details_by_group,\
    get_lessonName_by_id, get_gradebook_by_stud, orm_add_gradebook, orm_student_verification, orm_update_student


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

    buttons_stud: State = State()

#начало регистрации
@student_router.message(StateFilter(None), F.text == "Студент")
async def starting_st(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.clear()
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
        await state.set_state(Student_Registration.buttons_stud)

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

        old_tg_id_stud = await orm_student_verification(session, data)
        #проверка на добавления студента старостой
        if old_tg_id_stud:
            # изменение tg id
            await orm_update_student(session, old_tg_id_stud, message.chat.id)
            await state.set_state(Student_Registration.buttons_stud)
            await message.answer("Вы были зарегистрированы старостой", reply_markup=buttons.student_kb)
        else:
            try:
                await orm_add_student(session, data)
                await state.set_state(Student_Registration.buttons_stud)
                await message.answer("Вы успешно зарегистрировались", reply_markup=buttons.student_kb)

            except Exception as ex:
                logger.warning('data is not add', ex)
                await message.answer("Попробуйте снова.")

            logger.debug(data['id_stud'])
            logger.debug(data['name_stud'])
            logger.debug(data['group'])

    else:
        await message.answer(f"Группы {message.text} нет. Попробуйте снова")


# Выбор предмета
@student_router.message(Student_Registration.buttons_stud, F.text == 'Выбрать предмет')
async def choose_discipline(message: types.Message, session: AsyncSession):
    # Получаем ID чата пользователя
    id_chat = message.chat.id
    Stud = await orm_get_student(session, id_chat)
    group = int(Stud.studentGroup)
    classes: list = await get_lesson_details_by_group(session, group)

    # Проверяем, есть ли дисциплины
    if not classes:
        await message.answer("У вас нет привязанных дисциплин.")
        return

        # Создаем инлайн-кнопки
    buttons = [
        InlineKeyboardButton(
            text=f"{lesson_name} ({lesson_type})",  # Текст кнопки: Название + Тип
            callback_data=f"select_classes_{lesson_id}"  # Данные: id предмета
        )
        for lesson_id, lesson_name, lesson_type in classes
    ]

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 1] for i in range(len(buttons))])

    # Отправляем сообщение с клавиатурой
    await message.answer("Выберите предмет:", reply_markup=keyboard)

#Обработчик выбора предмета
@student_router.callback_query(F.data.startswith("select_classes_"))
async def handle_selected_discipline(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    discipline_id = int(callback.data.split("_")[-1])
    details: list = await get_lessonName_by_id(session, discipline_id)

    # Распаковываем данные о предмете
    lesson_name, lesson_type, group = details[0]

    # Сохраняем номер группы в состоянии
    await state.update_data(selected_group=group, select_discipline_id=discipline_id)

    # Подтверждаем нажатие кнопки
    await callback.answer("Занятие выбрано")
    await callback.message.answer(f"Вы выбрали предмет: {lesson_name}({lesson_type})"
                                  , reply_markup=buttons.student_kb)

# посмотреть оценки
@student_router.message(Student_Registration.buttons_stud, F.text == 'Оценки')
async def see_ratings(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()  # !!!!!!!!!!состояние не сброшено
    classe = data.get("select_discipline_id")
    id_chat = message.chat.id

    # если в бд у ученика еще нет дневника, он создается
    students_gradebook = await get_gradebook_by_stud(session, id_chat, classe)
    if not students_gradebook:
        await orm_add_gradebook(session, id_chat, classe)
        students_gradebook = await get_gradebook_by_stud(session, id_chat, classe)

    if not classe:
        await message.answer("Сначала выберите предмет.")
        await state.set_state(Student_Registration.buttons_stud)
        return

    # Формируем список оценок
    grades = (
        [5] * (students_gradebook.gradebook5 or 0) +
        [4] * (students_gradebook.gradebook4 or 0) +
        [3] * (students_gradebook.gradebook3 or 0) +
        [2] * (students_gradebook.gradebook2 or 0)
    )

    # Преобразуем список оценок в строку
    grades_str = ", ".join(map(str, grades))

    # Распаковываем данные о предмете
    details: list = await get_lessonName_by_id(session, classe)
    lesson_name, lesson_type, group = details[0]

    # Отправляем сообщение с оценками
    await message.answer(
        f"Ваши оценки по предмету {lesson_name}({lesson_type}): {grades_str}"
    )

# посмотреть посещения
@student_router.message(Student_Registration.buttons_stud, F.text == 'Посещения')
async def see_visits(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()  # !!!!!!!!!!состояние не сброшено
    classe = data.get("select_discipline_id")
    id_chat = message.chat.id

    if not classe:
        await message.answer("Сначала выберите предмет.")
        await state.set_state(Student_Registration.buttons_stud)
        return

    # если в бд у ученика еще нет дневника, он создается
    students_gradebook = await get_gradebook_by_stud(session, id_chat, classe)
    if not students_gradebook:
        await orm_add_gradebook(session, id_chat, classe)
        students_gradebook = await get_gradebook_by_stud(session, id_chat, classe)

    # Распаковываем данные о предмете
    details: list = await get_lessonName_by_id(session, classe)
    lesson_name, lesson_type, group = details[0]

    # Отправляем сообщение с оценками
    await message.answer(f"По предмету {lesson_name}({lesson_type}) у вас {students_gradebook.gradebookVisits} посещений")

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
