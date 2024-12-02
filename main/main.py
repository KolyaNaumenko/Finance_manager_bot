from telegram.ext import Application, CommandHandler
from functions.functions import start, add_income, add_expense, balance,set_currency,set_categories,add_recurring_payment,set_goal, track_goal, forecast
from database.database import initialize_database
from handlers.handlers import summary, set_budget_handler, compare,add_expense,help_command

# Ініціалізація бази даних
initialize_database()

# Створення бота
TOKEN = "7680334871:AAG9RI0Zr67_6Dom7fp7BY0nnwFK8kmIKMw"
app = Application.builder().token(TOKEN).build()

# Реєстрація команд
app.add_handler(CommandHandler("summary", summary))
app.add_handler(CommandHandler("set_budget", set_budget_handler))
app.add_handler(CommandHandler("compare", compare))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add_income", add_income))
app.add_handler(CommandHandler("add_expense", add_expense))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("set_currency", set_currency))
app.add_handler(CommandHandler("set_categories", set_categories))
app.add_handler(CommandHandler("add_recurring_payment", add_recurring_payment))
app.add_handler(CommandHandler("set_goal", set_goal))
app.add_handler(CommandHandler("track_goal", track_goal))
app.add_handler(CommandHandler("forecast", forecast))
app.add_handler(CommandHandler("help", help_command))
# Запуск бота
if __name__ == "__main__":
    print("Бот запущено!")
    app.run_polling()

