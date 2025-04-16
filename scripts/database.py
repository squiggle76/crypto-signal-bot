import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import psycopg2
from psycopg2 import sql
import config.config as db_config

# Подключение к базе данных PostgreSQL
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def connect_db():
    return psycopg2.connect(
        dbname=db_config.DB_NAME,
        user=db_config.DB_USER,
        password=db_config.DB_PASSWORD,
        host=db_config.DB_HOST,
        port=db_config.DB_PORT,
        sslmode="require"
    )

def create_tables():
    """Создает таблицы, если они не существуют."""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS price_history (
            id SERIAL PRIMARY KEY,
            pair TEXT NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            volume DOUBLE PRECISION NOT NULL,
            spread DOUBLE PRECISION,
            price_change DOUBLE PRECISION,
            avg_volume_1m DOUBLE PRECISION,
            futures_ratio DOUBLE PRECISION,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        DROP TABLE IF EXISTS market_events;

        CREATE TABLE IF NOT EXISTS market_events (
            id SERIAL PRIMARY KEY,
            pair TEXT NOT NULL,
            event_type TEXT NOT NULL,
            price_change DOUBLE PRECISION,
            price_before DOUBLE PRECISION,
            price_after DOUBLE PRECISION,
            direction TEXT,
            threshold_used DOUBLE PRECISION,
            spread DOUBLE PRECISION,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS order_book_snapshots (
            id SERIAL PRIMARY KEY,
            pair TEXT NOT NULL,
            bid_price DOUBLE PRECISION,
            ask_price DOUBLE PRECISION,
            spread DOUBLE PRECISION,
            top_10_liquidity DOUBLE PRECISION,
            iceberg_orders DOUBLE PRECISION,
            bid_volume DOUBLE PRECISION,
            ask_volume DOUBLE PRECISION,
            order_changes_3s DOUBLE PRECISION,
            avg_order_size DOUBLE PRECISION,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS liquidations (
            id SERIAL PRIMARY KEY,
            pair TEXT NOT NULL,
            side TEXT NOT NULL,
            amount DOUBLE PRECISION NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            total_liquidations_1m DOUBLE PRECISION,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        );
        """
    ]

    conn = connect_db()
    cursor = conn.cursor()
    for query in queries:
        cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Таблицы успешно созданы (если их не было)")

def log_event_to_db(pair, price_before, price_after, change_percent, bid, ask, threshold_used):
    """Запись резкого движения в таблицу market_events."""
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO market_events (
            pair,
            event_type,
            price_change,
            price_before,
            price_after,
            direction,
            threshold_used,
            spread,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW());
    """

    spread = abs(ask - bid) if ask and bid else None
    direction = "up" if price_after > price_before else "down"

    cursor.execute(query, (
        pair,
        "price_spike",
        round(change_percent, 5),
        round(price_before, 5),
        round(price_after, 5),
        direction,
        threshold_used,
        spread
    ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"📝 Скачок записан в базу: {pair} {change_percent:.2f}%")

if __name__ == "__main__":
    create_tables()