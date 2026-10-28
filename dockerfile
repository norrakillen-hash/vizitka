# syntax=docker/dockerfile:1

# ---------- База ----------
FROM python:3.12-slim

# ---------- Переменные окружения ----------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ---------- Рабочая папка ----------
WORKDIR /app

# ---------- Зависимости ----------
# Копируем ТОЛЬКО requirements.txt — для кэша
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ---------- Код приложения ----------
COPY . .

# ---------- Пользователь без root ----------
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# ---------- Порт ----------
EXPOSE 8000

# ---------- Запуск ----------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
