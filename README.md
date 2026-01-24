# Core Boilerplate - Forward Deployed Engineer Platform

Boilerplate reutilizable y extensible para desarrollo rápido de proyectos personalizados con automatizaciones IA.

## 🏗️ Arquitectura

El proyecto está dividido en tres componentes principales:

- **Frontend**: Next.js 15.5.9 con React 19.2.3, shadcn/ui y Tailwind CSS
- **Backend**: FastAPI modular con arquitectura por features (core/custom)
- **Message Broker**: Kafka para mensajería robusta y escalable
- **Automation**: N8N self-hosted con webhooks

### Estructura de Módulos

```
core/          # Módulos base (no modificar en forks)
custom/        # Módulos específicos del cliente (extender aquí)
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker & Docker Compose
- Node.js 18+ (para desarrollo local del frontend, opcional)
- Python 3.11+ (para desarrollo local del backend, opcional)
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes Python, recomendado)

### Levantar el Proyecto

```bash
# Opción 1: Usar Makefile (recomendado)
make dev

# Opción 2: Docker Compose directamente
docker-compose up -d
```

### Ejecutar Tests

```bash
# Todos los tests del backend
make test

# Solo tests unitarios (rápidos)
make test-unit

# Tests con coverage
make test-cov
```

📖 **Ver [Guía de Inicio Rápido](./docs/QUICK_START.md) para más detalles**

### Comandos Útiles

```bash
# Ver todos los comandos disponibles
make help

# Ver logs
make logs

# Detener servicios
make down

# Limpiar todo
make clean
```

### Servicios Disponibles

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **N8N**: http://localhost:5678
- **Nginx**: http://localhost:80

## 📁 Estructura del Proyecto

```
.
├── frontend/          # Aplicación Next.js
│   ├── app/          # App Router de Next.js
│   ├── components/   # Componentes React
│   │   ├── core/     # Componentes base
│   │   └── custom/   # Componentes personalizados
│   └── lib/          # Utilidades y configuraciones
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── core/     # Módulos core
│   │   │   └── features/  # Features autocontenidos
│   │   ├── custom/   # Módulos custom
│   │   │   └── features/    # Features personalizados
│   │   └── shared/   # Código compartido (interfaces, services, repos)
│   └── alembic/      # Migraciones DB
├── automation/        # Configuración N8N
├── nginx/            # Configuración Nginx
├── docker-compose.yml
└── docker-compose.prod.yml
```

## 🔧 Desarrollo

### Extender el Proyecto

Para agregar funcionalidad específica de cliente:

1. **Frontend**: Crear componentes en `frontend/components/custom/`
2. **Backend**: Crear módulos en `backend/app/custom/`
3. **N8N**: Agregar workflows en `automation/workflows/`

### Actualizar desde el Fork Original

Los módulos `core/` están diseñados para ser actualizados sin romper los módulos `custom/`. Al hacer merge desde el repo original:

1. Los cambios en `core/` se aplicarán automáticamente
2. Los módulos `custom/` permanecerán intactos
3. Revisar breaking changes en la documentación de actualización

## 🚢 Deployment

### Producción con Traefik

```bash
docker-compose -f docker-compose.prod.yml up -d
```

El `docker-compose.prod.yml` incluye los labels necesarios para Traefik.

### Variables de Entorno

Copiar `.env.example` a `.env` y configurar:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `N8N_BASIC_AUTH_USER`, `N8N_BASIC_AUTH_PASSWORD`
- `SECRET_KEY` (backend)
- `NEXT_PUBLIC_API_URL` (frontend)
- `KAFKA_BOOTSTRAP_SERVERS` (Kafka connection)

## 📚 Documentación Adicional

- [Arquitectura del Sistema](./docs/ARCHITECTURE.md) - Arquitectura completa y patrones de diseño
- [Decisiones Arquitectónicas](./docs/ARCHITECTURE_DECISIONS.md) - ¿Por qué Features y no Modules?
- [Asistentes de IA](./docs/AI_ASSISTANTS.md) - Configuración de Cursor y Codex
- [Documentación de Negocio](./docs/business/README.md) - Cómo organizar requisitos, diagramas y diseños
- [Setup con uv](./docs/UV_SETUP.md) - Guía de uso de uv para dependencias
- [MVP Features](./docs/MVP_FEATURES.md) - Funcionalidades mínimas viables
- [Estrategia de Testing](./docs/TESTING_STRATEGY.md) - Guía completa de testing
- [Guía de Extensión](./docs/EXTENDING.md) - Cómo extender el proyecto sin romper actualizaciones
- [Arquitectura Backend](./docs/BACKEND_ARCHITECTURE.md) - Detalles técnicos del backend
- [Configuración de Kafka](./docs/KAFKA_SETUP.md) - Setup y uso de Kafka
- [Guía de N8N](./docs/N8N_GUIDE.md) - Cómo usar N8N para automatizaciones
- [Pre-commit Hooks](./docs/PRE_COMMIT.md) - Configuración y uso de pre-commit
- [Conventional Commits](./docs/CONVENTIONAL_COMMITS.md) - Formato de mensajes de commit
- [Security Updates](./docs/SECURITY_UPDATES.md) - Registro de actualizaciones de seguridad
- [React 19 Migration](./docs/REACT_19_MIGRATION.md) - Guía de migración a React 19
- [Quick Start](./docs/QUICK_START.md) - Guía rápida de inicio y comandos esenciales

## 🔧 Pre-commit Hooks

El proyecto incluye pre-commit hooks para asegurar calidad de código antes de cada commit.

### Instalación

```bash
# Instalar pre-commit
make pre-commit-install

