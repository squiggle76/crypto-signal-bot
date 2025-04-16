from database import log_event_to_db, connect_db  # подключаем базу
from adaptive_threshold import AdaptiveThreshold
import time
import requests
import sys
import os

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot import send_telegram_message
import config.config as config



# Список валютных пар для отслеживания
PAIRS = ["BTCUSDT", "TRUMPUSDT"]

# URL Binance API
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

# Порог резкого движения в процентах
THRESHOLD_PERCENT = 0.01  # например, 0.01% за 40 секунд

def get_price(pair):
    """Получает текущую цену указанной валютной пары."""
    try:
        response = requests.get(BINANCE_URL, params={"symbol": pair})
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f"Ошибка получения данных для {pair}: {e}")
        return None

if __name__ == "__main__":
    price_history = {pair: [] for pair in PAIRS}  # Храним историю цен
    
    while True:
        prices = {}
        for pair in PAIRS:
            price = get_price(pair)
            if price:
                prices[pair] = price
                price_history[pair].append(price)
                
                # Храним не более 40 секунд данных (~6 записей)
                if len(price_history[pair]) > 6:
                    price_history[pair].pop(0)
                
                # Проверяем резкое движение
                if len(price_history[pair]) == 6:
                    old_price = price_history[pair][0]
                    change_percent = ((price - old_price) / old_price) * 100
                    
                    if abs(change_percent) >= THRESHOLD_PERCENT:
                        message = (
                            f"⚠️ Резкое движение!\n"
                            f"Пара: {pair}\n"
                            f"Цена сейчас: {price:.2f} USDT\n"
                            f"Изменение: {change_percent:.2f}% за 40 секунд."
                        )

                        print(message)
                        send_telegram_message(message, chat_id=5155774697)

                        try:
                            orderbook = requests.get(
                                "https://api.binance.com/api/v3/ticker/bookTicker",
                                params={"symbol": pair}
                            ).json()
                            bid_price = float(orderbook["bidPrice"])
                            ask_price = float(orderbook["askPrice"])

                            log_event_to_db(
                                pair=pair,
                                price_before=old_price,
                                price_after=price,
                                change_percent=change_percent,
                                bid=bid_price,
                                ask=ask_price,
                                threshold_used=THRESHOLD_PERCENT
                            )

                            print("✅ Уведомление отправлено и событие записано.")

                        except Exception as e:
                            print(f"❌ Ошибка при записи в базу: {e}")

                                            
        
        # ⏱ Показываем текущие котировки каждые 7 секунд
        print(f"Текущие цены: {prices}")
        time.sleep(7)
