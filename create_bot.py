from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()

# Get the token from the environment variables
telegram_token = os.getenv("key")

storage = MemoryStorage()

bot = Bot(telegram_token)
dp = Dispatcher(bot, storage=storage)
