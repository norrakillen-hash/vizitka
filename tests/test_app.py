"""Тесты для сайта-визитки."""


# ---------- Главная страница ----------

def test_index_returns_200(client):
    """Главная открывается и возвращает HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_index_contains_profile_data(client):
    """На главной есть имя, роль и ссылки из профиля."""
    response = client.get("/")
    text = response.text
    assert "Евгений Мазняк" in text
    assert "Python Backend Developer" in text
    assert "https://github.com/ivan" in text


def test_visit_counter_increments(client):
    """Счётчик визитов растёт при каждом запросе."""
    r1 = client.get("/")
    r2 = client.get("/")
    r3 = client.get("/")
    assert "Просмотров: 1" in r1.text
    assert "Просмотров: 2" in r2.text
    assert "Просмотров: 3" in r3.text


def test_sent_flag_shows_success_message(client):
    """При ?sent=1 показываем блок благодарности."""
    response = client.get("/?sent=1")
    assert response.status_code == 200
    assert "Спасибо" in response.text


# ---------- Форма обратной связи: успех ----------

def test_contact_success_redirects_to_index(client):
    """Успешная отправка → 303 редирект на /?sent=1."""
    response = client.post(
        "/contact",
        data={
            "name": "Тестовый Пользователь",
            "email": "test@example.com",
            "text": "Это тестовое сообщение, длиной больше 10 символов.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/?sent=1"


def test_contact_saves_message(client):
    """После успешной отправки сообщение видно в /admin."""
    client.post(
        "/contact",
        data={
            "name": "Пётр",
            "email": "petr@example.com",
            "text": "Здравствуйте, хочу предложить работу.",
        },
        follow_redirects=False,
    )
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Пётр" in response.text
    assert "petr@example.com" in response.text


# ---------- Форма обратной связи: ошибки валидации ----------

def test_contact_invalid_email(client):
    """Невалидный email → 400 с сообщением об ошибке."""
    response = client.post(
        "/contact",
        data={
            "name": "Тест",
            "email": "not-an-email",
            "text": "Валидный по длине текст.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "email" in response.text.lower()


def test_contact_short_name(client):
    """Слишком короткое имя → 400."""
    response = client.post(
        "/contact",
        data={
            "name": "А",
            "email": "test@example.com",
            "text": "Валидный по длине текст.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400


def test_contact_short_text(client):
    """Слишком короткое сообщение → 400."""
    response = client.post(
        "/contact",
        data={
            "name": "Тест",
            "email": "test@example.com",
            "text": "коротко",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400


def test_contact_missing_field(client):
    """Нет обязательного поля → 422 (FastAPI сам отдаёт)."""
    response = client.post(
        "/contact",
        data={"name": "Тест", "email": "test@example.com"},
        follow_redirects=False,
    )
    assert response.status_code == 422


def test_contact_invalid_does_not_save_to_db(client):
    """Невалидная отправка НЕ попадает в БД."""
    client.post(
        "/contact",
        data={
            "name": "А",  # короткое — не пройдёт
            "email": "test@example.com",
            "text": "Валидный по длине текст.",
        },
        follow_redirects=False,
    )
    response = client.get("/admin")
    assert "Пока никто не написал" in response.text


def test_contact_preserves_input_on_error(client):
    """При ошибке введённые данные возвращаются в форму."""
    response = client.post(
        "/contact",
        data={
            "name": "Тест",
            "email": "broken-email",
            "text": "Какое-то длинное сообщение тут.",
        },
        follow_redirects=False,
    )
    # Имя и текст должны быть в value/textarea
    assert 'value="Тест"' in response.text
    assert "Какое-то длинное сообщение тут." in response.text


# ---------- Админка ----------

def test_admin_empty(client):
    """Пустая админка показывает заглушку."""
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Пока никто не написал" in response.text


def test_admin_multiple_messages_newest_first(client):
    """Несколько сообщений — свежее сверху."""
    client.post(
        "/contact",
        data={
            "name": "Первый",
            "email": "first@example.com",
            "text": "Первое сообщение, тестовое.",
        },
        follow_redirects=False,
    )
    client.post(
        "/contact",
        data={
            "name": "Второй",
            "email": "second@example.com",
            "text": "Второе сообщение, тоже тестовое.",
        },
        follow_redirects=False,
    )
    response = client.get("/admin")
    text = response.text
    # Индекс первого вхождения должен быть больше (то есть ниже в HTML)
    pos_first = text.find("Первый")
    pos_second = text.find("Второй")
    assert pos_second != -1
    assert pos_first != -1
    assert pos_second < pos_first, "Свежее сообщение должно быть выше в HTML"


# ---------- Автодоки ----------

def test_docs_endpoint(client):
    """Swagger UI доступен."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema_valid(client):
    """OpenAPI-схема содержит наши эндпоинты."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/" in schema["paths"]
    assert "/contact" in schema["paths"]
    assert "/admin" in schema["paths"]

