import sqlite3

def initialize_database():
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    # Таблиця для зберігання даних користувачів
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            budget REAL DEFAULT 0,
            currency TEXT DEFAULT 'USD'
        )
    """)

    # Таблиця для зберігання транзакцій
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            category TEXT,
            amount REAL,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    conn.close()