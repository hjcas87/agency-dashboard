.PHONY: help dev up down logs build clean test

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Levantar entorno de desarrollo mínimo (solo PostgreSQL, backend y frontend se ejecutan manualmente)
	docker compose up -d postgres
	@echo "Servicios de infraestructura levantados:"
	@echo "  PostgreSQL: localhost:5432"
	@echo ""
	@echo "Backend y Frontend deben ejecutarse manualmente:"
	@echo "  Backend: cd backend && uv run uvicorn app.main:app --reload"
	@echo "  Frontend: cd frontend && npm run dev"
	@echo ""
	@echo "Para servicios adicionales (N8N, Celery, etc.):"
	@echo "  make dev-full"

dev-full: ## Levantar entorno completo con todos los servicios (N8N, Celery, RabbitMQ, etc.)
	docker compose up -d postgres rabbitmq n8n nginx celery_worker celery_beat celery_flower
	@echo "Todos los servicios levantados:"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  RabbitMQ: localhost:5672 (Management UI: http://localhost:15672)"
	@echo "  N8N: http://localhost:5678"
	@echo "  Flower (Celery): http://localhost:5555"
	@echo ""
	@echo "Backend y Frontend deben ejecutarse manualmente:"
	@echo "  Backend: cd backend && uv run uvicorn app.main:app --reload"
	@echo "  Frontend: cd frontend && npm run dev"

up: dev ## Alias para dev

down: ## Detener todos los servicios
	docker compose down

logs: ## Ver logs de todos los servicios
	docker compose logs -f

build: ## Construir imágenes Docker
	docker compose build

clean: ## Limpiar volúmenes y contenedores
	docker compose down -v
	docker system prune -f

test: ## Ejecutar tests
	cd backend && uv run pytest

test-unit: ## Ejecutar solo unit tests
	cd backend && uv run pytest -m unit

test-integration: ## Ejecutar solo integration tests
	cd backend && uv run pytest -m integration

test-cov: ## Ejecutar tests con coverage
	cd backend && uv run pytest --cov=app --cov-report=html --cov-report=term-missing

lint: ## Ejecutar linting
	cd backend && uv run black --check app && uv run isort --check-only app && uv run ruff check app
	cd frontend && npm run lint && npm run format:check

format: ## Formatear código
	cd backend && uv run black app && uv run isort app && uv run ruff check --fix app
	cd frontend && npm run format

pre-commit-install: ## Instalar pre-commit hooks
	uv pip install pre-commit || pip install pre-commit
	pre-commit install

pre-commit-run: ## Ejecutar pre-commit en todos los archivos
	pre-commit run --all-files

deploy: ## Levantar todo en producción (build + up + migrate)
	docker compose -f docker compose.deploy.yml up -d --build
	@echo "Esperando que PostgreSQL esté listo..."
	@sleep 5
	@echo "Ejecutando migraciones..."
	docker compose -f docker compose.deploy.yml exec -T backend uv run alembic upgrade head
	@echo ""
	@echo "Deploy completo. Servicios disponibles en:"
	@echo "  App: https://${DOMAIN}"
	@echo "  API: https://${DOMAIN}/api/docs"
	@echo ""
	@echo "Crear primer usuario con:"
	@echo "  make deploy-create-user EMAIL=admin@ejemplo.com NAME=Admin PASSWORD=tu-password"

deploy-build: ## Construir imágenes de producción
	docker compose -f docker compose.deploy.yml build

deploy-up: ## Levantar servicios de producción (sin build)
	docker compose -f docker compose.deploy.yml up -d

deploy-down: ## Detener servicios de producción
	docker compose -f docker compose.deploy.yml down

deploy-migrate: ## Ejecutar migraciones en producción
	docker compose -f docker compose.deploy.yml exec -T backend uv run alembic upgrade head

deploy-create-user: ## Crear usuario admin (requiere EMAIL= NAME= PASSWORD=)
	docker compose -f docker compose.deploy.yml exec -T backend uv run python scripts/create_superuser.py --email $(EMAIL) --name "$(NAME)" --password "$(PASSWORD)"

deploy-logs: ## Ver logs de producción
	docker compose -f docker compose.deploy.yml logs -f

deploy-restart: ## Reiniciar todos los servicios de producción
	docker compose -f docker compose.deploy.yml restart

prod: ## Levantar entorno de producción (requiere .env configurado)
	docker compose -f docker compose.prod.yml up -d

prod-down: ## Detener entorno de producción
	docker compose -f docker compose.prod.yml down

backend-shell: ## Abrir shell en contenedor backend
	docker compose exec backend /bin/bash

frontend-shell: ## Abrir shell en contenedor frontend
	docker compose exec frontend /bin/sh

db-migrate: ## Ejecutar migraciones de base de datos
	docker compose exec backend alembic upgrade head

db-revision: ## Crear nueva migración (usar: make db-revision MESSAGE="descripción")
	docker compose exec backend alembic revision --autogenerate -m "$(MESSAGE)"

frontend-api-types: ## Generar tipos TypeScript desde OpenAPI de FastAPI
	cd frontend && npm run generate-api-types:dev

