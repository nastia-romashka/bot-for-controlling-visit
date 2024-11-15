from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.chat_types import ChatTypeFilter
from all_buttons.buttons import start_kb
from all_buttons import buttons
from parser import ParsingSUAIRasp

pars: ParsingSUAIRasp = ParsingSUAIRasp()

student_router = Router()
student_router.message.filter(ChatTypeFilter(["private"]))

class Student_Registration(StatesGroup):
    # Шаги состояний
    name = State()
    group = State()


@student_router.message(StateFilter(None), F.text == "Студент")
async def starting(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите имя в формате: <i>Иванов И. И.</i>", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Student_Registration.name)

@student_router.message(Student_Registration.name, F.text)
async def add_name_st(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите номер группы")
    await state.set_state(Student_Registration.group)

@student_router.message(Student_Registration.group, F.text)
async def add_name_st(message: types.Message, state: FSMContext):
    if pars.get_groups(str(message.text)) == True:
        await state.update_data(group=message.text)
        await message.answer("Успешная регистрация", reply_markup=buttons.student_kb)
        #data = await state.get_data()
        await state.clear()
    else:
        await message.answer(f"Группы {message.text} нет. Попробуйте снова")

@student_router.message(StateFilter("*"), Command("отмена"))
@student_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действия отменены", reply_markup=start_kb)
