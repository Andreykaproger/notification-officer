.PHONY: help up down build logs ps shell migrate revision upgrade downgrade lint format test

help:
	@echo "Available commands:"
	@echo "  make up          - Start containers"
	@echo "  make down        - Stop containers"
	@echo "  make build       - Rebuild containers"
	@echo "  make logs        - Show logs"
	@echo "  make ps          - Show running containers"
	@echo "  make shell       - Open shell in API container"
	@echo "  make migrate     - Apply migrations"
	@echo "  make revision    - Create Alembic migration"
	@echo "  make downgrade   - Rollback last migration"
	@echo "  make lint        - Run Ruff"
	@echo "  make format      - Format code"
	@echo "  make test        - Run tests"

COMPOSE = docker compose \
	-f docker-compose.yml \
	-f docker-compose.dev.yml

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) up --build -d

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

shell:
	$(COMPOSE) exec api bash

migrate:
	$(COMPOSE) exec api uv run alembic upgrade head

revision:
	@read -p "Migration name: " name; \
	$(COMPOSE) exec api uv run alembic revision --autogenerate -m "$$name"

downgrade:
	$(COMPOSE) exec api uv run alembic downgrade -1

lint:
	$(COMPOSE) exec api uv run ruff check .

format:
	$(COMPOSE) exec api uv run ruff format .

test:
	$(COMPOSE) exec api uv run pytest

current:
	$(COMPOSE) exec api uv run alembic current

history:
	$(COMPOSE) exec api uv run alembic history

heads:
	$(COMPOSE) exec api uv run alembic heads

db:
	$(COMPOSE) exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)