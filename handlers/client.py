from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_client
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked, ChatNotFound
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.types import LabeledPrice
from aiogram.types import ReplyKeyboardRemove
from data_base import sqlite_db
from config import PAYMENT_TOKEN, GROUP_ADMIN_ID
import sqlite3
import time
import os


class Registration(StatesGroup):
    name = State()
    telephone = State()
    address = State()


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    try:
        await bot.send_message(
            message.from_user.id,
            'Добро пожаловать в  наш интернет-магазин. Вы можете заказать сумки '
            'из каталога. Для начала зарегистрируйтесь. Затем выбирете кнопку /Каталог из меню',
            reply_markup=kb_client)
        await message.delete()
    except BotBlocked:
        await message.reply('Вы заблокировали бота, но вы можете написать ему в ЛС: https://t.me/online_shop23_bot')
    except ChatNotFound:
        await message.reply('Чат не найден. Пожалуйста, используйте бота в ЛС: https://t.me/online_shop23_bot')


@dp.message_handler(commands=['Регистрация'], state=None)
async def registration(message: types.Message):
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users'
                ' (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name VARCHAR(100), telephone VARCHAR(50),'
                ' address VARCHAR(200))')
    conn.commit()
    cur.close()
    conn.close()
    await Registration.name.set()
    await bot.send_message(message.from_user.id, 'Сейчас Вас зарегистрируем! Введите Ваше имя')


