import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Проверяем переменную окружения (её мы зададим на Netrun)
if os.environ.get("DB_PATH"):
    DB_PATH = os.environ.get("DB_PATH", "vizitka.db")
else:
    # Локальный вариант для разработки
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)
    DB_PATH = DATA_DIR / "vizitka.db"


@contextmanager
def get_connection():
    """
    Открывает соединение с БД, отдаёт его наружу, а после выхода
    из блока with — коммитит изменения и закрывает соединение.
    Если внутри блока была ошибка — откатывает изменения (rollback).
    """
    conn = sqlite3.connect(DB_PATH)
    # Row позволяет обращаться к колонкам по имени: row["count"], а не row[0]
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Создаёт таблицы, если их ещё нет. Вызывается при старте приложения.
    IF NOT EXISTS — значит повторный вызов безопасен.
    """
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                visited_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip          TEXT,
                user_agent  TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                email       TEXT NOT NULL,
                text        TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def register_visit(ip: str | None, user_agent: str | None) -> int:
    """
    Записывает визит и возвращает общее количество посещений.
    """
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO visits (ip, user_agent) VALUES (?, ?)",
            (ip, user_agent),
        )
        row = conn.execute("SELECT COUNT(*) AS total FROM visits").fetchone()
        return row["total"]

def save_message(name: str, email: str, text: str) -> int:
    """
    Сохраняет сообщение и возвращает его id.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO messages (name, email, text) VALUES (?, ?, ?)",
            (name, email, text),
        )
        return cursor.lastrowid


def get_all_messages() -> list[sqlite3.Row]:
    """
    Возвращает все сообщения, свежие — сверху.
    """
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name, email, text, created_at "
            "FROM messages ORDER BY id DESC"
        ).fetchall()
