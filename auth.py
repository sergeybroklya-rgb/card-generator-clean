import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

DB_PATH = "users.db"

def init_db():
    """Создаёт таблицы пользователей и истории"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            subscription_active INTEGER DEFAULT 0,
            subscription_until TEXT,
            generations_today INTEGER DEFAULT 0,
            total_generations INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    # Таблица истории генераций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            products_count INTEGER,
            created_at TEXT,
            file_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email: str, password: str) -> bool:
    """Регистрирует нового пользователя"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password, created_at, total_generations) VALUES (?, ?, ?, ?)",
            (email, hash_password(password), datetime.now().isoformat(), 0)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email: str, password: str) -> dict:
    """Проверяет логин и возвращает данные пользователя"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, subscription_active, subscription_until, total_generations FROM users WHERE email = ? AND password = ?",
        (email, hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "subscription_active": bool(row[2]),
            "subscription_until": row[3],
            "total_generations": row[4]
        }
    return None

def can_generate(user_id: int) -> bool:
    """Проверяет, может ли пользователь генерировать (3 бесплатно или подписка)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT total_generations, subscription_active FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False
    
    total, subscription = row
    if subscription:
        return True
    return total < 3  # 3 бесплатные генерации

def increment_generations(user_id: int):
    """Увеличивает счётчик генераций"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET total_generations = total_generations + 1 WHERE id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

def save_history(user_id: int, filename: str, products_count: int, file_path: str):
    """Сохраняет историю генерации"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (user_id, filename, products_count, created_at, file_path) VALUES (?, ?, ?, ?, ?)",
        (user_id, filename, products_count, datetime.now().isoformat(), file_path)
    )
    conn.commit()
    conn.close()

def get_history(user_id: int) -> list:
    """Возвращает историю генераций пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, products_count, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"filename": r[0], "products_count": r[1], "created_at": r[2]} for r in rows]

def get_all_users() -> list:
    """Возвращает список всех пользователей (для админа)"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, subscription_active, subscription_until, total_generations FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    return [{"id": r[0], "email": r[1], "subscription_active": bool(r[2]), 
             "subscription_until": r[3], "total_generations": r[4]} for r in rows]

def activate_subscription(user_id: int, days: int = 30):
    """Активирует подписку для пользователя на N дней"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    until = (datetime.now() + timedelta(days=days)).isoformat()
    cursor.execute(
        "UPDATE users SET subscription_active = 1, subscription_until = ? WHERE id = ?",
        (until, user_id)
    )
    conn.commit()
    conn.close()

# Инициализируем БД при запуске
init_db()