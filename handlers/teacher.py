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

from database import DataBase

from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG")

pars: ParsingSUAIRasp = ParsingSUAIRasp()

teacher_router = Router()
teacher_router.message.filter(ChatTypeFilter(["private"]))

db: DataBase = DataBase()


class Teacher_Registration(StatesGroup):
    # Шаги состояний
    id: State = State()
    name_and_post: State = State()
    password: State = State()

    teacher_registration_step = None

    texts = {
        "Teacher_Registration:name": "Введите имя заново:",
        "Teacher_Registration:name_and_post": "Выберете заново заново:",
        "Teacher_Registration:password": "Введите пароль заново:"
    }


@teacher_router.message(F.text == "Преподаватель")
async def starring(message: types.Message, state: FSMContext):
    await message.answer("Введите имя в формате: <i>Иванов И. И.</i>", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Teacher_Registration.id)


@teacher_router.message(Teacher_Registration.id, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(id=message.chat.id)
    names: list = pars.get_names_and_post(message.text)

    name_post: dict[str, str] = {}

    for i in range(len(names)):
        name_post[names[i]] = f'teacher_{message.text}_{i}'

    await message.answer("Выберете себя", reply_markup=get_callback_btns(btns=name_post))
    await state.set_state(Teacher_Registration.name_and_post)


@teacher_router.callback_query(Teacher_Registration.name_and_post, F.data.startswith("teacher_"))
async def name_post(callback: types.CallbackQuery, state: FSMContext):
    cd: list = callback.data.split("_")
    inf: list = pars.get_names_and_post(cd[-2])
    name_and_post = inf[int(cd[-1])]
    await state.update_data(name_and_post=name_and_post)

    await callback.answer("Вы выбрали")
    await callback.message.answer(f"Введите пароль")
    await state.set_state(Teacher_Registration.password)


@teacher_router.message(Teacher_Registration.password, F.text)
async def password(message: types.Message, state: FSMContext):
    hash_password = sha256(message.text.encode('utf-8')).hexdigest()
    if hash_password == default_password:
        await state.update_data(password=hash_password)
        Teacher_Registration.teacher_registration_step = None
        data = await state.get_data()
        await state.clear()
        await message.answer("Вы вошли!")
        # Надо доработать
        FIO: str= data['name_and_post']
        fio_arr = []
        fio_arr.append(FIO[:FIO.find(' ')])
        FIO = FIO[FIO.find(' ') + 1:]
        fio_arr.append(FIO[:FIO.find('.')])
        FIO = FIO[FIO.find('.') + 1:]
        fio_arr.append(FIO[:FIO.find('.')])
        FIO = FIO[FIO.find('.'):]
        fio_arr.append(FIO[FIO.rfind('-') + 2:])

        logger.debug(data['id'])
        logger.debug(data['password'])
        logger.debug(fio_arr)

        db.add_teacher_in_db(array = fio_arr, tg_id=data['id'],password=data['password'])
    else:
        await message.answer("Пароль не верен. Попробуйте снова.")


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


db.close()
