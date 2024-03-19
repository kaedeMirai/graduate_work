FROM python:3.11

WORKDIR /app
ENV PYTHONPATH=/app

RUN pip install --upgrade pip && pip install --no-cache-dir poetry==1.6.1 distlib
COPY ./poetry.lock ./pyproject.toml /app/

RUN poetry config virtualenvs.create false && poetry install --no-cache

COPY ./src /app/
COPY ./migrations /app/migrations

COPY ./alembic.ini /app/alembic.ini
COPY ./docker-entrypoint.sh /app/docker-entrypoint.sh
COPY ./Makefile /app/Makefile
RUN chmod o+x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
