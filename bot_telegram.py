from aiogram.utils import executor
from create_bot import dp
from data_base import sqlite_db
import logging
from handlers import client, admin, other, payment


async def on_startup(_):
    print('Бот вышел в онлайн')
    sqlite_db.sql_start()


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
payment.register_handlers_payment(dp)
other.register_handlers_other(dp)

# Set up logging
logging.basicConfig(level=logging.DEBUG)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
# webhook для загрузки бота на сервере
