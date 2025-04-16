import asyncio
import logging
import psycopg2
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils import executor

# Настройки бота
TOKEN = "7775976297:AAGXD9KqM_x9y4ITM8IroODuiJuwuHmvhAw"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключение к базе данных PostgreSQL
DATABASE_URL = "postgresql://neondb_owner:npg_A8UYieglXhJ9@ep-tiny-wildflower-a8bf72pn-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL)

def save_market_event(symbol, event_type, price, volume, price_change_5min):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO market_events (symbol, event_type, price, volume, price_change_5min)
    VALUES (%s, %s, %s, %s, %s);
    """, (symbol, event_type, price, volume, price_change_5min))
    conn.commit()
    conn.close()
    return f"✅ Событие {event_type} для {symbol} сохранено!"

# Уведомление в Telegram
async def send_alert(event_info):
    await bot.send_message(chat_id="YOUR_TELEGRAM_CHAT_ID", text=event_info)

def analyze_market_reaction(symbol, price, volume, event_type):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM market_events 
    WHERE symbol = %s 
    AND event_type = %s 
    AND ABS(price - %s) < 100 
    AND ABS(volume - %s) < 500000;
    """, (symbol, event_type, price, volume))
    events = cursor.fetchall()
    conn.close()
    if not events:
        return "Нет похожих случаев в истории."
    up_count = sum(1 for e in events if e[6] > 0)
    down_count = sum(1 for e in events if e[6] < 0)
    total = len(events)
    up_percent = round((up_count / total) * 100, 2)
    down_percent = round((down_count / total) * 100, 2)
    return f"📊 Анализ истории ({total} случаев): 🔼 {up_percent}% вверх, 🔽 {down_percent}% вниз"

@dp.message(Command("analyze"))
async def analyze_spoofing(message: Message):
    symbol = "BTC/USDT"
    price = 43700
    volume = 2500000
    analysis = analyze_market_reaction(symbol, price, volume, "Spoofing")
    await message.answer(analysis)

@dp.message(Command("spoof"))
async def report_spoofing(message: Message):
    result = save_market_event("BTC/USDT", "Spoofing", 43700, 2500000, 0.57)
    await send_alert(result)
    await message.answer(result)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)

