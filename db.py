import os
from typing import Dict, List, Tuple
import pytz
import datetime
import sqlite3


conn = sqlite3.connect(os.path.join("db", "db"))
cursor = conn.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join( "?" * len(column_values.keys()) )
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    conn.commit()


def get_expenses():
    cursor.execute("select sum(amount)"
                   "from expense where created=current_date")
    result = cursor.fetchone()
    return result


def get_base_expenses():
    cursor.execute("select sum(amount) "
                   "from expense where created=current_date "
                   "and category_codename in (select codename "
                   "from category where is_base_expense=true)")
    result = cursor.fetchone()
    return result


def get_expenses_month():
    now = get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor.execute(f"select sum(amount) "
                   f"from expense where created >= '{first_day_of_month}'")
    result = cursor.fetchone()
    return result


def get_base_expenses_month():
    now = get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor.execute(f"select sum(amount) "
                   f"from expense where created >= '{first_day_of_month}' "
                   f"and category_codename in (select codename "
                   f"from category where is_base_expense=true)")
    result = cursor.fetchone()
    return result


def last_expenses():
    cursor.execute(
        "select e.id, e.amount, c.name "
        "from expense e left join category c "
        "on c.codename=e.category_codename "
        "order by created desc limit 10")
    result = cursor.fetchall()
    return result

def get_cursor():
    return cursor


def get_now_datetime():
    tz = pytz.timezone("Asia/Yekaterinburg")
    now = datetime.datetime.now(tz)
    return now
