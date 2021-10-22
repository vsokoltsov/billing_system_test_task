#!make

SHELL := /bin/bash
APP_PORT := $(or ${APP_PORT},${APP_PORT},8080)
APP_HOST := $(or ${APP_HOST},${APP_HOST},127.0.0.1)
PYTHONPATH := $(or ${PYTHONPATH},${PYTHONPATH},.)

.EXPORT_ALL_VARIABLES:

.PHONY: alembic-upgrade
alembic-upgrade:
	@echo "* Alembic Upgrade (head)"
	alembic upgrade head

.PHONY: run-dev
run-dev: alembic-upgrade
	@echo "* Run the app server for local development"
	APP_HOME=. APP_RELOAD=1 python app/main.py

.PHONY: test
test:
	@echo "* Run tests"
	@set -o allexport \
		&& source .env.test \
		&& make alembic-upgrade \
		&& py.test -svvv -rs --cov app --cov-report term-missing