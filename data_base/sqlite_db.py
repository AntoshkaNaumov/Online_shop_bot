import sqlite3 as sq
from create_bot import bot


def sql_start():
    global base, cur
    base = sq.connect('online_shop.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS shop(img TEXT, name PRIMARY KEY, description TEXT, price TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS orders '
                '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'user_id INTEGER, '
                'order_number TEXT, '
                'order_summary TEXT, '
                'status TEXT DEFAULT "новый")')  # Добавляем столбец "status" с значением по умолчанию
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO shop VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(message):
    #products = []
    for ret in cur.execute('SELECT * FROM shop').fetchall():
        await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание: {ret[2]}\nЦена {ret[-1]}')
    #return products


async def sql_read2():
    return cur.execute('SELECT * FROM shop').fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM shop WHERE name == ?', (data,))
    base.commit()


async def get_product_by_name(product_name):
    products = await sql_read()
    for product in products:
        photo, name, description, price = product
        if name == product_name:
            return product
    return None
