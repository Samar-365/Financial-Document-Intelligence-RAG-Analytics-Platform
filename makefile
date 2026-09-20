.PHONY: install run test lint format migrate revision seed reset docker-up docker-down

install:
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -v

test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

lint:
	flake8 app tests
	mypy app

format:
	black app tests
	isort app tests

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(m)"

seed:
	python scripts/seed_db.py

reset:
	python scripts/reset_db.py

docker-up:
	docker compose up -d

docker-down:
	docker compose down