FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/pip \
    mkdir -p game net shared server client \
    && touch game/__init__.py net/__init__.py shared/__init__.py server/__init__.py client/__init__.py \
    && pip install ".[server]"

COPY game ./game
COPY net ./net
COPY shared ./shared
COPY server ./server

RUN useradd --create-home app
USER app

EXPOSE 8000
CMD ["fastapi", "run", "server/main.py", "--port", "8000"]