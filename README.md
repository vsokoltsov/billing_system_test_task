# Simple billing system test task

![CI](https://github.com/vsokoltsov/billing_system_test_task/workflows/CI/badge.svg?branch=main)

## Pre-running

* Populate `.env` and `.env.test` files with variables from `.env.sample`

## Run

* `docker-compose up`

## Tests

* `docker-compose -f docker-compose.test.yml up -d`
* `docker-compose run billing bash -c "pytest -v"`