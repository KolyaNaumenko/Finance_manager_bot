from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
import sqlite3
from datetime import datetime

# Функція для додавання транзакції
def add_transaction(user_id, transaction_type, amount, category):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (user_id, type, amount, category, date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, transaction_type, amount, category, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

# Команда для додавання доходу
def add_income(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) < 2:
            update.message.reply_text("Використання: /add_income <сума> <категорія>")
            return

        amount = float(args[0])
        category = ' '.join(args[1:])
        add_transaction(user_id, "income", amount, category)
        update.message.reply_text(f"Доход {amount} додано до категорії '{category}'.")
    except Exception as e:
        update.message.reply_text(f"Помилка: {e}")

# Команда для додавання витрати
def add_expense(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) < 2:
            update.message.reply_text("Використання: /add_expense <сума> <категорія>")
            return

        amount = float(args[0])
        category = ' '.join(args[1:])
        add_transaction(user_id, "expense", amount, category)
        update.message.reply_text(f"Витрату {amount} додано до категорії '{category}'.")
    except Exception as e:
        update.message.reply_text(f"Помилка: {e}")




def get_balance(user_id):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            (SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = ? AND type = 'income') -
            (SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = ? AND type = 'expense')
    """, (user_id, user_id))

    balance = cursor.fetchone()[0]
    conn.close()
    return balance

def balance(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        current_balance = get_balance(user_id)
        update.message.reply_text(f"Ваш поточний баланс: {current_balance}")
    except Exception as e:
        update.message.reply_text(f"Помилка: {e}")

def get_summary(user_id, period):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    query = """
        SELECT category, type, SUM(amount)
        FROM transactions
        WHERE user_id = ? AND date >= DATE('now', ?)
        GROUP BY category, type
    """
    cursor.execute(query, (user_id, period))
    summary = cursor.fetchall()
    conn.close()
    return summary

def summary(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) < 1:
            update.message.reply_text("Використання: /summary <період (day, week, month)>")
            return

        period = args[0]
        if period not in ['day', 'week', 'month']:
            update.message.reply_text("Період має бути одним з: day, week, month")
            return

        summary_data = get_summary(user_id, f"-{period}")
        if not summary_data:
            update.message.reply_text("Немає даних за вказаний період.")
            return

        message = "Фінансовий звіт:\n"
        for category, transaction_type, amount in summary_data:
            message += f"- {transaction_type.capitalize()} ({category}): {amount}\n"
        update.message.reply_text(message)
    except Exception as e:
        update.message.reply_text(f"Помилка: {e}")