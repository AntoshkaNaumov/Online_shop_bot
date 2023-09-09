from aiogram import types, Dispatcher
from create_bot import dp, bot
import json
from config import PAYMENT_TOKEN, secret_key


# @dp.message_handler(commands=['invoice'])  # подключение системы оплаты к боту
async def invoice_test(message: types.Message):
    await bot.send_invoice(message.chat.id, 'Покупка товара',
    'Покупка нашего лучшего товара', 'invoice', secret_key,
    'RUB', [types.LabeledPrice('Покупка товара', 500 * 100)])


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(message: types.Message):
    await message.answer(f'Success: {message.successful_payment.order_info}')


def register_handlers_payment(dp: Dispatcher):
    dp.register_message_handler(invoice_test, commands=['invoice'])