# O manualmente
uv pip install pre-commit  # o pip install pre-commit
pre-commit install
```

### Hooks Configurados

**Backend (Python):**

- ✅ Black (formateo)
- ✅ isort (ordenamiento de imports)
- ✅ Ruff (linting)
- ✅ MyPy (type checking)
- ✅ Pytest unit tests

**Frontend (Next.js/TypeScript):**

- ✅ Prettier (formateo)
- ✅ ESLint (linting)
- ✅ TypeScript type checking

**Commit Messages:**

- ✅ Conventional Commits validation

### Uso

Los hooks se ejecutan automáticamente en cada commit. Para ejecutarlos manualmente:

```bash
# Ejecutar en todos los archivos
make pre-commit-run

# O manualmente
pre-commit run --all-files

# Ejecutar solo un hook específico
pre-commit run black --all-files
```

### Formato de Commits

Los mensajes de commit deben seguir el formato de [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# ✅ Formato correcto
git commit -m "feat: agregar autenticación con JWT"
git commit -m "fix(api): corregir error 500 en usuarios"
git commit -m "docs: actualizar guía de instalación"

# ❌ Formato incorrecto
git commit -m "agregar feature"
git commit -m "fix bug"
```

Ver [Guía de Conventional Commits](./docs/CONVENTIONAL_COMMITS.md) para más detalles.

### Saltar Hooks (No Recomendado)

```bash
# Solo en casos excepcionales
git commit --no-verify
```

## 🛠️ Comandos Útiles

Ver `Makefile` para todos los comandos disponibles:

```bash
make help          # Ver todos los comandos
make dev           # Levantar entorno de desarrollo
make logs          # Ver logs
make db-migrate    # Ejecutar migraciones
make clean         # Limpiar volúmenes y contenedores
```

## 🔌 API Client (Type-Safe)

El frontend usa `openapi-fetch` para consumir la API de FastAPI con tipos generados automáticamente.

### Generar Tipos desde OpenAPI

```bash
# Asegúrate de que el backend esté corriendo
make dev

# Generar tipos TypeScript desde el esquema OpenAPI
make frontend-api-types

# O manualmente
cd frontend && npm run generate-api-types:dev
```

### Uso del Cliente API

```typescript
import { apiClient } from "@/lib/api/client";

// GET request tipado
const { data, error } = await apiClient.GET("/api/v1/users");

// POST request tipado
const { data, error } = await apiClient.POST("/api/v1/users", {
  body: {
    email: "user@example.com",
    name: "John Doe",
  },
});
```

Ver [lib/api/README.md](./frontend/lib/api/README.md) para más detalles.

## 🧪 Testing

```bash
# Con uv (recomendado)
cd backend && uv run pytest

# O usar Makefile
make test
make test-unit
make test-integration
make test-cov

# Linting y formateo
make lint      # Verificar formato
make format    # Formatear código
```

## 📦 Gestión de Dependencias

Este proyecto usa **uv** para gestión de dependencias (más rápido que pip).

```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias
cd backend
uv pip install -e ".[dev]"

# Generar lock file
uv lock

# Ver más en backend/README.md
```

### Estructura de Tests

- **Unit Tests**: Tests rápidos sin dependencias externas
- **Integration Tests**: Tests con base de datos y servicios mockeados
- **E2E Tests**: Tests end-to-end con todos los servicios
- **Performance Tests**: Tests de rendimiento

Ver [Estrategia de Testing](./docs/TESTING_STRATEGY.md) para más detalles.

## 🤝 Contribución

Este es un boilerplate interno. Para contribuir al core, contactar al equipo de arquitectura.
