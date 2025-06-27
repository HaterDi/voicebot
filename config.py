# config.py  (мини-версия без Key Vault)
import os

APP_ID       = os.getenv("MICROSOFT_APP_ID", "")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "")
PORT         = int(os.getenv("PORT", 8000))

# строка подключения к SQL (опционально)
SQL_CONNECTION = os.getenv("SQL_CONNECTION", "")

