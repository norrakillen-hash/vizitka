from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import get_all_messages, init_db, register_visit, save_message
from profile import PROFILE
from schemas import ContactForm

# Путь к папке проекта (там, где лежит main.py)
BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Код до yield — выполняется при старте приложения.
    Код после yield — при остановке.
    """
    init_db()          # создаём таблицы, если их ещё нет
    yield

# Создаём приложение. title/description — это для автодоков /docs
app = FastAPI(
    title="Vizitka",
    description="Сайт-визитка на FastAPI",
    version="0.1.0",
    lifespan=lifespan,
)

# Говорим FastAPI: "всё, что лежит в static/, отдавай как есть по адресу /static/..."
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Говорим: "шаблоны ищи в папке templates/"
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request, sent: bool = False):
    """Главная страница. Считаем визит и передаём счётчик в шаблон."""
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    visits_total = register_visit(ip=ip, user_agent=user_agent)

    """Главная страница — рендерим шаблон и передаём туда PROFILE."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"p": PROFILE,
                 "visits_total": visits_total,
                 "sent": sent,
        },
    )

@app.post("/contact", response_class=HTMLResponse)
def contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    text: str = Form(...),
):
    """
    Принимает данные формы, валидирует через Pydantic, сохраняет в БД.
    При успехе — редирект на главную с ?sent=1.
    При ошибке валидации — перерисовывает главную с ошибками.
    """
    try:
        form = ContactForm(name=name, email=email, text=text)
    except Exception as e:
        visits_total = register_visit(
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "p": PROFILE,
                "visits_total": visits_total,
                "sent": False,
                "errors": str(e),
                "form_data": {"name": name, "email": email, "text": text},
            },
            status_code=400,
        )

    save_message(name=form.name, email=form.email, text=form.text)
    return RedirectResponse(url="/?sent=1", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    """Список всех сообщений."""
    messages = get_all_messages()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"messages": messages},
    )