@dp.message_handler(state=Registration.name)
async def user_nam(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await Registration.next()
    await bot.send_message(message.chat.id, 'Введите номер телефона')


@dp.message_handler(state=Registration.telephone)
async def user_tel(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['telephone'] = message.text

    await Registration.next()
    await bot.send_message(message.chat.id, 'Введите адрес доставки')


@dp.message_handler(state=Registration.address)
async def user_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text

    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    user_id = message.from_user.id
    name = data['name']
    telephone = data['telephone']
    address = data['address']

    # Check if user_id already exists in the database
    cur.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    user_count = cur.fetchone()[0]

    if user_count > 0:
        await bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')
    else:
        cur.execute("INSERT INTO users (user_id, name, telephone, address) VALUES (?, ?, ?, ?)",
                    (user_id, name, telephone, address))
        conn.commit()
        await bot.send_message(message.chat.id, 'Пользователь зарегистрирован')

    cur.close()
    conn.close()

    await state.finish()


async def shop_information(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Магазин осуществляет доставку по России компанией СДЭК до пункта выдачи')


@dp.message_handler(commands=['Оплата'])
async def pay_information(message: types.Message):
    await bot.send_message(
        message.from_user.id, 'Для оплаты заказов мы сотрудничаем с  ЮKassa.'
        ' Он предлагает самые популярные способы оплаты:'
        'ЮMoney, Qiwi, Visa, Master Card, МИР, мобильная коммерция и другие.')


async def shop_menu_command(message: types.Message):
    # Retrieve products from the database using the sql_read function
    products = await sqlite_db.sql_read()

    for product in products:
        photo, name, description, price = product

        # Create a string to display the product details
        product_info = f"Название: {name}\nОписание: {description}\nЦена, руб.: {price}"

        # Create an InlineKeyboardMarkup to hold the buttons for each product
        keyboard = InlineKeyboardMarkup()

        # Add "Купить" button
        buy_button = InlineKeyboardButton('Купить', callback_data=f"купить_{name}")
        keyboard.row(buy_button)

        # Add "В корзину" button
        add_to_cart_button = InlineKeyboardButton('В корзину', callback_data=f"в_корзину_{name}")
        keyboard.row(add_to_cart_button)

        # Send the product photo along with the product details and the buttons
        await bot.send_photo(message.chat.id, photo, caption=product_info, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith('в_корзину_'))
async def add_to_cart(callback_query: types.CallbackQuery, state: FSMContext):
    product_name = callback_query.data[10:]  # Extract the product name from the callback data

    async with state.proxy() as data:
        user_cart = data.get("user_cart", {})

    # Retrieve the complete product details from the database
    product_details = get_product_details_from_database(product_name)  # Function to fetch product details

    if product_details:
        # Update the user's cart with complete product details and quantity
        user_cart[product_name] = user_cart.get(product_name, {'quantity': 0})  # Initialize as dictionary
        user_cart[product_name]['quantity'] += 1
        user_cart[product_name]['details'] = product_details  # Store complete product details

        # Update the user's cart in the state
        async with state.proxy() as data:
            data["user_cart"] = user_cart

        await bot.answer_callback_query(callback_query.id, text="Товар добавлен в корзину")
    else:
        await bot.answer_callback_query(callback_query.id, text="Произошла ошибка при получении информации о товаре")


# Function to retrieve product details from the database
def get_product_details_from_database(product_name):
    conn = sqlite3.connect('online_shop.db')
    cursor = conn.cursor()

    # Retrieve product details from the 'shop' table based on the product name
    cursor.execute("SELECT img, name, description, price FROM shop WHERE name=?", (product_name,))
    result = cursor.fetchone()

    conn.close()

    if result:
        photo, name, description, price = result
        product_details = {
            'name': name,
            'description': description,
            'price': price
        }
        return product_details
    else:
        return None


def calculate_cart_total(user_cart, db_connection):
    total_quantity = 0
    total_price = 0

    # Create a cursor to execute SQL queries
    cursor = db_connection.cursor()

    for product_name, product_info in user_cart.items():
        quantity = product_info['quantity']  # Extract the quantity from the product info

        cursor.execute("SELECT price FROM shop WHERE name=?", (product_name,))
        result = cursor.fetchone()

        if result:
            price_per_item = float(result[0])  # Assuming price is stored as text
            total_quantity += quantity  # Increment the total quantity
            total_price += price_per_item * quantity

    return total_quantity, total_price


# Обработчик кнопки "Корзина"
async def show_cart(message: types.Message, state: FSMContext):
    # Получаем текущую корзину пользователя из состояния
    async with state.proxy() as data:
        user_cart = data.get("user_cart", {})

    if not user_cart:
        await message.answer("Ваша корзина пуста.")
        return

    # Создаем подключение к базе данных
    db_connection = sqlite3.connect("online_shop.db")

    # Вызываем функцию для подсчета общей суммы и количества товаров
    total_quantity, total_price = calculate_cart_total(user_cart, db_connection)

    # Закрываем соединение с базой данных
    db_connection.close()

    cart_message = "Товары в корзине:\n"
    # ... Формируем сообщение о товарах в корзине ...
    for product_name, quantity in user_cart.items():
        cart_message += f"{product_name} - {quantity} \n"

    # Добавляем информацию о количестве и общей сумме в сообщение
    cart_message += f"\nВсего товаров: {total_quantity} шт.\n"
    cart_message += f"Общая сумма заказа: {total_price} руб."

    kb_cart_actions = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_cart_actions.row("Оформить заказ", "Мои заказы")
    kb_cart_actions.row("Очистить корзину")  # Добавляем кнопку для очистки корзины
    kb_cart_actions.row("Назад")

    await message.answer(cart_message, reply_markup=kb_cart_actions)


# Обработчик для кнопки "Очистить корзину"
async def clear_cart(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_cart"] = {}  # Просто очищаем корзину в данных состояния

    await message.answer("Корзина успешно очищена.")
    await show_cart(message, state)  # Показываем обновленную корзину


# Добавьте этот обработчик в вашем модуле
@dp.message_handler(lambda message: message.text == "Очистить корзину", state="*")
async def handle_clear_cart(message: types.Message, state: FSMContext):
    await clear_cart(message, state)


# Handler for "Оформить заказ" button in the cart view
@dp.message_handler(lambda message: message.text == "Оформить заказ")
async def checkout_order(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_cart = data.get("user_cart", {})

    # Проверка наличия файла базы данных
    if not os.path.exists('users.sql'):
        await message.answer("Для оформления заказа, пожалуйста, зарегистрируйтесь.\nВведите /Регистрация")
        return  # Выход из функции

    # Retrieve user data from the database
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    user_id = message.from_user.id

    cur.execute("SELECT name, telephone, address FROM users WHERE user_id = ?", (user_id,))
    user_data = cur.fetchone()

    cur.close()
    conn.close()

    if user_data:
        user_name, user_telephone, user_add = user_data
        order_number = generate_order_number()  # Generate a unique order number

        cart_summary = "Детали заказа:\n"
        for product_name, quantity in user_cart.items():
            cart_summary += f"{product_name} - {quantity} - {order_number}\n"

        order_message = (
            f"Подтвердите Ваш заказ:\n"
            f"Заказчик: {user_name}\n"
            f"Телефон: {user_telephone}\n"
            f"Адрес: {user_add}\n\n"
            f"{cart_summary}"
        )

        kb_confirm_order = ReplyKeyboardMarkup(resize_keyboard=True)
        kb_confirm_order.row("Подтвердить")
        kb_confirm_order.row("Отмена")

        # await Registration.address.set()
        await state.update_data(user_data=user_data)
        await state.update_data(cart_summary=cart_summary)

        await message.answer(order_message, reply_markup=kb_confirm_order)
    else:
        await message.answer("Для оформления заказа, пожалуйста, зарегистрируйтесь.\nВведите /Регистрация")


# Handler for the "Отмена" button during order checkout
@dp.message_handler(lambda message: message.text == "Отмена")
async def cancel_order(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_cart"] = {}  # Очищаем корзину

    await message.answer("Заказ отменен. Корзина очищена.")
    await command_start(message)  # Вызываем обработчик /start для отображения главного меню


@dp.message_handler(lambda message: message.text == "Подтвердить")
async def confirm_order(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        user_data = data['user_data']
        cart_summary = data['cart_summary']
        user_cart = data.get('user_cart', {})

    # Compose the order confirmation message
    order_confirmation_message = (
        f"Ваш заказ подтвержден:\n"
        f"Заказчик: {user_data[0]}\n"
        f"Телефон: {user_data[1]}\n"
        f"Адрес: {user_data[2]}\n\n"
        f"{cart_summary}\n"
        "Спасибо за заказ!"
    )

    # Calculate total price
    db_connection = sqlite3.connect('online_shop.db')
    total_quantity, total_price = calculate_cart_total(user_cart, db_connection)
    db_connection.close()

    # Save the order in the orders table and update the status
    conn = sqlite3.connect('online_shop.db')
    cur = conn.cursor()

    # user_id = message.from_user.id
    # Extract order_number from cart_summary
    order_number = None
    if user_cart:
        print(user_cart)
        # Extract order_number from the first product entry in cart_summary
        order_number = user_cart[list(user_cart.keys())[0]].get('order_number', None)

    if order_number is None:
        await bot.send_message(callback_query.from_user.id, "Failed to retrieve order number. Please contact support.")
        return

    order_summary = f"Заказ #{order_number}\n{cart_summary}\nОбщая сумма: {total_price} руб."

    cur.execute("INSERT INTO orders (order_number, order_summary, status) VALUES (?, ?, ?)",
                (order_number, order_summary, "подтвержден"))  # Установка статуса на "подтвержден"
    conn.commit()

    cur.close()
    conn.close()

    # Create a keyboard for payment
    kb_payment = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Оплатить", callback_data="оплатить")
    )

    # Send the order confirmation message with payment button
    await bot.send_message(callback_query.from_user.id, order_confirmation_message, reply_markup=kb_payment)
    # Remove the InlineKeyboardMarkup
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Ваш заказ подтвержден. Спасибо за заказ!")

    # Clear the user's cart and other data
    await state.update_data(user_cart={})
    await state.reset_state()


# Function to generate a unique order identifier
def generate_order_number():
    return str(int(time.time()))  # Just a simple example using timestamp


@dp.callback_query_handler(lambda query: query.data == 'оплатить')
async def process_payment(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        user_cart = data.get('user_cart', {})

        # Calculate total price
        db_connection = sqlite3.connect('online_shop.db')
        total_quantity, total_price = calculate_cart_total(user_cart, db_connection)
        db_connection.close()

        # Извлекаем product_name из корзины или заказа
        product_name = "Ваш продукт"  # По умолчанию

        if user_cart:
            # Если корзина не пуста, берем первый продукт из неё
            product_name = list(user_cart.keys())[0]  # Получаем первый ключ из словаря корзины

        await bot.send_invoice(
            chat_id=callback_query.from_user.id,
            title=f'Покупка товара - {product_name}',
            description="Оплата за покупку в нашем магазине",
            payload=f'buy_product {product_name}',
            provider_token=PAYMENT_TOKEN,
            currency='RUB',
            prices=[LabeledPrice(label=product_name, amount=int(total_price) * 100)],
            start_parameter='buy_product',
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('Купить', pay=True)
            )
        )


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Функция для извлечения номера заказа из строки заказа
def extract_order_number(order_summary):
    # Пример: "Заказ #12345\n..."
    order_number_start = order_summary.find("#") + 1
    order_number_end = order_summary.find("\n", order_number_start)
    order_number = order_summary[order_number_start:order_number_end]
    return order_number


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_data = data.get('user_data')
        cart_summary = data.get('cart_summary')

    if user_data:
        user_name, user_telephone, user_add = user_data

        # Prepare the order confirmation message
        order_confirmation_message = (
            f"Ваш заказ подтвержден:\n"
            f"Заказчик: {user_name}\n"
            f"Телефон: {user_telephone}\n"
            f"Адрес: {user_add}\n\n"
            f"{cart_summary}\n"
            "Спасибо за заказ!"
        )

        # Update the order status to "оплачен" in the database
        conn = sqlite3.connect('online_shop.db')
        cur = conn.cursor()

        order_number = extract_order_number(cart_summary)  # Extract order number from summary
        print(order_number)

        cur.execute("UPDATE orders SET status = 'оплачен' WHERE order_number = ?", (order_number,))
        conn.commit()

        cur.close()
        conn.close()

        # Send the order confirmation message to the user
        await message.answer(order_confirmation_message)

        # Send the order confirmation message to the group administrator
        await bot.send_message(GROUP_ADMIN_ID, order_confirmation_message)

        # Clear the user's cart and update the state
        async with state.proxy() as data:
            data["user_cart"] = {}  # Clear the cart
    else:
        user_username = message.from_user.username
        user_id = message.from_user.id

        # Form the user mention using username or user ID
        if user_username:
            user_mention = f"@{user_username}"
        else:
            user_mention = f"[Пользователь](tg://user?id={user_id})"

        # Get the purchased product name from the user_purchases dictionary
        if user_id in user_purchases:
            product_name = user_purchases[user_id]

            # Send a message to the group administrator with the user's mention and the product name
            admin_notification = f"Пользователь {user_mention} совершил оплату и купил товар: {product_name}"
            await bot.send_message(GROUP_ADMIN_ID, admin_notification)

            # Remove the user's entry from the user_purchases dictionary
            del user_purchases[user_id]

            await state.finish()
        else:
            await message.answer("Не удалось определить купленный товар. Обратитесь к администратору.")


# Handler for "Мои заказы" button in the cart view
@dp.message_handler(lambda message: message.text == "Мои заказы")
async def show_my_orders(message: types.Message):
    conn = sqlite3.connect('online_shop.db')
    cur = conn.cursor()

    user_id = message.from_user.id

    # Fetch the user's orders with order numbers, summaries, and statuses from the database
    cur.execute("SELECT order_number, order_summary, status FROM orders WHERE user_id = ?", (user_id,))
    orders = cur.fetchall()

    cur.close()
    conn.close()

    if orders:
        orders_list = "\n".join([f"{order[1]} (Статус: {order[2]})" for order in orders])
        orders_message = f"Ваши заказы:\n{orders_list}"
    else:
        orders_message = "У вас пока нет заказов."

    await message.answer(orders_message)


# Handler to navigate back from the cart view
@dp.message_handler(lambda message: message.text == "Назад")
async def go_back_to_main_menu(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=kb_client)


# This dictionary will store user IDs and their purchased products
user_purchases = {}


# Handler for the "Buy" button
@dp.callback_query_handler(lambda query: query.data.startswith('купить_'))
async def buy_product(callback_query: types.CallbackQuery):
    product_name = callback_query.data[7:]  # Extract the product name from the callback data

    # Retrieve the product details from the database based on the product name
    product = await sqlite_db.get_product_by_name(product_name)

    if product:
        photo, name, description, price = product

        try:
            # Convert the price to a valid integer by first converting it to a float and then to an integer
            price_in_rubles = int(float(price) * 100)
        except ValueError:
            # If the price is not a valid float, handle the error gracefully
            await bot.send_message(callback_query.from_user.id, "Invalid product price. Please contact support.")
            return

        # Create an invoice for the product purchase
        await bot.send_invoice(callback_query.from_user.id,
                               title=f'Покупка товара - {name}',
                               description=description,
                               payload='buy_product',
                               provider_token=PAYMENT_TOKEN,
                               currency='RUB',
                               prices=[types.LabeledPrice(label=name, amount=price_in_rubles)],
                               start_parameter='buy_product',  # Unique parameter for deep linking
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton('Купить', pay=True)
                               )
                               )

        # Store the purchased product's name along with the user ID
        user_id = callback_query.from_user.id
        user_purchases[user_id] = product_name

    else:
        await bot.send_message(callback_query.from_user.id, "Product not found!")


# Handler for "Мои заказы" button in main_menu
@dp.message_handler(commands="Заказы")
async def show_orders(message: types.Message):
    conn = sqlite3.connect('online_shop.db')
    cur = conn.cursor()

    user_id = message.from_user.id

    # Fetch the user's orders with order numbers, summaries, and statuses from the database
    cur.execute("SELECT order_number, order_summary, status FROM orders WHERE user_id = ?", (user_id,))
    orders = cur.fetchall()

    cur.close()
    conn.close()

    if orders:
        orders_list = "\n".join([f"{order[1]} (Статус: {order[2]})" for order in orders])
        orders_message = f"Ваши заказы:\n{orders_list}"
    else:
        orders_message = "Еще нет заказов."

    await message.answer(orders_message)


# Handler for the "Help" button
async def help_command(message: types.Message):
    await message.answer("Помощь по использованию бота:\n"
                         "1. Команда /start - запуск бота\n"
                         "2. Команда '/help' - отображение справочной информации\n"
                         "3. Команда 'Доставка' - информация о доставке\n"
                         "4. Команда 'Регистрация' - регистрация новых пользователей\n"
                         "5. Команда 'Оплата' - информация об оплате\n"
                         "6. Команда 'Каталог' - просмотр каталога товаров"
                         )


def register_handlers_client(dispatcher: Dispatcher):
    dispatcher.register_message_handler(command_start, commands=['start'])
    dispatcher.register_message_handler(shop_information, commands=['Доставка'])
    dispatcher.register_message_handler(shop_menu_command, commands=['Каталог'])
    dispatcher.register_message_handler(help_command, commands=['help', 'Помощь'])
    dispatcher.register_message_handler(show_cart, commands=['Корзина'])
