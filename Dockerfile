FROM python:3.14-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY app ./app
COPY bot.py ./
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --no-cache-dir .

RUN useradd --system --create-home --uid 10001 dipbot && \
    mkdir -p /app/log /app/images /app/reported_images /app/var && \
    chown -R dipbot:dipbot /app

USER dipbot

CMD ["dip-bot"]
