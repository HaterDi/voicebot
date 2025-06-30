# services/db.py
import sqlite3
from pathlib import Path

# ──────────────────────────────
# 1) Файл базы – рядом с этим .py
# ──────────────────────────────
DB_PATH = Path(__file__).with_suffix(".sqlite3")

# ──────────────────────────────
# 2) Подключение
# ──────────────────────────────
def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

# ──────────────────────────────
# 3) Инициализация (создаём таблицу один раз)
# ──────────────────────────────
def _init():
    with _conn() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name  TEXT,
                last_name   TEXT,
                phone       TEXT,
                email       TEXT,
                country     TEXT,
                city        TEXT,
                zip         TEXT
            )
            """
        )

_init()  # вызываем при импорте


# ──────────────────────────────
# 4) Сохранение одной анкеты
# ──────────────────────────────
_FIELD_ORDER = (
    "first_name",
    "last_name",
    "phone",
    "email",
    "country",
    "city",
    "zip",
)


def save_user(values: dict):
    """
    values – это step.values из бота.
    Сохраняем ТОЛЬКО нужные поля, игнорируя 'index', 'key' и прочие.
    """
    row = [values.get(k) for k in _FIELD_ORDER]  # порядок как в БД
    with _conn() as con:
        con.execute(
            f"""
            INSERT INTO users ({','.join(_FIELD_ORDER)})
            VALUES ({','.join('?' * len(_FIELD_ORDER))})
            """,
            row,
        )


# ──────────────────────────────
# 5) Чтение всех пользователей
# ──────────────────────────────
def get_all_users():
    """
    Возвращает список кортежей:
    [(first_name, last_name, phone, email, country, city, zip), ...]
    """
    with _conn() as con:
        cur = con.execute(
            f"SELECT {','.join(_FIELD_ORDER)} FROM users ORDER BY id"
        )
        return cur.fetchall()