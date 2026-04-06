import os
from datetime import timedelta
from pytz import timezone

# Настройки приложения
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_reports.db")
TIMEZONE = timezone('Europe/Moscow')

# Настройки CORS
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
]