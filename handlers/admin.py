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
# @dp.message_handler(comands='Загрузить', state=None)
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


@dp.message_handler(commands='Удалить')
async def delete_item(message: types.Message):
    if message.from_user.id == ID:
        read = await sqlite_db.sql_read2()
        for ret in read:
            await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание: {ret[2]}\nЦена {ret[-1]}')
            await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().\
                add(InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}')))


@dp.message_handler(commands='Просмотр')
async def view_confirmed_orders(message: types.Message):

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


@dp.message_handler(commands='Загрузка')
async def mailing_list_download(message: types.Message):
    if message.from_user.id == ID:
        # Connect to the SQLite database
        conn = sqlite3.connect('users.sql')
        cur = conn.cursor()

        # Retrieve user IDs from the database
        try:
            cur.execute('SELECT user_id FROM users')
            user_ids = [row[0] for row in cur.fetchall()]
        except Exception as e:
            await message.answer("Failed to retrieve user IDs from the database. Please try again later.")
            return
        finally:
            # Close the database connection
            conn.close()

        # Message content that you want to send
        message_content = "Hello, this is an important update for our users."

        # Loop through user IDs and send the message
        for user_id in user_ids:
            try:
                await bot.send_message(user_id, message_content)
            except Exception as e:
                # Handle any exceptions that might occur while sending messages
                print(f"Failed to send message to user {user_id}: {e}")

        await message.answer("Message sent to the users in the mailing list.")
    else:
        await message.answer("You do not have the necessary permissions for this command.")


# Регистрирует хендлеры
def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=['Загрузить'], state=None)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(make_changes_command, commands=['moderator'], is_chat_admin=True)
    dp.register_message_handler(start_mark_delivered, commands='mark_delivered')
    dp.register_message_handler(process_order_number, state=MarkDelivered.waiting_for_order_number)
