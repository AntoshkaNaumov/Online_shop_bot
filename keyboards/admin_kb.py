# Кнопки клавиатуры админа
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext


button_load = KeyboardButton('/Download')
button_delete = KeyboardButton('/Delete')
button_orders = KeyboardButton('/Orders')
button_loading = KeyboardButton('/Newsletter')


button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load)\
    .add(button_delete).add(button_orders).add(button_loading)


# Create the submenu keyboard
submenu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Confirmed Orders'),
    KeyboardButton('Paid Orders'),
    KeyboardButton('Back')
)
