import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Чтобы импортировать main.py и database.py из корня проекта
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import database  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Готовит изолированный TestClient с отдельной БД в tmp_path.
    После теста tmp_path удаляется pytest'ом автоматически.
    """
    test_db = tmp_path / "test.db"

    # Подменяем путь к БД во всём модуле database
    monkeypatch.setattr(database, "DB_PATH", test_db)

    # Создаём схему в новой БД
    database.init_db()

    # TestClient как контекст-менеджер — запускает lifespan
    with TestClient(app) as c:
        yield c
