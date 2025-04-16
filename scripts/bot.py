# bot.py
import logging
import asyncio
import sys, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Добавляем корень проекта в sys.path для доступа к config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import TELEGRAM_TOKEN
from adaptive_threshold import AdaptiveThreshold
from binance_data import get_recent_price_changes
from movement_detector import is_sharp_movement

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Временное хранилище выбранной пары по user_id
user_pairs = {}

# Модель адаптивного порога
threshold_model = AdaptiveThreshold()

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Я бот анализа крипторынка. Доступные команды: /help /status_threshold /setpair")

@dp.message(F.text == "/help")
async def cmd_help(message: types.Message):
    await message.answer("🛠 Команды:\n/start — приветствие\n/status_threshold — текущие пороги движения\n/setpair — установить валютную пару")

@dp.message(F.text.startswith("/setpair"))
async def cmd_setpair(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("⚠️ Используй формат: /setpair BTCUSDT")
        return

    pair = parts[1].upper()
    user_id = message.from_user.id
    user_pairs[user_id] = pair

    await message.answer(f"✅ Валютная пара установлена: {pair}")

@dp.message(F.text == "/status_threshold")
async def cmd_status_threshold(message: types.Message):
    user_id = message.from_user.id
    pair = user_pairs.get(user_id, "BTCUSDT")  # по умолчанию BTCUSDT

    price_changes, volumes = get_recent_price_changes(pair=pair)

    # Обновляем модель порогов
    if price_changes:
        threshold_model.update(pair, price_changes[-1])

    thresholds = {
        'price_speed': threshold_model.get_threshold(pair),
        'spoofing': sum(volumes) * 0.01 if volumes else 0.01
    }

    sharp = is_sharp_movement(pair, price_changes)
    movement_status = "📈 Обнаружено резкое движение!" if sharp else "📉 Резких движений не зафиксировано."

    text = f"📊 Пороговые значения для {pair}:\n"
    text += f"💹 Скорость цены: {thresholds['price_speed']:.5f}\n"
    text += f"🧊 Spoofing: {thresholds['spoofing']:.5f}\n"
    text += f"\n{movement_status}"

    await message.answer(text)

@dp.message()
async def log_all_messages(message: types.Message):
    print(f"[DEBUG] Получено сообщение: {message.text}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
