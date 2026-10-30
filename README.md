![CI](https://github.com/norrakillen-hash/vizitka/actions/workflows/ci.yml/badge.svg)

# Vizitka — сайт-визитка на FastAPI

Персональный сайт-визитка с формой обратной связи, счётчиком посещений и админкой. Полностью контейнеризован, с тестами и CI.

**[Открыть живой сайт](https://vizitka.de2.netrun.io/)**

## Стек

- **Python 3.12**
- **FastAPI** — веб-фреймворк
- **Jinja2** — шаблоны
- **SQLite** — база данных
- **Docker / Docker Compose** — запуск
- **Pytest + httpx** — тесты
- **GitHub Actions** — CI

## Что умеет

- Визитка с профилем, навыками и проектами
- Счётчик посещений (SQLite)
- Форма обратной связи с серверной валидацией (Pydantic)
- Админка `/admin` со списком сообщений
- Автодокументация API на `/docs`
- Покрытие тестами > 90%

## Запуск локально

### Вариант 1: через Docker (рекомендую)

```bash
docker compose up --build
```

### Вариант 2:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Тесты

```bash
pytest
pytest --cov=. --cov-report=term-missing   # с покрытием
```

### Структура

```
.
├── main.py              # FastAPI-приложение
├── profile.py           # данные профиля
├── database.py          # работа с SQLite
├── schemas.py           # Pydantic-модели
├── templates/           # Jinja2-шаблоны
├── static/              # CSS
├── tests/               # pytest-тесты
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Эндпоинты

```
Метод	Путь	Описание
GET	/	Главная страница
POST	/contact	Отправка формы связи
GET	/admin	Список сообщений
GET	/docs	Swagger UI
```
