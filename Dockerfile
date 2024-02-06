FROM python:3.11

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY bot.py .

COPY .env .

COPY ./app /app

COPY ./alembic /alembic

COPY alembic.ini .

CMD ["python", "bot.py"]