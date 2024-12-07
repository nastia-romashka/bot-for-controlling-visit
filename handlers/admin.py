from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from filters.chat_types import ChatTypeFilter
from all_buttons.buttons import start_kb
from all_buttons import buttons
from hashlib import sha256
from config import default_password

from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query_admin import orm_add_admin, orm_get_admin, orm_get_table_lesson, orm_load_table_lesson, orm_get_table_student,orm_get_table_teacher, orm_get_table_gradebook
from db.orm_query_admin import orm_load_table_teacher, orm_load_table_gradebook, orm_load_table_students
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG")

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]))


class Admin_Registration(StatesGroup):
    # Шаги состояний
    id: State = State()
    password: State = State()
    table: State = State()
    load_table: State = State()

    admin_registration_step = None

    admin_registered = False

    texts = {
        "Admin_Registration:password": "Введите пароль заново:"
    }


@admin_router.message(Command('admin'))
async def starring(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(id=message.chat.id)
    await message.answer(f"Введите пароль")
    await state.set_state(Admin_Registration.password)


# Ввод пароля
@admin_router.message(Admin_Registration.password, F.text)
async def password(message: types.Message, state: FSMContext, session: AsyncSession):
    hash_password = sha256(message.text.encode('utf-8')).hexdigest()

    adm = await orm_get_admin(session, message.chat.id)
    if adm and adm.adminTelegram_id:
        pw = adm.adminPassword

        if hash_password == pw:
            await state.update_data(password=hash_password)
            Admin_Registration.admin_registration_step = None
            Admin_Registration.admin_registered = False
            await state.set_state(Admin_Registration.table)
            await message.answer("Вы вошли!", reply_markup=buttons.admin_kb)


    else:
        # Успешная регистрация
        if hash_password == default_password:
            await state.update_data(password=hash_password)
            Admin_Registration.admin_registration_step = None
            data = await state.get_data()

            try:
                await orm_add_admin(session, data)
                await state.set_state(Admin_Registration.table)
                await message.answer("Вы вошли!", reply_markup=buttons.admin_kb)

            except Exception as ex:
                logger.warning('data is not add', ex)
                await message.answer("Попробуйте снова.")

            logger.debug(data['id'])
            logger.debug(data['password'])

        # Не верный пароль
        else:
            await message.answer("Пароль не верен. Попробуйте снова.")


@admin_router.message(Admin_Registration.table, F.text.in_(['Студенты', 'Занятия', 'Преподаватели', 'Журнал']))
async def get_table(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == 'Студенты':
        # Генерация таблицы
        await orm_get_table_student(session)
        await state.update_data(table=message.text)

        # Отправка файла
        file_path = "table_student.xlsx"  # Путь к файлу
        file = FSInputFile(file_path)
        await state.set_state(Admin_Registration.load_table)
        await message.answer_document(file, caption="Таблица студентов", reply_markup=buttons.admin_kb2)


    elif message.text == 'Занятия':
        # Генерация таблицы
        await orm_get_table_lesson(session)
        await state.update_data(table=message.text)

        # Отправка файла
        file_path = "table_lessons.xlsx"  # Путь к файлу
        file = FSInputFile(file_path)
        await state.set_state(Admin_Registration.load_table)
        await message.answer_document(file, caption="Таблица занятий", reply_markup=buttons.admin_kb2)

    elif message.text == 'Преподаватели':
        # Генерация таблицы
        await orm_get_table_teacher(session)
        await state.update_data(table=message.text)

        # Отправка файла
        file_path = "table_teacher.xlsx"  # Путь к файлу
        file = FSInputFile(file_path)
        await state.set_state(Admin_Registration.load_table)
        await message.answer_document(file, caption="Таблица преподавателей", reply_markup=buttons.admin_kb2)

    elif message.text == 'Журнал':
        # Генерация таблицы
        await orm_get_table_gradebook(session)
        await state.update_data(table=message.text)

        # Отправка файла
        file_path = "table_gradebook.xlsx"  # Путь к файлу
        file = FSInputFile(file_path)
        await state.set_state(Admin_Registration.load_table)
        await message.answer_document(file, caption="Таблица журнал", reply_markup=buttons.admin_kb2)






@admin_router.message(Admin_Registration.load_table, F.document,)
async def load_table(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    document = message.document
    file_id = document.file_id
    file_name = document.file_name

    # Проверка, является ли документ Excel файлом
    if file_name.endswith('.xlsx'):
        # Скачивание файла
        file = await message.bot.get_file(file_id)
        file_path = file.file_path

        if data['table'] == 'Студенты':
            await message.bot.download_file(file_path, f'./downloads/{file_name}')
            await orm_load_table_students(session, f'./downloads/{file_name}')
            await message.answer(f"Данные обновлены")


        elif data['table'] == 'Занятия':

            await message.bot.download_file(file_path, f'./downloads/{file_name}')
            await orm_load_table_lesson(session, f'./downloads/{file_name}')
            await message.answer(f"Данные обновлены")

        elif data['table'] == 'Преподаватели':

            await message.bot.download_file(file_path, f'./downloads/{file_name}')
            await orm_load_table_teacher(session, f'./downloads/{file_name}')
            await message.answer(f"Данные обновлены")

        elif data['table'] == 'Журнал':

            await message.bot.download_file(file_path, f'./downloads/{file_name}')
            await orm_load_table_gradebook(session, f'./downloads/{file_name}')
            await message.answer(f"Данные обновлены")


    else:
        await message.reply(f"Данный файл не формата .xlsx")

@admin_router.message(StateFilter("*"), F.text=='Назад')
async def back(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == 'Назад':
        await state.set_state(Admin_Registration.table)
        await message.answer("▲", reply_markup=buttons.admin_kb)

# Отмена действий
@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if Admin_Registration.admin_registration_step:
        Admin_Registration.admin_registration_step = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=start_kb)
