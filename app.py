# Файл для создания бота
import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from handlers.teacher import teacher_router
from handlers.student import student_router

from all_buttons import buttons

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
#список id админов
bot.my_admins_list = []

dp = Dispatcher()

#функция, реагирующая на команду start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("В роли кого вы будете использовать этого тг бота?",
                         reply_markup=buttons.start_kb)

dp.include_router(teacher_router)
dp.include_router(student_router)

async def main():
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())
