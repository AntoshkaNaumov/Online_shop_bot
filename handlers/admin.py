from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram import types
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3


ID = None


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()


# Получаем ID текущего модератора
# dp.message_handler(commands=['moderator'], is_chat_admin=True)#, reply_markup-button_case_admin)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Что ты хочешь сделать???', reply_markup=admin_kb.button_case_admin)
    await message.delete()


# Начало загрузки диалога нового пуска меню
# @dp.message_handler(comands='Download', state=None)
async def cm_start(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin.photo.set()
        await message.reply('Загрузи фото')


# Ловим первый ответ и пишем в словарь
# @dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await message.reply("Теперь введи название")


# Ловим второй ответ
# @dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as date:
            date['name'] = message.text
        await FSMAdmin.next()
        await message.reply("Введи описание")


# Ловим третий ответ
# @dp.message_handler(state=FSMAdmin.description)
async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSMAdmin.next()
        await message.reply("Теперь укажи цену")


# Ловим последний ответ и используем полученные данные
# @dp.message_handler(state=FSMAdmin.price)
async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['price'] = float(message.text)

        await sqlite_db.sql_add_command(state)
        await state.finish()
        # Отправляем сообщение пользователю о успешном добавлении товара
        await message.answer("Товар успешно добавлен!")


# Выход из состояний
# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена.', show_alert=True)


@dp.message_handler(commands='Delete')
async def delete_item(message: types.Message):
    if message.from_user.id == ID:
        read = await sqlite_db.sql_read2()
        for ret in read:
            await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание: {ret[2]}\nЦена {ret[-1]}')
            await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().\
                add(InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}')))


#@dp.message_handler(commands='Confirmed Orders')
#async def view_confirmed_orders(message: types.Message):

    # Подключение к базе данных
#    conn = sqlite3.connect('online_shop.db')
#    cur = conn.cursor()

    # Выполнение SQL-запроса
#    cur.execute("SELECT * FROM orders WHERE status = 'подтвержден'")
#    confirmed_orders = cur.fetchall()

    # Закрытие соединения с базой данных
#    cur.close()
#    conn.close()

#    if confirmed_orders:
#        response = "Список подтвержденных заказов:\n"
#        for order in confirmed_orders:
#            response += f"Номер заказа #{order[2]}\nОписание: {order[3]}\n\nСтатус: {order[4]}\n\n"

#        await message.answer(response)
#    else:
#        await message.answer("Нет подтвержденных заказов.")


#@dp.message_handler(commands='Paid Orders')
#async def view_paid_orders(message: types.Message):

    # Подключение к базе данных
#    conn = sqlite3.connect('online_shop.db')
#    cur = conn.cursor()

    # Выполнение SQL-запроса
#    cur.execute("SELECT * FROM orders WHERE status = 'оплачен'")
#    confirmed_orders = cur.fetchall()

    # Закрытие соединения с базой данных
#    cur.close()
#    conn.close()

#    if confirmed_orders:
#        response = "Список оплаченных заказов:\n"
#        for order in confirmed_orders:
#            response += f"Номер заказа #{order[2]}\nОписание: {order[3]}\n\nСтатус: {order[4]}\n\n"

#        await message.answer(response)
#    else:
#        await message.answer("Нет оплаченных заказов.")


# Задаем состояния для ожидания номера заказа
class MarkDelivered(StatesGroup):
    waiting_for_order_number = State()


# Регистрируем хендлер для команды /mark_delivered
@dp.message_handler(commands=['mark_delivered'])
async def start_mark_delivered(message: types.Message):
    if message.from_user.id == ID:
        await message.answer("Введите номер заказа для пометки как 'доставлен':")
        await MarkDelivered.waiting_for_order_number.set()
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")


# Хендлер для обработки текстового сообщения (номера заказа)
@dp.message_handler(state=MarkDelivered.waiting_for_order_number)
async def process_order_number(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        try:
            order_number = int(message.text)
            # Подключение к базе данных
            conn = sqlite3.connect('online_shop.db')
            cur = conn.cursor()

            # Обновление статуса заказа в базе данных
            cur.execute("UPDATE orders SET status = 'доставлен' WHERE order_number = ?", (order_number,))
            conn.commit()

            # Закрытие соединения с базой данных
            cur.close()
            conn.close()

            await message.answer(f"Заказ #{order_number} помечен как 'доставлен'.")
        except ValueError:
            await message.answer("Введите корректный номер заказа.")
        await state.finish()
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")


class MailingState(StatesGroup):
    WaitingForMessage = State()
    WaitingForImage = State()


@dp.message_handler(commands='Newsletter')
async def start_mailing(message: types.Message):
    if message.from_user.id == ID:
        await MailingState.WaitingForMessage.set()
        await message.answer("Please enter the message you want to send to users.")
    else:
        await message.answer("You do not have the necessary permissions for this command.")


@dp.message_handler(state=MailingState.WaitingForMessage)
async def get_message_content(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message_content'] = message.text

    await MailingState.WaitingForImage.set()
    await message.answer("Now, please upload an image to include in the message.")


@dp.message_handler(content_types=types.ContentType.PHOTO, state=MailingState.WaitingForImage)
async def get_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['image_file_id'] = message.photo[-1].file_id

    await state.finish()
    await send_message_with_image_to_users(data['message_content'], data['image_file_id'])


async def send_message_with_image_to_users(message_content, image_file_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    # Retrieve user IDs from the database
    try:
        cur.execute('SELECT user_id FROM users')
        user_ids = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print("Failed to retrieve user IDs from the database.")
        return
    finally:
        # Close the database connection
        conn.close()

    # Loop through user IDs and send the message with image
    for user_id in user_ids:
        try:
            await bot.send_photo(user_id, photo=image_file_id, caption=message_content)
        except Exception as e:
            print(f"Failed to send message with image to user {user_id}: {e}")

    print("Message with image sent to the users in the mailing list.")


class SubmenuState(StatesGroup):
    WaitingForSubmenuChoice = State()


@dp.message_handler(commands='Orders')
async def show_orders_submenu(message: types.Message):
    if message.from_user.id == ID:
        await SubmenuState.WaitingForSubmenuChoice.set()
        await message.answer("Please choose an option:", reply_markup=admin_kb.submenu_keyboard)
    else:
        await message.answer("You do not have the necessary permissions for this command.")


@dp.message_handler(state=SubmenuState.WaitingForSubmenuChoice)
async def handle_submenu_choice(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        if message.text == 'Confirmed Orders':
            await message.answer("Displaying confirmed orders...")
            # Implement your logic to display confirmed orders here
            # Подключение к базе данных
            conn = sqlite3.connect('online_shop.db')
            cur = conn.cursor()

            # Выполнение SQL-запроса
            cur.execute("SELECT * FROM orders WHERE status = 'подтвержден'")
            confirmed_orders = cur.fetchall()

            # Закрытие соединения с базой данных
            cur.close()
            conn.close()

            if confirmed_orders:
                response = "Список подтвержденных заказов:\n"
                for order in confirmed_orders:
                    response += f"Номер заказа #{order[2]}\nОписание: {order[3]}\n\nСтатус: {order[4]}\n\n"

                await message.answer(response)
            else:
                await message.answer("Нет подтвержденных заказов.")

        elif message.text == 'Paid Orders':
            await message.answer("Displaying paid orders...")
            # Implement your logic to display paid orders here
            # Подключение к базе данных
            conn = sqlite3.connect('online_shop.db')
            cur = conn.cursor()

            # Выполнение SQL-запроса
            cur.execute("SELECT * FROM orders WHERE status = 'оплачен'")
            confirmed_orders = cur.fetchall()

            # Закрытие соединения с базой данных
            cur.close()
            conn.close()

            if confirmed_orders:
                response = "Список оплаченных заказов:\n"
                for order in confirmed_orders:
                    response += f"Номер заказа #{order[2]}\nОписание: {order[3]}\n\nСтатус: {order[4]}\n\n"

                await message.answer(response)
            else:
                await message.answer("Нет оплаченных заказов.")

        elif message.text == 'Back':
            await message.answer("Returning to main menu...", reply_markup=admin_kb.button_case_admin)
            await state.finish()

    else:
        await message.answer("You do not have the necessary permissions for this command.")


# Регистрирует хендлеры
def register_handlers_admin(dispatcher: Dispatcher):
    dispatcher.register_message_handler(cm_start, commands=['Download'], state=None)
    dispatcher.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    dispatcher.register_message_handler(load_name, state=FSMAdmin.name)
    dispatcher.register_message_handler(load_description, state=FSMAdmin.description)
    dispatcher.register_message_handler(load_price, state=FSMAdmin.price)
    dispatcher.register_message_handler(cancel_handler, state="*", commands='cancel')
    dispatcher.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), state="*")
    dispatcher.register_message_handler(make_changes_command, commands=['moderator'], is_chat_admin=True)
    dispatcher.register_message_handler(start_mark_delivered, commands='mark_delivered')
    dispatcher.register_message_handler(process_order_number, state=MarkDelivered.waiting_for_order_number)
    dispatcher.register_message_handler(start_mailing, commands='Newsletter')
    dispatcher.register_message_handler(get_message_content, state=MailingState.WaitingForMessage)
    dispatcher.register_message_handler(get_image, content_types=types.ContentType.PHOTO, state=MailingState.WaitingForImage)
