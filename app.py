# Файл для создания бота
import asyncio
import os
from loguru import logger

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from handlers.teacher import teacher_router
from handlers.student import student_router

from db.engine import create_db, drop_db, session_maker
from middlewares.db import DataBaseSession

from all_buttons import buttons

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# список id админов
bot.my_admins_list = []

dp = Dispatcher()


# функция, реагирующая на команду start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("В роли кого вы будете использовать этого тг бота?",
                         reply_markup=buttons.start_kb)


# Обработчик событий для учителя
dp.include_router(teacher_router)
# Обработчик событий для студента
dp.include_router(student_router)


# Функция создания db при включении бота
async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    logger.info('The bot has finished working!')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
