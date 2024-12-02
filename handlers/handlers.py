
from datetime import datetime, timedelta
from database.database import get_transactions_by_period,set_budget, save_transaction, get_budget, get_total_expenses
from telegram import Update
from telegram.ext import ContextTypes


async def summary(update, context):
    try:
        # Отримуємо аргумент (період)
        args = context.args
        if not args:
            await update.message.reply_text("Використання: /summary <day|week|month|all>")
            return

        period = args[0].lower()
        user_id = update.message.from_user.id

        # Визначення дат для фільтрації
        today = datetime.now()
        if period == "day":
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = today - timedelta(days=today.weekday())
        elif period == "month":
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "all":
            start_date = None  # Усі дані
        else:
            await update.message.reply_text("Невірний період. Використовуйте: day, week, month або all.")
            return

        # Отримуємо дані з бази
        transactions = get_transactions_by_period(user_id, start_date)

        if not transactions:
            await update.message.reply_text("Немає транзакцій за обраний період.")
            return

        # Форматування виводу
        total_income = 0
        total_expense = 0
        result = "📊 <b>Звіт за період:</b>\n"

        for t in transactions:
            amount = t['amount']
            category = t['category']
            t_type = t['type']
            date = t['date']

            if t_type == 'income':
                total_income += amount
                t_type_display = "➕ Дохід"
            else:
                total_expense += amount
                t_type_display = "➖ Витрата"

            result += f"{date}: {t_type_display} {amount} ({category})\n"

        result += f"\n<b>Загальна сума:</b>\n"
        result += f"Дохід: {total_income}\n"
        result += f"Витрати: {total_expense}\n"

        await update.message.reply_text(result, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")


async def set_budget_handler(update, context):
    user_id = update.message.from_user.id
    try:
        budget = float(context.args[0])
        set_budget(user_id, budget)

        total_expenses = get_total_expenses(user_id)
        response = f"✅ Бюджет встановлено: {budget}"
        if total_expenses > budget:
            response += f"\n⚠️ Увага! Ваші витрати ({total_expenses:.2f}) вже перевищують новий бюджет!"

        await update.message.reply_text(response)
    except (IndexError, ValueError):
        await update.message.reply_text("Введіть коректну суму: /set_budget <сума>")


async def compare(update, context):
    user_id = update.message.from_user.id
    try:
        period1 = context.args[0]
        period2 = context.args[1]

        def get_period_dates(period):
            today = datetime.now()
            if period == "day":
                return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
            elif period == "week":
                start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
                return start_date, today.strftime('%Y-%m-%d')
            elif period == "month":
                start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
                return start_date, today.strftime('%Y-%m-%d')
            else:
                raise ValueError("Невідомий період.")

        start_date1, end_date1 = get_period_dates(period1)
        start_date2, end_date2 = get_period_dates(period2)

        transactions1 = get_transactions_by_period(user_id, start_date1, end_date1)
        transactions2 = get_transactions_by_period(user_id, start_date2, end_date2)

        def calculate_totals(transactions):
            income, expenses = 0, 0
            for t_type, _, amount in transactions:
                if t_type == "income":
                    income += amount
                elif t_type == "expense":
                    expenses += amount
            return income, expenses

        income1, expenses1 = calculate_totals(transactions1)
        income2, expenses2 = calculate_totals(transactions2)

        report = f"📊 **Порівняння фінансових результатів:**\n\n"
        report += f"Період 1: {start_date1} - {end_date1}\n"
        report += f"  - Доходи: {income1}\n"
        report += f"  - Витрати: {expenses1}\n\n"
        report += f"Період 2: {start_date2} - {end_date2}\n"
        report += f"  - Доходи: {income2}\n"
        report += f"  - Витрати: {expenses2}\n"

        await update.message.reply_text(report, parse_mode="Markdown")
    except (IndexError, ValueError):
        await update.message.reply_text("Використовуйте: /compare <період1> <період2> (day/week/month)")

async def add_expense(update, context):
    user_id = update.message.from_user.id
    try:
        amount = float(context.args[0])
        category = " ".join(context.args[1:])
        if not category:
            raise ValueError("Категорія не вказана.")

        # Додавання транзакції
        save_transaction(user_id, "expense", category, amount)

        # Перевірка бюджету
        budget = get_budget(user_id)
        total_expenses = get_total_expenses(user_id)

        response = f"✅ Витрата додана: {amount} ({category})"
        if budget > 0:
            remaining_budget = budget - total_expenses
            if remaining_budget <= 0:
                response += f"\n⚠️ Ви перевищили свій бюджет на {abs(remaining_budget):.2f}!"
            elif remaining_budget <= budget * 0.25:
                response += f"\n⚠️ Увага! Ви наближаєтеся до використання бюджету. Залишилося: {remaining_budget:.2f}"

        await update.message.reply_text(response)
    except (IndexError, ValueError):
        await update.message.reply_text("Використання: /add_expense <сума> <категорія>")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
<b>Доступні команди:</b>
1. <b>/add_income [сума] [категорія]</b> — Додати дохід. 
   Приклад: <code>/add_income 1000 Зарплата</code>
2. <b>/add_expense [сума] [категорія]</b> — Додати витрату.
   Приклад: <code>/add_expense 500 Продукти</code>
3. <b>/balance</b> — Відобразити поточний баланс.
4. <b>/summary [період]</b> — Отримати звіт за період.
   Приклад: <code>/summary тиждень</code>
5. <b>/set_currency [валюта]</b> — Встановити валюту за замовчуванням.
   Приклад: <code>/set_currency USD</code>
6. <b>/set_categories [тип] [категорії]</b> — Налаштувати категорії доходів або витрат.
   Приклад: <code>/set_categories income Зарплата Інвестиції</code>
7. <b>/add_recurring_payment [сума] [категорія] [тип] [період]</b> — Додати періодичний платіж.
   Приклад: <code>/add_recurring_payment 100 Продукти expense 30</code>
8. <b>/set_goal [сума] [дата] [опис]</b> — Додати фінансову ціль.
   Приклад: <code>/set_goal 5000 2024-12-31 Купівля велосипеда</code>
9. <b>/track_goal</b> — Перегляд прогресу фінансових цілей.
10. <b>/forecast</b> — Прогноз витрат на основі історії.
11. <b>/help</b> — Перелік усіх команд із поясненням.

<b>Додаткова інформація:</b>
- Команди можна вводити в будь-якому порядку.
- Категорії повинні бути заздалегідь налаштовані для використання.
- Періоди у командах: <code>день</code>, <code>тиждень</code>, <code>місяць</code>.
"""
    await update.message.reply_text(help_text, parse_mode='HTML')