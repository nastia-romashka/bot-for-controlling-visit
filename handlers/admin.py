from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InputFile
from aiogram.types import FSInputFile
from filters.chat_types import ChatTypeFilter
from all_buttons.buttons import start_kb
from all_buttons import buttons
from hashlib import sha256
from config import default_password

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_add_admin, orm_get_admin, orm_get_table_lesson

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

    admin_registration_step = None

    admin_registered = False

    texts = {
        "Admin_Registration:password": "Введите пароль заново:"
    }


# Начало регистрации преподавателя
@admin_router.message(Command('admin'))
async def starring(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(id=message.chat.id)
    await message.answer(f"Введите пароль")
    await state.set_state(Admin_Registration.password)

# Ввод пароля
@admin_router.message(Admin_Registration.password, F.text)
async def password(message: types.Message, state: FSMContext, session: AsyncSession):
    hash_password = sha256(message.text.encode('utf-8')).hexdigest()

    # Проверка был ли преподаватель зарегистрирован ранее
    if Admin_Registration.admin_registered:
        adm = await orm_get_admin(session, message.chat.id)
        pw = adm.adminPassword

        if hash_password == pw:
            await state.update_data(password=hash_password)
            Admin_Registration.admin_registration_step = None
            Admin_Registration.admin_registered = False
            await state.clear()
            await message.answer("Вы вошли!", reply_markup=buttons.admin_kb)


    else:
        # Успешная регистрация
        if hash_password == default_password:
            await state.update_data(password=hash_password)
            Admin_Registration.admin_registration_step = None
            data = await state.get_data()

            try:
                await orm_add_admin(session, data)
                await state.clear()
                await message.answer("Вы вошли!", reply_markup=buttons.admin_kb)

            except Exception as ex:
                logger.warning('data is not add', ex)
                await message.answer("Попробуйте снова.")

            logger.debug(data['id'])
            logger.debug(data['password'])

        # Не верный пароль
        else:
            await message.answer("Пароль не верен. Попробуйте снова.")

@admin_router.message(StateFilter("*"), F.text.in_(['Студенты', 'Занятия', 'Преподаватели', 'Журнал']))
async def get_table(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == 'Занятия':
        # Генерация таблицы
        await orm_get_table_lesson(session)

        # Отправка файла
        file_path = "table_name.xlsx"  # Путь к файлу
        file = FSInputFile(file_path)
        await message.answer_document(file, caption="Таблица занятий")

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
