#файл с кнопками
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Студент'),
            KeyboardButton(text='Преподаватель'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Кто вы?",
)
