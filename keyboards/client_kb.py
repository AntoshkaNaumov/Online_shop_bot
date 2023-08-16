from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Define buttons
b1 = KeyboardButton('/Помощь')
b2 = KeyboardButton('/Доставка')
b3 = KeyboardButton('/Каталог')
b4 = KeyboardButton('/Регистрация')
b5 = KeyboardButton('/Оплата')
b6 = KeyboardButton('/Корзина')
b7 = KeyboardButton('/Заказы')

# Create a custom keyboard layout
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)


# Add buttons to rows with custom text color
kb_client.row(b3, b6, b7)
kb_client.row(b4, b5, b2)
kb_client.add(b1)
