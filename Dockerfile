FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
COPY game ./game
COPY net ./net
COPY shared ./shared
COPY server ./server

RUN pip install --no-cache-dir .

RUN useradd --create-home app
USER app

EXPOSE 8000
CMD ["fastapi", "run", "server/main.py", "--port", "8000"]