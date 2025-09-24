FROM python:3.12-slim

# Системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Рабочая директория
WORKDIR /app
COPY pyproject.toml poetry.lock /app/

# Установка зависимостей проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Копирование исходного кода
COPY . /app

#сборка статики
RUN poetry run python manage.py collectstatic --noinput
# Порт приложения
EXPOSE 8000





# Команда запуска
CMD ["python", "manage.py", "runserver_plus", "0.0.0.0:8000"]
