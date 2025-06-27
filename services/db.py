# voicebot/services/db.py
import os, logging, textwrap

# ⬇️  пробуем импортировать pyodbc, но не падаем, если его нет
try:
    import pyodbc
except ImportError:
    pyodbc = None

SQL_CONNECTION = os.getenv("SQL_CONNECTION", "")

_INIT_SQL = textwrap.dedent("""
IF OBJECT_ID('dbo.users') IS NULL
CREATE TABLE users(
  id INT IDENTITY PRIMARY KEY,
  first NVARCHAR(50), last NVARCHAR(50),
  phone NVARCHAR(30), email NVARCHAR(100),
  country NVARCHAR(50), city NVARCHAR(50), zip NVARCHAR(20),
  created_at DATETIME DEFAULT GETDATE()
)
""")

def _get_conn():
    if not pyodbc or not SQL_CONNECTION:
        return None
    return pyodbc.connect(SQL_CONNECTION)

def save_user(data: dict):
    """
    Пишет ответы в таблицу users. Если pyodbc или строка подключения
    отсутствуют, просто выводит предупреждение и продолжает работу.
    """
    conn = _get_conn()
    if conn is None:
        logging.warning("⚠️  SQL disabled – nothing saved (pyodbc or SQL_CONNECTION missing)")
        return

    with conn:
        conn.execute(_INIT_SQL)
        conn.execute(
            "INSERT INTO users(first,last,phone,email,country,city,zip) "
            "VALUES (?,?,?,?,?,?,?)",
            data["first"], data["last"], data["phone"], data["email"],
            data["country"], data["city"], data["zip"]
        )
        conn.commit()
        logging.info("✅ User saved to SQL")
