FROM python:3.9

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app/
ENV PATH="${PATH}:/root/.poetry/bin"
ENV POETRY_VIRTUALENVS_CREATE="false"

WORKDIR ${APP_HOME}


RUN pip install poetry
COPY pyproject.toml poetry.lock ${APP_HOME}
RUN poetry install --no-interaction --no-ansi --no-root

COPY . ${APP_HOME}

RUN groupadd usergroup
RUN useradd -s /bin/bash user
RUN chown -R user:usergroup ${APP_HOME}
RUN chmod +x /app/docker-entrypoint.sh

RUN poetry install --no-interaction --no-ansi

USER "user"

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["help"]