# Файл для создания бота
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import bot_token

import buttons

bot = Bot(token=bot_token)
dp = Dispatcher()

#функция, реагирующая на команду start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("В роли кого вы будете использовать этого тг бота?",
                         reply_markup=buttons.start_kb)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())



