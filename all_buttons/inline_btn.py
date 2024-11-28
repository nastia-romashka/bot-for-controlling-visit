from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()

def get_group_buttons(groups: list[str]) -> InlineKeyboardMarkup:
    """
    :param groups: Список номеров групп.
    :return: InlineKeyboardMarkup с кнопками для выбора групп.
    """
    buttons = [
        InlineKeyboardButton(text=f"Группа {group}", callback_data=f"select_group_{group}")
        for group in groups
    ]
    # Возвращаем клавиатуру, где каждая кнопка в отдельной строке
    return InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])
