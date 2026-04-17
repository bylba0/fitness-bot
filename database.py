import sqlite3

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
            last_reset TEXT DEFAULT ''
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
    cursor.execute(
        "UPDATE users SET goal = ? WHERE user_id = ?",
        (goal, user_id)
    )
    conn.commit()
    conn.close()

def add_calories(user_id: int, calories: int, protein: int, fat: int, carbs: int):
    from datetime import date
    today = str(date.today())
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Сбрасываем если новый день
    cursor.execute("SELECT last_reset FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row and row[0] != today:
        cursor.execute("""
            UPDATE users SET daily_calories=0, daily_protein=0,
            daily_fat=0, daily_carbs=0, last_reset=? WHERE user_id=?
        """, (today, user_id))
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

def get_stats(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user