from telegram.ext import Application, CommandHandler
from functions import (add_income, add_expense, balance)

# Створення бота
application = Application.builder().token("7680334871:AAG9RI0Zr67_6Dom7fp7BY0nnwFK8kmIKMw").build()

# Додавання обробників
application.add_handler(CommandHandler("add_income", add_income))
application.add_handler(CommandHandler("add_expense", add_expense))
application.add_handler(CommandHandler("balance", balance))

# Запуск бота
application.run_polling()