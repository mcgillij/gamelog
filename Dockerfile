FROM python:3.13-slim

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry==2.1.1

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi --no-cache && \
    rm -rf /root/.cache/pypoetry/*

COPY . .
CMD ["fastapi", "--verbose", "dev", "main.py", "--reload", "--host", "0.0.0.0"]
