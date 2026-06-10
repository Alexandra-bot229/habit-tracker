import sqlite3
from datetime import date, timedelta

DATABASE = 'habits.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Таблица пользователей
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at DATE NOT NULL
        )
    ''')
    
    # Таблица привычек (с привязкой к пользователю)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            target_count INTEGER DEFAULT 1,
            created_at DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица отметок (с привязкой к пользователю)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            completed_date DATE NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(habit_id, completed_date)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных создана!")

# ========== Функции для пользователей ==========
def add_user(username, password):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
            (username, password, date.today().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username, password):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

# ========== Функции для привычек (с привязкой к user_id) ==========
def get_all_habits(user_id):
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close()
    return habits

def add_habit(user_id, name, description, target_count):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO habits (user_id, name, description, target_count, created_at) VALUES (?, ?, ?, ?, ?)',
        (user_id, name, description, target_count, date.today().isoformat())
    )
    conn.commit()
    conn.close()

def delete_habit(habit_id, user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM habit_logs WHERE habit_id = ? AND user_id = ?', (habit_id, user_id))
    conn.execute('DELETE FROM habits WHERE id = ? AND user_id = ?', (habit_id, user_id))
    conn.commit()
    conn.close()

def get_habit_by_id(habit_id, user_id):
    conn = get_db_connection()
    habit = conn.execute('SELECT * FROM habits WHERE id = ? AND user_id = ?', (habit_id, user_id)).fetchone()
    conn.close()
    return habit

def complete_habit(habit_id, user_id, completed_date=None):
    if completed_date is None:
        completed_date = date.today().isoformat()
    conn = get_db_connection()
    conn.execute(
        'INSERT OR IGNORE INTO habit_logs (habit_id, user_id, completed_date) VALUES (?, ?, ?)',
        (habit_id, user_id, completed_date)
    )
    conn.commit()
    conn.close()

def get_completion_count(habit_id, user_id):
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM habit_logs WHERE habit_id = ? AND user_id = ?', (habit_id, user_id)).fetchone()[0]
    conn.close()
    return count

def is_completed_today(habit_id, user_id):
    today = date.today().isoformat()
    conn = get_db_connection()
    result = conn.execute(
        'SELECT * FROM habit_logs WHERE habit_id = ? AND user_id = ? AND completed_date = ?',
        (habit_id, user_id, today)
    ).fetchone()
    conn.close()
    return result is not None

def get_last_7_days_logs(habit_id, user_id):
    logs = []
    today = date.today()
    conn = get_db_connection()
    for i in range(7):
        d = today - timedelta(days=i)
        result = conn.execute(
            'SELECT * FROM habit_logs WHERE habit_id = ? AND user_id = ? AND completed_date = ?',
            (habit_id, user_id, d.isoformat())
        ).fetchone()
        logs.append({
            'date': d.isoformat(),
            'completed': result is not None
        })
    conn.close()
    return logs

def search_habits(user_id, query):
    conn = get_db_connection()
    habits = conn.execute(
        'SELECT * FROM habits WHERE user_id = ? AND name LIKE ? ORDER BY created_at DESC',
        (user_id, f'%{query}%')
    ).fetchall()
    conn.close()
    return habits