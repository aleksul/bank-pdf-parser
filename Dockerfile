FROM python:3.10

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pdm

RUN mkdir /app
WORKDIR /app

RUN python -m venv .venv

COPY LICENSE pdm.lock pyproject.toml run.py ./
COPY src ./src

RUN pdm --non-interactive --no-cache install --no-self --frozen-lockfile

EXPOSE 8000

ENTRYPOINT pdm run run.py
