import sqlite3
from datetime import datetime

def initialize_database():
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    # Таблиця користувачів
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            budget REAL DEFAULT 0,
            currency TEXT DEFAULT 'USD'
        )
    """)

    # Таблиця для категорій
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT CHECK(type IN ('income', 'expense')),
        name TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    # Таблиця транзакцій
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
    # Таблиця періодичних платежів
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recurring_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            type TEXT,  -- income або expense
            period INTEGER, -- в днях
            last_added TEXT
        )
    """)

    # Таблиця фінансових цілей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            target_date TEXT,
            description TEXT,
            progress REAL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def ensure_user_exists(user_id, username):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username)
        VALUES (?, ?)
    """, (user_id, username))

    conn.commit()
    conn.close()

def save_transaction(user_id, transaction_type, category, amount):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (user_id, type, category, amount, date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, transaction_type, category, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

def update_balance(user_id, amount, transaction_type):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    if transaction_type == "income":
        cursor.execute("""
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        """, (amount, user_id))
    elif transaction_type == "expense":
        cursor.execute("""
            UPDATE users SET balance = balance - ? WHERE user_id = ?
        """, (amount, user_id))

    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT balance FROM users WHERE user_id = ?
    """, (user_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0

# Отримання транзакцій за заданий період
def get_transactions_by_period(user_id, start_date=None):
    conn = sqlite3.connect("database/finance.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if start_date:
        query = """
            SELECT amount, type, category, date 
            FROM transactions 
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC
        """
        cursor.execute(query, (user_id, start_date.strftime("%Y-%m-%d")))
    else:
        query = """
            SELECT amount, type, category, date 
            FROM transactions 
            WHERE user_id = ?
            ORDER BY date DESC
        """
        cursor.execute(query, (user_id,))

    transactions = cursor.fetchall()
    conn.close()
    return transactions


# Збереження бюджету
def set_budget(user_id, budget):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users 
        SET budget = ? 
        WHERE user_id = ?
    """, (budget, user_id))

    conn.commit()
    conn.close()

# Отримання бюджету користувача
def get_budget(user_id):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT budget 
        FROM users 
        WHERE user_id = ?
    """, (user_id,))
    budget = cursor.fetchone()
    conn.close()
    return budget[0] if budget else 0


def get_total_expenses(user_id):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
    """, (user_id,))

    total_expenses = cursor.fetchone()[0]
    conn.close()
    return total_expenses or 0