from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.chat_types import ChatTypeFilter
from all_buttons.buttons import start_kb
from all_buttons import buttons, inline_btn
from parser import ParsingSUAIRasp
from hashlib import sha256
from config import default_password
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.types import FSInputFile

from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query.orm_query_teacher import orm_add_teacher, orm_get_teacher, orm_add_lesson, orm_add_gradebook,\
    get_lesson_details, get_lessonName_by_id, get_student_by_group, add_gradebook_visit, \
    get_gradebook_by_stud, orm_get_student, add_gradebook_grade, create_student_dataframe

from dashboard.dashboard import create_dashboard

from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG")

pars: ParsingSUAIRasp = ParsingSUAIRasp()

teacher_router = Router()
teacher_router.message.filter(ChatTypeFilter(["private"]))

# Глобальные переменные
#attendance_data = {}

async def add_all_lessons(session: AsyncSession,data:dict, lessons: list):
    for el in lessons:
        await orm_add_lesson(session,data,el)



class Teacher_Registration(StatesGroup):
    # Шаги состояний
    id: State = State()
    name_and_post: State = State()
    password: State = State()

    teacher_registration_step = None

    teacher_registered = False

    texts = {
        "Teacher_Registration:name": "Введите имя заново:",
        "Teacher_Registration:name_and_post": "Выберете заново заново:",
        "Teacher_Registration:password": "Введите пароль заново:"
    }


# Начало регистрации преподавателя
@teacher_router.message(F.text == "Преподаватель")
async def starring(message: types.Message, state: FSMContext, session: AsyncSession):

    tg_id = message.chat.id
    teacher = await orm_get_teacher(session, tg_id)
    # Если преподаватель уже есть в базе данных, переходим к проверке пароля
    if teacher and teacher.teacherTelegram_id:
        Teacher_Registration.teacher_registered = True
        await message.answer("Введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Teacher_Registration.password)
        await state.update_data(id=teacher.teacherTelegram_id,
                                name_and_post=[teacher.teacherSurname,
                                               teacher.teacherName,
                                               teacher.teacherPatronymic,
                                               teacher.teacherPosition])
    else:
        # Если преподавателя нет в базе данных, переходим к регистрации имени
        await message.answer("Введите имя в формате: <i>Иванов И. И.</i>", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Teacher_Registration.id)


# Получение имени
@teacher_router.message(Teacher_Registration.id, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(id=message.chat.id)
    names: list = pars.get_names_and_post(message.text)

    if not names:
        await message.answer("Имя не найдено, пожалуйста, введите его заново.")

    name_post: dict[str, str] = {}

    for i in range(len(names)):
        name_post[names[i]] = f'teacher_{message.text}_{i}'

    await message.answer("Выберете себя", reply_markup=inline_btn.get_callback_btns(btns=name_post))
    await state.set_state(Teacher_Registration.name_and_post)

# Получения информации после выбора преподавателя из списка
@teacher_router.callback_query(Teacher_Registration.name_and_post, F.data.startswith("teacher_"))
async def name_post(callback: types.CallbackQuery, state: FSMContext):
    cd: list = callback.data.split("_")
    name_and_post: list = pars.get_names_and_post_arr(cd[-2],int(cd[-1]))
    await state.update_data(name_and_post=name_and_post)

    await callback.answer("Вы выбрали")
    await callback.message.answer(f"Введите пароль")
    await state.set_state(Teacher_Registration.password)

# Ввод пароля
@teacher_router.message(Teacher_Registration.password, F.text)
async def password(message: types.Message, state: FSMContext, session: AsyncSession):
    hash_password = sha256(message.text.encode('utf-8')).hexdigest()

    # Проверка был ли преподаватель зарегистрирован ранее
    if Teacher_Registration.teacher_registered:
        teach = await orm_get_teacher(session, message.chat.id)
        pw = teach.teacherPassword

        if hash_password == pw:
            await state.update_data(password=hash_password)
            Teacher_Registration.teacher_registration_step = None
            Teacher_Registration.teacher_registered = False
            await state.clear()
            await message.answer("Вы вошли!", reply_markup=buttons.teacher_kb_1)

        else:
            await message.answer("Пароль не верен. Попробуйте снова.")


    else:
        # Успешная регистрация
        if hash_password == default_password:
            await state.update_data(password=hash_password)
            Teacher_Registration.teacher_registration_step = None
            data = await state.get_data()

            try:
                await orm_add_teacher(session, data)
                await state.clear()
                await message.answer("Вы вошли!", reply_markup=buttons.teacher_kb_1)

                await add_all_lessons(session, data,pars.search_groups_and_lessons(f"{data['name_and_post'][0]+ data['name_and_post'][1]+ data['name_and_post'][2]}"))

            except Exception as ex:
                logger.warning('data is not add', ex)
                await message.answer("Попробуйте снова.")

            logger.debug(data['id'])
            logger.debug(data['password'])
            logger.debug(data['name_and_post'])

        # Не верный пароль
        else:
            await message.answer("Пароль не верен. Попробуйте снова.")

# Отмена действий
@teacher_router.message(StateFilter("*"), Command("отмена"))
@teacher_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if Teacher_Registration.teacher_registration_step:
        Teacher_Registration.teacher_registration_step = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=start_kb)


# Выбор занятия и группы
@teacher_router.message(F.text == 'Выбрать занятие')
async def choose_discipline(message: types.Message, session: AsyncSession):
    # Получаем ID чата пользователя
    id_chat = message.chat.id
    discipline: list = await get_lesson_details(session, id_chat)

    # Проверяем, есть ли дисциплины
    if not discipline:
        await message.answer("У вас нет привязанных дисциплин.")
        return

    # Создаем инлайн-кнопки
    buttons = [
        InlineKeyboardButton(
            text=f"{lesson_name} ({lesson_type}), гр. {lesson_group}",  # Текст кнопки: Название + Тип + Группа
            callback_data=f"select_discipline_{lesson_id}"  # Данные: id предмета
        )
        for lesson_id, lesson_name, lesson_type, lesson_group in discipline
    ]

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 1] for i in range(len(buttons))])

    # Отправляем сообщение с клавиатурой
    await message.answer("Выберите занятие:",reply_markup=keyboard)

