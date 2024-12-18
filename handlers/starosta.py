from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from filters.chat_types import ChatTypeFilter
from all_buttons import buttons
from hashlib import sha256
from config import default_password
from parser import ParsingSUAIRasp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db.orm_query.orm_query_starosta import orm_get_starosta, orm_add_starosta, orm_get_table_students, \
    orm_load_table_students, orm_update_starosta

from db.orm_query.orm_query_student import orm_get_student, get_lesson_details_by_group,\
    get_lessonName_by_id, get_gradebook_by_stud, orm_add_gradebook

from sqlalchemy.ext.asyncio import AsyncSession


from loguru import logger
import sys

pars: ParsingSUAIRasp = ParsingSUAIRasp()

logger.remove()
logger.add(sys.stderr, level="DEBUG")

starosta_router = Router()
starosta_router.message.filter(ChatTypeFilter(["private"]))

class Starosta_Registration(StatesGroup):
    # Шаги состояний
    id_starosta: State = State()
    password_starosta: State = State()
    name_starosta: State = State()
    group_starosta: State = State()
    check_starosta: State = State()

    starosta_registration_step = None

    starosta_registered = False

    buttons_starosta: State = State()
    load_table_starosta: State = State()

@starosta_router.message(StateFilter(None), F.text == "Староста")
async def starting_starosta(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    await state.update_data(id_starosta=message.chat.id)
    await message.answer(f"Введите пароль")
    await state.set_state(Starosta_Registration.password_starosta)

# Ввод пароля
@starosta_router.message(Starosta_Registration.password_starosta, F.text)
async def password_starosta(message: types.Message, state: FSMContext, session: AsyncSession):
    hash_password = sha256(message.text.encode('utf-8')).hexdigest()

    starosta = await orm_get_starosta(session, message.chat.id)
    if starosta and starosta.studentTelegram_id and (hash_password == default_password):
        await orm_update_starosta(session, message.chat.id)
        Starosta_Registration.starosta_registered = True
        await message.answer("Вы уже зарегистрировались", reply_markup=buttons.starosta_kb)
        await state.update_data(id_starosta=starosta.studentTelegram_id,
                                name_starosta=[starosta.studentSurname,
                                               starosta.studentName,
                                               starosta.studentPatronymic],
                                group_starosta=starosta.studentGroup)
        await state.set_state(Starosta_Registration.buttons_starosta)

    else:
        # Верный пароль
        if hash_password == default_password:
            await state.update_data(password_starosta=hash_password)
            # await state.set_state(Admin_Registration.table)
            # Если студента нет в базе данных, переходим к регистрации
            await state.update_data(id_starosta=message.chat.id)
            await message.answer("Введите имя в формате: <i>Иванов И.И.</i>",
                                 reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(Starosta_Registration.name_starosta)

        # Не верный пароль
        else:
            await message.answer("Пароль не верен. Попробуйте снова.")


@starosta_router.message(Starosta_Registration.name_starosta, F.text)
async def add_name_starosta(message: types.Message, state: FSMContext):
    await state.update_data(name_starosta=message.text)
    await message.answer("Введите номер группы")
    await state.set_state(Starosta_Registration.group_starosta)

# Получение группы
@starosta_router.message(Starosta_Registration.group_starosta, F.text)
async def add_group_starosta(message: types.Message, state: FSMContext, session: AsyncSession):
    if pars.get_groups(str(message.text)) == True:
        await state.update_data(group_starosta=message.text)
        Starosta_Registration.starosta_registration_step = None
        data = await state.get_data()

        try:
            await orm_add_starosta(session, data)
            await state.set_state(Starosta_Registration.buttons_starosta)
            await message.answer("Вы успешно зарегистрировались", reply_markup=buttons.starosta_kb)

        except Exception as ex:
            logger.warning('data is not add', ex)
            await message.answer("Попробуйте снова.")

        logger.debug(data['id_starosta'])
        logger.debug(data['name_starosta'])
        logger.debug(data['group_starosta'])
        await state.set_state(Starosta_Registration.buttons_starosta)
    else:
        await message.answer(f"Группы {message.text} нет. Попробуйте снова")

# Выбор предмета
@starosta_router.message(Starosta_Registration.buttons_starosta, F.text == 'Выбрать предмет')
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
            callback_data=f"select_id_classes_{lesson_id}"  # Данные: id предмета
        )
        for lesson_id, lesson_name, lesson_type in classes
    ]

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 1] for i in range(len(buttons))])

    # Отправляем сообщение с клавиатурой
    await message.answer("Выберите предмет:", reply_markup=keyboard)

#Обработчик выбора предмета
@starosta_router.callback_query(F.data.startswith("select_id_classes_"), Starosta_Registration.buttons_starosta)
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
                                  , reply_markup=buttons.starosta_kb)

# посмотреть оценки
@starosta_router.message(Starosta_Registration.buttons_starosta, F.text == 'Оценки')
async def see_ratings(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    classe = data.get("select_discipline_id")
    id_chat = message.chat.id

    if not classe:
        await message.answer("Сначала выберите предмет.")
        await state.set_state(Starosta_Registration.buttons_starosta)
        return

    # если в бд у ученика еще нет дневника, он создается
    students_gradebook = await get_gradebook_by_stud(session, id_chat, classe)
    if not students_gradebook:
        await orm_add_gradebook(session, id_chat, classe)
        students_gradebook = await get_gradebook_by_stud(session, id_chat, classe)

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
@starosta_router.message(Starosta_Registration.buttons_starosta, F.text == 'Посещения')
async def see_visits(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    classe = data.get("select_discipline_id")
    id_chat = message.chat.id

    if not classe:
        await message.answer("Сначала выберите предмет.")
        await state.set_state(Starosta_Registration.buttons_starosta)
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

#загрузить список группы
@starosta_router.message(Starosta_Registration.buttons_starosta, F.text == 'Загрузить список группы')
async def download_list_students(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    group = data.get("group_starosta")
    await orm_get_table_students(session, group)

    # Отправка файла
    file_path = "table_student_starosta.xlsx"  # Путь к файлу
    file = FSInputFile(file_path)
    await state.set_state(Starosta_Registration.load_table_starosta)
    await message.answer_document(file, caption="Таблица студентов", reply_markup=buttons.starosta_kb2)

#Обработка нового списка
@starosta_router.message(Starosta_Registration.load_table_starosta, F.document,)
async def load_table_students(message: types.Message, state: FSMContext, session: AsyncSession):
    document = message.document
    file_id = document.file_id
    file_name = document.file_name

    # Проверка, является ли документ Excel файлом
    if file_name.endswith('.xlsx'):
        # Скачивание файла
        file = await message.bot.get_file(file_id)
        file_path = file.file_path

        await message.bot.download_file(file_path, f'./downloads/{file_name}')
        await orm_load_table_students(session, f'./downloads/{file_name}')
        await message.answer(f"Данные обновлены")

    else:
        await message.reply(f"Данный файл не формата .xlsx")

@starosta_router.message(StateFilter("*"), F.text=='Вернуться назад')
async def back(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == 'Вернуться назад':
        await state.set_state(Starosta_Registration.buttons_starosta)
        await message.answer("▲", reply_markup=buttons.starosta_kb)