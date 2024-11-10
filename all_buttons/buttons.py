from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Студент'),
            KeyboardButton(text='Преподаватель'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Кто вы?"
)

student_kb = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Отметиться'),
            KeyboardButton(text='Оценки'),
            KeyboardButton(text='Посещения'),
        ],
    ],
    resize_keyboard=True,
)
