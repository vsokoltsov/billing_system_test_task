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

.PHONY: check
check:
	@echo "Run isort"
	@exec isort --check-only .
	@echo "Run black"
	@exec black --check --diff app tests
	@echo "Run flake"
	@exec pylint app tests
	@exec vulture app
	@echo "Run mypy"
	@exec mypy app
	@exec rm -rf .mypy_cache

.PHONY: lint
lint:
	@echo "* Run isort"
	@exec isort .
	@echo "* Run black"
	@exec black app tests
	@echo "* Run pylint"
	@exec pylint app tests
	@echo "* Run mypy"
	@exec mypy app
	@exec rm -rf .mypy_cache