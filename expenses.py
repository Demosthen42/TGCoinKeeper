import re
from typing import NamedTuple

import db
from categories import Categories


class Message(NamedTuple):
    amount: int
    category_text: str


class Expense(NamedTuple):
    amount: int
    category_name: str


def add_expense(raw_message: str) -> Expense:
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_text)
    db.insert("expense", {
        "amount": parsed_message.amount,
        "created": get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(amount=parsed_message.amount,
                   category_name=category.name)


def get_today_statistics() -> str:
    result = db.get_expenses()
    if not result[0]:
        return "Сегодня ещё нет расходов"
    all_today_expenses = result[0]
    result = db.get_base_expenses()
    base_today_expenses = result[0] if result[0] else 0
    return (f"Расходы сегодня:\n"
            f"всего — {all_today_expenses} руб.\n"
            f"базовые — {base_today_expenses} руб. из {_get_budget_limit()} руб.\n\n"
            f"За текущий месяц: /month")


def get_month_statistics() -> str:
    result = db.get_expenses_month()
    if not result[0]:
        return "В этом месяце ещё нет расходов"
    all_today_expenses = result[0]

    now = db.get_now_datetime()
    base_today_expenses = result[0] if result[0] else 0
    return (f"Расходы в текущем месяце:\n"
            f"всего — {all_today_expenses} руб.\n"
            f"другие — {base_today_expenses} руб. из "
            f"{now.day * _get_budget_limit()} руб.")


def last():
    rows = db.last_expenses()
    last_expenses = []
    for row in rows:
        last_expenses.append({
            'amount': row[1],
            'id': row[0],
            'category_name': row[2]
        })
    return last_expenses


def delete_expense(row_id: int) -> None:
    db.delete("expense", row_id)


def _parse_message(raw_message: str) -> Message:
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    try:
        amount = regexp_result.group(1).replace(" ", "")
        category_text = regexp_result.group(2).strip().lower()
    except:
        raise Exception(
            "Не могу разобрать. Напишите сообщение в формате 'трата' 'категория' "
            "например:\n500 еда")
    return Message(amount=amount, category_text=category_text)


def get_now_formatted() -> str:
    return db.get_now_datetime().strftime("%Y-%m-%d")


def _get_budget_limit() -> int:
    return db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]
