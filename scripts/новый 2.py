import time
import requests

# Список валютных пар для отслеживания
PAIRS = ["BTCUSDT", "TRUMPUSDT"]

# URL Binance API
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

# Порог резкого движения в процентах
THRESHOLD_PERCENT = 0.5  # 0.5% за 40 секунд

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
                
                # Храним не более 40 секунд данных (по 7 секунд за итерацию ~6 записей)
                if len(price_history[pair]) > 6:
                    price_history[pair].pop(0)
                
                # Проверяем резкое движение
                if len(price_history[pair]) == 6:
                    old_price = price_history[pair][0]  # Цена 40 секунд назад
                    change_percent = ((price - old_price) / old_price) * 100
                    
                    if abs(change_percent) >= THRESHOLD_PERCENT:
                        direction = "вверх" if change_percent > 0 else "вниз"
                        print(f"⚠️ Резкое движение! {pair} изменился на {change_percent:.2f}% за 40 секунд ({direction}).")
        
        print(f"Текущие цены: {prices}")
        time.sleep(7)