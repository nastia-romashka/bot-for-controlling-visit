from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.chat_types import ChatTypeFilter
from all_buttons.buttons import start_kb
from parser import ParsingSUAIRasp
from all_buttons.inline_btn import get_callback_btns
from hashlib import sha256
from config import default_password

from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_add_teacher, orm_get_teacher, orm_add_lesson

from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG")

pars: ParsingSUAIRasp = ParsingSUAIRasp()

teacher_router = Router()
teacher_router.message.filter(ChatTypeFilter(["private"]))

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

    name_post: dict[str, str] = {}

    for i in range(len(names)):
        name_post[names[i]] = f'teacher_{message.text}_{i}'

    await message.answer("Выберете себя", reply_markup=get_callback_btns(btns=name_post))
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
            await message.answer("Вы вошли!")


    else:
        # Успешная регистрация
        if hash_password == default_password:
            await state.update_data(password=hash_password)
            Teacher_Registration.teacher_registration_step = None
            data = await state.get_data()

            try:
                await orm_add_teacher(session, data)
                await state.clear()
                await message.answer("Вы вошли!")

                await add_all_lessons(session, data,pars.search_groups_and_lessons(f'{data['name_and_post'][0]+
                                                                  data['name_and_post'][1]+
                                                                  data['name_and_post'][2]}'))

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

