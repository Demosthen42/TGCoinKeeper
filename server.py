import logging
import logging.handlers
import sys
from aiogram import Bot, Dispatcher, executor, types

import expenses
from categories import Categories



logger = logging.getLogger()
logger.debug(' i think a module is loaded')
fmt = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(process)d] %(module)s : %(funcName)s  [line:%(lineno)d] - %(message)s ')
file_handler = logging.handlers.RotatingFileHandler('./full.log', maxBytes=200000000, backupCount=100)
file_handler.setFormatter(fmt)
std = logging.StreamHandler(sys.stdout)
std.setFormatter(fmt)
logger.addHandler(file_handler)
logger.addHandler(std)
logger.setLevel(logging.DEBUG)


API_TOKEN = "5062989408:AAFB74KAo_4Z07_W-MfIty8a69OzWA0DqrM"


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Бот планировщик расходов\n\n"
        "Добавить расход: 100 еда\n"
        "Статистика за сегодня: /today\n"
        "За текущий месяц: /month\n"
        "Последние внесённые расходы: /expenses\n"
        "Категории трат: /categories")


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n* " +\
            ("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return
    last_expenses_rows = [
        f"{row['amount']} руб. на {row['category_name']} —  нажми "
        f"/del{row['id']} для удаления"
        for row in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* ".join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    try:
        expense = expenses.add_expense(message.text)
    except Exception as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} руб на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
