# Файл для создания бота
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import bot_token
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from handlers.teacher import teacher_router

from all_buttons import buttons

bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

#функция, реагирующая на команду start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("В роли кого вы будете использовать этого тг бота?",
                         reply_markup=buttons.start_kb)

dp.include_router(teacher_router)

async def main():
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())



