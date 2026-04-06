from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from .api import auth, reports, users, admin
from .config import ALLOWED_ORIGINS
from .database import engine, Base
from pytz import timezone
from datetime import datetime

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Инициализируем приложение
app = FastAPI(
    title="Финансовая отчетность",
    description="Веб-приложение для сбора и анализа финансовой отчетности",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="templates")

# Подключаем маршруты
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.middleware("http")
async def add_timezone_header(request: Request, call_next):
    """Добавляем часовой пояс в заголовки"""
    request.state.timezone = timezone('Europe/Moscow')
    response = await call_next(request)
    return response

@app.getHTMLResponse)
async def root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Дашборд пользователя"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/report", response_class=HTMLResponse)
async def report_form(request: Request):
    """Форма отчета"""
    return templates.TemplateResponse("report_form.html", {"request": request})