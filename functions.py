from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
import sqlite3
from datetime import datetime

# Асинхронна функція для додавання транзакції
async def add_transaction(user_id, transaction_type, amount, category):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (user_id, type, amount, category, date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, transaction_type, amount, category, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

# Команда для додавання доходу
async def add_income(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Використання: /add_income <сума> <категорія>")
            return

        amount = float(args[0])
        category = ' '.join(args[1:])
        await add_transaction(user_id, "income", amount, category)
        await update.message.reply_text(f"Доход {amount} додано до категорії '{category}'.")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

# Команда для додавання витрати
async def add_expense(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Використання: /add_expense <сума> <категорія>")
            return

        amount = float(args[0])
        category = ' '.join(args[1:])
        await add_transaction(user_id, "expense", amount, category)
        await update.message.reply_text(f"Витрату {amount} додано до категорії '{category}'.")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

# Команда для перегляду балансу
async def balance(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        conn = sqlite3.connect("database/finance.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                (SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = ? AND type = 'income') -
                (SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = ? AND type = 'expense')
        """, (user_id, user_id))

        current_balance = cursor.fetchone()[0]
        conn.close()
        await update.message.reply_text(f"Ваш поточний баланс: {current_balance}")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")


def ensure_user_exists(user_id, username):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username)
        VALUES (?, ?)
    """, (user_id, username))

    conn.commit()
    conn.close()