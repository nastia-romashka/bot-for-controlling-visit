from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Староста'),
            KeyboardButton(text='Студент'),
            KeyboardButton(text='Преподаватель'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Кто вы?"
)

student_kb = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Выбрать предмет'),
            KeyboardButton(text='Оценки'),
            KeyboardButton(text='Посещения'),
        ],
    ],
    resize_keyboard=True,
)

starosta_kb = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Загрузить список группы'),
            KeyboardButton(text='Выбрать предмет'),
            KeyboardButton(text='Оценки'),
            KeyboardButton(text='Посещения'),
        ],
    ],
    resize_keyboard=True,
)

starosta_kb2 = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Вернуться назад')
        ],
    ],
    resize_keyboard=True,
)

teacher_kb_1 = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Выбрать занятие'),
        ],
    ],
    resize_keyboard=True,
)

teacher_kb_2 = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Отметить посещение'),
            KeyboardButton(text='Поставить оценки'),
            KeyboardButton(text='Выбрать занятие')
        ],
    ],
    resize_keyboard=True,
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Студенты'),
            KeyboardButton(text='Занятия'),
            KeyboardButton(text='Преподаватели'),
            KeyboardButton(text='Журнал')
        ],
    ],
    resize_keyboard=True,
)

admin_kb2 = ReplyKeyboardMarkup(
    keyboard=[[
            KeyboardButton(text='Назад')
        ],
    ],
    resize_keyboard=True,
)