# Mendri — Agency Dashboard

Dashboard base para gestionar proyectos, clientes, presupuestos y facturación de la agencia.

## Qué incluye

| Componente | Descripción |
|---|---|
| **Auth completa** | Login, registro, protected routes |
| **Dashboard** | Layout con sidebar, header, métricas base |
| **Sistema de mensajes** | Toast notifications globales para redirecciones |
| **Theme** | Dark/light mode con componentes listos |
| **N8N** | Integración lista para automatizaciones |
| **Celery** | Background tasks para tareas pesadas |

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Next.js 16 (App Router), React 19, TypeScript, Tailwind, shadcn/ui |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic, Pydantic |
| Base de datos | PostgreSQL 15 |
| Message Broker | RabbitMQ + Celery |
| Automatización | N8N self-hosted |
| Infra | Docker Compose, Nginx |

## Inicio rápido

### Prerrequisitos

- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes Python)
- Node.js 18+

### Levantar el proyecto

```bash
# 1. Copiar variables de entorno
cp .env.example backend/.env

# 2. Iniciar infraestructura (PostgreSQL, RabbitMQ, N8N, Celery)
make dev

# 3. Backend (en otra terminal)
cd backend && uv run uvicorn app.main:app --reload

# 4. Frontend (en otra terminal)
cd frontend && npm install && npm run dev
```

### Servicios disponibles

| Servicio | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| N8N | http://localhost:5678 |
| RabbitMQ Management | http://localhost:15672 |

## Comandos útiles

```bash
make help          # Ver todos los comandos
make dev           # Levantar infraestructura
make down          # Detener servicios
make logs          # Ver logs
make test          # Ejecutar tests
make format        # Formatear código
make lint          # Verificar calidad
make pre-commit-install  # Instalar pre-commit hooks
```

## Estructura

```
.
├── backend/                    # FastAPI
│   ├── app/
│   │   ├── core/               # Módulos base (auth, users, health)
│   │   ├── custom/             # Features del proyecto
│   │   └── shared/             # Interfaces y servicios compartidos
│   └── alembic/                # Migraciones DB
├── frontend/                   # Next.js
│   ├── app/
│   │   ├── (auth)/            # Rutas públicas (login, register)
│   │   ├── (private)/         # Rutas protegidas
│   │   └── api/               # API routes
│   ├── components/
│   │   ├── core/              # Componentes base
│   │   └── custom/            # Componentes del proyecto
│   └── lib/                   # Utilidades
├── automation/                 # Workflows N8N
├── docker-compose.yml          # Desarrollo
├── docker-compose.prod.yml     # Producción
└── docs/
    ├── agents/                    # Roles y skills para IA
    └── solution_design/           # Templates de diseño de solución
```

## Arquitectura

El proyecto sigue el patrón **core/custom**:

- **`core/`** — Módulos genéricos reutilizables (no modificar en forks)
- **`custom/`** — Features específicas del proyecto (aquí se trabaja)

Ver [ARCHITECTURE.md](./ARCHITECTURE.md) para detalles técnicos completos.

## Pre-commit

Se ejecuta automáticamente en cada commit:

- ✅ Prettier (formato frontend)
- ✅ TypeScript type check
- ✅ Black/isort/ruff (formato backend)
- ✅ Conventional commits validation

```bash
make pre-commit-install   # Instalar hooks
```

## Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Configurar variables de producción en `.env` (SECRET_KEY, CORS, etc.).
