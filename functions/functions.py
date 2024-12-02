from telegram import Update
from telegram.ext import ContextTypes
from database.database import ensure_user_exists, save_transaction, update_balance, get_balance
import sqlite3
import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    ensure_user_exists(user_id, username)
    await update.message.reply_text("Ласкаво просимо до фінансового менеджера !"
                                    "/help щоб дізнатися можливості бота")

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Використання: /add_income <сума> <категорія>")
            return

        amount = float(args[0])
        category = ' '.join(args[1:])

        save_transaction(user_id, "income", category, amount)
        update_balance(user_id, amount, "income")

        await update.message.reply_text(f"Доход {amount} додано до категорії '{category}'.")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Використання: /add_expense <сума> <категорія>")
            return

        amount = float(args[0])
        category = ' '.join(args[1:])

        save_transaction(user_id, "expense", category, amount)
        update_balance(user_id, amount, "expense")

        await update.message.reply_text(f"Витрату {amount} додано до категорії '{category}'.")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_balance = get_balance(user_id)
    await update.message.reply_text(f"Ваш поточний баланс: {current_balance}")

# Команда для встановлення валюти
async def set_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if len(context.args) != 1:
        await update.message.reply_text("Використання: /set_currency <валюта>")
        return

    currency = context.args[0].upper()
    try:
        with sqlite3.connect("database/finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET currency = ? WHERE user_id = ?", (currency, user_id))
            conn.commit()
        await update.message.reply_text(f"Валюта встановлена: {currency}")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

# Команда для налаштування категорій
async def set_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if len(args) < 2:
        await update.message.reply_text("Використання: /set_categories <тип> <категорія1> <категорія2> ...")
        return

    category_type = args[0]
    categories = args[1:]

    if category_type not in ["income", "expense"]:
        await update.message.reply_text("Тип має бути 'income' або 'expense'.")
        return

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    try:
        for category in categories:
            cursor.execute("""
            INSERT INTO categories (user_id, type, name)
            VALUES (?, ?, ?)
            """, (user_id, category_type, category))
        conn.commit()

        await update.message.reply_text(f"Категорії оновлено: {', '.join(categories)}")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")
    finally:
        conn.close()
# Періодичні платежі
async def add_recurring_payment(update, context):
    user_id = update.message.from_user.id
    if len(context.args) < 4:
        update.message.reply_text("Використання: /add_recurring_payment <сума> <категорія> <тип> <період (дні)>")
        return

    amount = float(context.args[0])
    category = context.args[1]
    payment_type = context.args[2].lower()
    period = int(context.args[3])

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recurring_payments (user_id, amount, category, type, period, last_added)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, amount, category, payment_type, period, datetime.date.today()))
    conn.commit()
    conn.close()
    await update.message.reply_text("Періодичний платіж додано!")



# Фінансові цілі
async def set_goal(update, context):
    user_id = update.message.from_user.id
    if len(context.args) < 3:
        await update.message.reply_text("Використання: /set_goal <сума> <термін (дата у форматі YYYY-MM-DD)> <опис>")
        return

    amount = float(context.args[0])
    target_date = context.args[1]
    description = " ".join(context.args[2:])

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO goals (user_id, amount, target_date, description, progress)
        VALUES (?, ?, ?, ?, 0)
    """, (user_id, amount, target_date, description))
    conn.commit()
    conn.close()
    await update.message.reply_text("Фінансова ціль додана!")


async def track_goal(update, context):
    user_id = update.message.from_user.id

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT description, amount, progress, target_date 
        FROM goals WHERE user_id = ?
    """, (user_id,))
    goals = cursor.fetchall()
    conn.close()

    if not goals:
        update.message.reply_text("У вас немає фінансових цілей.")
        return

    response = "Ваші цілі:\n"
    for goal in goals:
        description, amount, progress, target_date = goal
        response += f"- {description}: {progress}/{amount} до {target_date}\n"
    await update.message.reply_text(response)

# Прогнозування витрат
async def forecast(update, context):
    user_id = update.message.from_user.id

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(amount) FROM transactions
        WHERE user_id = ? AND type = 'expense'
    """, (user_id,))
    avg_expense = cursor.fetchone()[0] or 0
    conn.close()

    await update.message.reply_text(f"Середні витрати на основі даних: {avg_expense:.2f}")
