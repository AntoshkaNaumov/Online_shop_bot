# Кнопки клавиатуры админа
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

button_load = KeyboardButton('/Загрузить')
button_delete = KeyboardButton('/Удалить')
button_orders = KeyboardButton('/Просмотр')
button_loading = KeyboardButton('/Загрузка')


button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load)\
    .add(button_delete).add(button_orders)
