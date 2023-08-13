from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Define buttons
b1 = KeyboardButton('/Помощь')
b2 = KeyboardButton('/Доставка')
b3 = KeyboardButton('/Каталог')
b4 = KeyboardButton('/Регистрация')
b5 = KeyboardButton('/Оплата')
b6 = KeyboardButton('/Корзина')

# Create a custom keyboard layout
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)


# Add buttons to rows with custom text color
kb_client.row(b3, b6, b1)
kb_client.row(b4, b5, b2)


#b7 = KeyboardButton('/Офоромить заказ')
#b8 = KeyboardButton('/Мои заказы')

#kb_client2 = ReplyKeyboardMarkup(resize_keyboard=True)

#kb_client.add(b7).add(b8)
