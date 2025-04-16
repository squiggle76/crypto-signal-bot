from aiogram import Bot
from config.config import TELEGRAM_TOKEN
import asyncio

bot = Bot(token=TELEGRAM_TOKEN)

async def clear():
    result = await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook удалён:", result)

asyncio.run(clear())
