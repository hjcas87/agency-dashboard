# Guía de Inicio Rápido

Guía rápida para levantar el proyecto y ejecutar tests.

## 🚀 Levantar el Proyecto en Desarrollo

### Opción 1: Con Docker Compose (Recomendado)

```bash
# 1. Levantar todos los servicios
make dev
# O directamente:
docker-compose up -d

# 2. Ver logs (opcional)
make logs
# O directamente:
docker-compose logs -f

# 3. Verificar que todo está corriendo
# Abre en tu navegador:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - N8N: http://localhost:5678
```

### Opción 2: Desarrollo Local (Sin Docker)

#### Backend

```bash
# 1. Instalar dependencias
cd backend
uv pip install -e ".[dev]"

# 2. Configurar variables de entorno
# Crear .env en backend/ con:
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
# POSTGRES_DB=core_db
# POSTGRES_HOST=localhost
# SECRET_KEY=tu-secret-key-aqui
# KAFKA_BOOTSTRAP_SERVERS=localhost:9092
# N8N_BASE_URL=http://localhost:5678

# 3. Ejecutar servidor
uv run uvicorn app.main:app --reload
```

#### Frontend

```bash
# 1. Instalar dependencias
cd frontend
npm install

# 2. Configurar variables de entorno
# Crear .env.local en frontend/ con:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Ejecutar servidor de desarrollo
npm run dev
```

## 🧪 Ejecutar Tests

### Tests del Backend

```bash
# Todos los tests
make test
# O directamente:
cd backend && uv run pytest

# Solo tests unitarios (rápidos)
make test-unit
# O directamente:
cd backend && uv run pytest -m unit

# Solo tests de integración
make test-integration
# O directamente:
cd backend && uv run pytest -m integration

# Tests con coverage
make test-cov
# O directamente:
cd backend && uv run pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Tests del Frontend

```bash
# Type checking
cd frontend && npm run type-check

# Linting
cd frontend && npm run lint
```

## 📋 Comandos Útiles

### Ver todos los comandos disponibles

```bash
make help
```

### Gestión de Servicios

```bash
# Levantar servicios
make dev

# Detener servicios
make down

# Ver logs
make logs

# Reconstruir imágenes
make build

# Limpiar todo (volúmenes, contenedores)
make clean
```

### Desarrollo

```bash
# Linting
make lint

# Formatear código
make format

# Generar tipos TypeScript desde OpenAPI
make frontend-api-types
```

### Base de Datos

```bash
# Ejecutar migraciones
make db-migrate

# Crear nueva migración
make db-revision MESSAGE="descripción de la migración"
```

### Shells en Contenedores

```bash
# Abrir shell en backend
make backend-shell

# Abrir shell en frontend
make frontend-shell
```

## 🔍 Verificar que Todo Funciona

### 1. Verificar Servicios

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs backend
docker-compose logs frontend
```

### 2. Probar Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# API Docs
open http://localhost:8000/docs
```

### 3. Verificar Frontend

```bash
# Abrir en navegador
open http://localhost:3000
```

## 🐛 Troubleshooting

### Puerto ya en uso

```bash
# Ver qué está usando el puerto
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL

# Detener servicios
make down
```

### Problemas con Docker

```bash
# Limpiar todo y empezar de nuevo
make clean
make build
make dev
```

### Problemas con dependencias

```bash
# Backend
cd backend
rm -rf .venv __pycache__
uv pip install -e ".[dev]"

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Base de datos no conecta

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

## 📚 Recursos

- [README Principal](../README.md)
- [Arquitectura](./ARCHITECTURE.md)
- [Testing Strategy](./TESTING_STRATEGY.md)
- [Backend Architecture](./BACKEND_ARCHITECTURE.md)