#Обработчик выбора группы
@teacher_router.callback_query(F.data.startswith("select_discipline_"))
async def handle_selected_discipline(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    discipline_id = int(callback.data.split("_")[-1])
    details: list = await get_lessonName_by_id(session, discipline_id)

    # Распаковываем данные о предмете
    lesson_name, lesson_type, group = details[0]

    # Сохраняем номер группы в состоянии
    await state.update_data(selected_group=group, select_discipline_id=discipline_id)

    # Подтверждаем нажатие кнопки
    await callback.answer("Занятие выбрано")
    await callback.message.answer(f"Вы выбрали предмет: {lesson_name}({lesson_type}),"
                                  f" гр.{group}", reply_markup=buttons.teacher_kb_2)

# Отметить посещения
@teacher_router.message(F.text == 'Отметить посещение')
async def mark_visits(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data() #!!!!!!!!!!состояние не сброшено
    group = data.get("selected_group")

    if not group:
        await message.answer("Сначала выберите занятие.")
        await state.clear()
        return

    students: list = await get_student_by_group(session, group)

    # Создаем инлайн-кнопки
    buttons = [
        InlineKeyboardButton(
            text=f"{stud_surname} {stud_name}.{stud_patronymic}.",
            callback_data=f"select_stud_{stud_id}"
        )
        for stud_id, stud_surname, stud_name, stud_patronymic in students
    ]

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 1] for i in range(len(buttons))])

    # Отправляем сообщение с клавиатурой
    await message.answer("Отметьте студентов", reply_markup=keyboard)

#Обработчик выбора студента
@teacher_router.callback_query(F.data.startswith("select_stud_"))
async def handle_selected_stud(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    stud_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    discipline_id = data.get("select_discipline_id")

    if not discipline_id:
        await callback.message.answer("Сначала выберите занятие.")
        await state.clear()
        return

    # если в бд у ученика еще нет дневника, он создается
    students_gradebook = await get_gradebook_by_stud(session, stud_id, discipline_id)
    if not students_gradebook:
        await orm_add_gradebook(session, stud_id, discipline_id)

    # добавляем студенту одно посещение
    await add_gradebook_visit(session, stud_id, discipline_id)
    # Подтверждаем нажатие кнопки по студенту
    Stud = await orm_get_student(session, stud_id)
    await callback.answer(f"Вы отметили ученика {Stud.studentSurname} {Stud.studentName}.{ Stud.studentPatronymic}.")
    await callback.message.answer(f"Ученик {Stud.studentSurname} {Stud.studentName}.{ Stud.studentPatronymic}. отмечен.")

# Поставить оценки
@teacher_router.message(F.text == 'Поставить оценки')
async def give_ratings(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data() #!!!!!!!!!!состояние не сброшено
    group = data.get("selected_group")

    if not group:
        await message.answer("Сначала выберите занятие.")
        await state.clear()
        return

    students: list = await get_student_by_group(session, group)

    # Создаем инлайн-кнопки
    buttons = [
        InlineKeyboardButton(
            text=f"{stud_surname} {stud_name}.{stud_patronymic}.",
            callback_data=f"get_stud_{stud_id}"
        )
        for stud_id, stud_surname, stud_name, stud_patronymic in students
    ]

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 1] for i in range(len(buttons))])

    # Отправляем сообщение с клавиатурой
    await message.answer("Выберете кому поставить оценку", reply_markup=keyboard)

