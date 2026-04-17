import sqlite3
from datetime import date

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            goal TEXT DEFAULT 'не указана',
            daily_calories INTEGER DEFAULT 0,
            daily_protein INTEGER DEFAULT 0,
            daily_fat INTEGER DEFAULT 0,
            daily_carbs INTEGER DEFAULT 0,
            daily_water INTEGER DEFAULT 0,
            last_reset TEXT DEFAULT '',
            current_weight REAL DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weight_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            weight REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(user_id: int, name: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )
        conn.commit()
    conn.close()

def set_goal(user_id: int, goal: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET goal = ? WHERE user_id = ?", (goal, user_id))
    conn.commit()
    conn.close()

def reset_if_new_day(cursor, user_id: int):
    today = str(date.today())
    cursor.execute("SELECT last_reset FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row and row[0] != today:
        cursor.execute("""
            UPDATE users SET daily_calories=0, daily_protein=0,
            daily_fat=0, daily_carbs=0, daily_water=0, last_reset=?
            WHERE user_id=?
        """, (today, user_id))

def add_calories(user_id: int, calories: int, protein: int, fat: int, carbs: int):
    today = str(date.today())
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    reset_if_new_day(cursor, user_id)
    cursor.execute("""
        UPDATE users SET
            daily_calories = daily_calories + ?,
            daily_protein = daily_protein + ?,
            daily_fat = daily_fat + ?,
            daily_carbs = daily_carbs + ?,
            last_reset = ?
        WHERE user_id = ?
    """, (calories, protein, fat, carbs, today, user_id))
    conn.commit()
    conn.close()

def add_water(user_id: int, ml: int):
    today = str(date.today())
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    reset_if_new_day(cursor, user_id)
    cursor.execute("""
        UPDATE users SET daily_water = daily_water + ?, last_reset = ?
        WHERE user_id = ?
    """, (ml, today, user_id))
    conn.commit()
    conn.close()

def add_weight(user_id: int, weight: float):
    today = str(date.today())
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET current_weight = ? WHERE user_id = ?", (weight, user_id))
    cursor.execute(
        "INSERT INTO weight_history (user_id, weight, date) VALUES (?, ?, ?)",
        (user_id, weight, today)
    )
    conn.commit()
    conn.close()

def get_weight_history(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT weight, date FROM weight_history WHERE user_id = ? ORDER BY date DESC LIMIT 7",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_stats(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user