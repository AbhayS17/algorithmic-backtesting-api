# database.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("backtests.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            short_window INTEGER,
            long_window INTEGER,
            market_return REAL,
            strategy_return REAL
        )
    """)
    conn.commit()
    return conn, cursor