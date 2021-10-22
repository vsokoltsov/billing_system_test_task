FROM python:3.9

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/

RUN pip install poetry
COPY pyproject.toml poetry.lock /app/
RUN poetry install

COPY . /app/