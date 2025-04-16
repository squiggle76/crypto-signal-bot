# debug.py
import asyncio
from aiogram import Bot
from config.config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)

async def test():
    me = await bot.get_me()
    print("✅ Токен рабочий, бот подключен как:", me.username)

asyncio.run(test())
