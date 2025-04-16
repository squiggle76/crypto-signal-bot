import psycopg2

# 🔹 ЗАМЕНИ ЭТУ СТРОКУ на свою строку подключения из Neon.tech
DATABASE_URL = "postgresql://neondb_owner:npg_A8UYieglXhJ9@ep-tiny-wildflower-a8bf72pn-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

def connect_db():
    """Подключение к базе данных."""
    return psycopg2.connect(DATABASE_URL)

def create_table():
    """Создаём таблицу в PostgreSQL"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_events (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        symbol TEXT,
        event_type TEXT,
        price REAL,
        volume REAL,
        price_change_5min REAL,
        spoofing_volume REAL,
        spoofing_count INT DEFAULT 0,
        price_30min_ago REAL,
        volume_30min_ago REAL,
        spread_30min_ago REAL,
        last_spoofing_count INT DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()
    print("✅ Таблица создана!")

def save_market_event(symbol, event_type, price, volume, price_change_5min, spoofing_volume=None, spoofing_count=0):
    """Сохраняем событие в базе данных с анализом предшествующего рынка."""
    conn = connect_db()
    cursor = conn.cursor()

    # Запрашиваем данные за 30 минут до события
    cursor.execute("""
        SELECT price, volume, spread, COUNT(*) 
        FROM market_events 
        WHERE symbol = %s AND timestamp >= NOW() - INTERVAL '30 minutes'
    """, (symbol,))
    row = cursor.fetchone()

    price_30min_ago = row[0] if row else None
    volume_30min_ago = row[1] if row else None
    spread_30min_ago = row[2] if row else None
    last_spoofing_count = row[3] if row else 0  # Количество Spoofing-ов за 30 минут

    # Записываем данные в базу
    cursor.execute("""
        INSERT INTO market_events 
        (symbol, event_type, price, volume, price_change_5min, spoofing_volume, spoofing_count,
         price_30min_ago, volume_30min_ago, spread_30min_ago, last_spoofing_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (symbol, event_type, price, volume, price_change_5min, spoofing_volume, spoofing_count,
          price_30min_ago, volume_30min_ago, spread_30min_ago, last_spoofing_count))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Событие {event_type} для {symbol} сохранено с анализом рынка!")

def get_all_events():
    """Получаем все события из базы данных."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM market_events;")
    events = cursor.fetchall()
    conn.close()
    return events

# ✅ Теперь код выполняется корректно
if __name__ == "__main__":
    create_table()  # Создаём таблицу при запуске
    print(get_all_events())  # Выведет все события из базы
    print("✅ Database script executed successfully!")
