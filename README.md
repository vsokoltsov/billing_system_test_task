# Simple billing system test task

![CI](https://github.com/vsokoltsov/billing_system_test_task/workflows/CI/badge.svg?branch=main)

## Pre-running

* Populate `.env` and `.env.test` files with variables from `.env.sample`

## Run

* `docker-compose up`

## Tests

* `docker-compose run billing_app bash -c "pytest -v"`