# Получить статистику
@teacher_router.message(F.text == 'Получить статистику')
async def give_ratings(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    df = await create_student_dataframe(session,data.get("selected_group"))

    create_dashboard(df,'dashboard/dashboard.png')

    photo = FSInputFile("dashboard/dashboard.png")
    await message.answer_photo(photo)


#Обработчик выставления оценок
@teacher_router.callback_query(F.data.startswith("get_stud_"))
async def handle_give_ratings(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    stud_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    discipline_id = data.get("select_discipline_id")

    if not discipline_id:
        await callback.message.answer("Сначала выберите занятие.")
        await state.clear()
        return

    # если в бд у ученика еще нет дневника, он создается
    students_gradebook = await get_gradebook_by_stud(session, stud_id, discipline_id)
    if not students_gradebook:
        await orm_add_gradebook(session, stud_id, discipline_id)

    # подтверждаем нажатие кнопок
    Stud = await orm_get_student(session, stud_id)
    stud_SNP = f"{Stud.studentSurname} {Stud.studentName}.{Stud.studentPatronymic}."
    await callback.answer(stud_SNP)
    await callback.message.answer(f"Какую оценку поставить студенту {stud_SNP}?",
                                  reply_markup=inline_btn.rating())
    # Сохраняем номер группы в состоянии
    await state.update_data(selected_group=Stud.studentGroup, select_discipline_id=discipline_id,
                            select_stud_id=stud_id, select_stud_SNP=stud_SNP)

#Обработчик выставления оценок
@teacher_router.callback_query(F.data.startswith("rating_"))
async def handle_ratings_into_database(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    rating = int(callback.data.split("_")[-1])
    data = await state.get_data()
    discipline_id = data.get("select_discipline_id")

    if not discipline_id:
        await callback.message.answer("Сначала выберите занятие.")
        await state.clear()
        return

    # выставляем студенту оценку
    await add_gradebook_grade(session, data.get("select_stud_id"), discipline_id, rating)
    # Подтверждаем нажатие кнопки по студенту
    await callback.answer(f"Оценка {rating}")
    await callback.message.answer(f"Вы поставили ученику {data.get('select_stud_SNP')} оценку {rating}.")



"""@teacher_router.message(F.text == "Выбрать группу")
async def choose_group(message: types.Message, session: AsyncSession):
    # Получаем ID чата пользователя
    id_chat = message.chat.id
    # Извлекаем данные преподавателя из базы
    teacher = await orm_get_teacher(session, id_chat)
    if not teacher:
        await message.answer("Вы не зарегистрированы как преподаватель. Пожалуйста, зарегистрируйтесь.")
        return
    # Формируем ФИО преподавателя
    teacher_name = f"{teacher.teacherSurname} {teacher.teacherName[0]}.{teacher.teacherPatronymic[0]}."
    groups: list = pars.search_groups(teacher_name)

    keyboard = get_group_buttons(groups)
    # Отправка сообщения с инлайн-кнопками
    await message.answer("Выберите группу:", reply_markup=keyboard)

# Обработчик выбора группы
@teacher_router.callback_query(F.data.startswith("select_group_"))
async def handle_group_selection(callback: types.CallbackQuery, state: FSMContext):
    group_number = callback.data.split("_")[-1]

    # Сохранение выбранной группы
    await state.update_data(selected_group=group_number)

    # Клавиатура с кнопкой "Начать отмечать посещения (10 мин)"
    start_attendance_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text= "Начать отмечать посещения (10 мин)", callback_data=f"start_attendance_{group_number}")]
        ]
    )
    await callback.answer(f"Вы выбрали группу {group_number}")
    await callback.message.answer(
        f"Группа {group_number} выбрана. Нажмите на кнопку, чтобы начать отмечать посещения.",
        reply_markup=start_attendance_kb
    )

# Начало учёта посещаемости
@teacher_router.callback_query(F.data.startswith("start_attendance_"))
async def start_attendance(callback: types.CallbackQuery, state: FSMContext):
    group_number = callback.data.split("_")[-1]
    attendance_data[group_number] = set()  # Сбрасываем список отметившихся студентов

    # Рассылка студентам уведомления с кнопкой "Отметиться"
    student_ids = "1349374748"  # Получение ID студентов из базы

    check_in_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отметиться",
                    callback_data=f"mark_attendance_{group_number}"
                )
            ]
        ]
    )

    for student_id in student_ids:
        await callback.bot.send_message(
            chat_id=student_id,
            text=f"Преподаватель начал отмечать посещаемость для группы {group_number}. У вас есть 10 минут!",
            reply_markup=check_in_kb
        )

    # Уведомление преподавателя
    await callback.answer("Учёт посещаемости начат.")
    await callback.message.answer(f"Учёт посещаемости для группы {group_number} начат на 10 минут.")

    # Таймер на 10 минут
    await asyncio.sleep(600)

    # Завершение учёта
    present_students = attendance_data.get(group_number, set())
    await callback.message.answer(
        f"Учёт посещаемости завершён. Присутствующие студенты:\n" +
        "\n".join(present_students) if present_students else "Никто не отметился."
    )

    # Очистка данных для группы
    attendance_data.pop(group_number, None)"""


