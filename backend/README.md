# Core Backend

Backend API construido con FastAPI siguiendo arquitectura por features.

## Setup con uv

Este proyecto usa [uv](https://github.com/astral-sh/uv) para gestión de dependencias.

### Instalación de uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# O con pip
pip install uv
```

### Instalación de dependencias

```bash
# Instalar dependencias de producción
uv pip install -e .

# Instalar dependencias de desarrollo también
uv pip install -e ".[dev]"

# O usar uv sync (si tienes uv.lock)
uv sync
```

### Crear lock file

```bash
# Generar uv.lock
uv lock
```

## Desarrollo

### Ejecutar servidor

```bash
# Con uvicorn directamente
uvicorn app.main:app --reload

# O con uv run
uv run uvicorn app.main:app --reload
```

### Ejecutar tests

```bash
# Todos los tests
uv run pytest

# Solo unit tests
uv run pytest -m unit

# Con coverage
uv run pytest --cov=app --cov-report=html
```

### Linting y formateo

```bash
# Formatear código
uv run black app

# Ordenar imports
uv run isort app

# Linting con ruff
uv run ruff check app

# Fix automático
uv run ruff check --fix app
```

## Estructura

```
app/
├── core/
│   ├── features/      # Features core
│   ├── config.py      # Configuración
│   ├── database.py    # DB setup
│   └── router.py      # Router principal
├── custom/
│   └── features/      # Features personalizados
└── shared/            # Código compartido
```

## Configuración

Todas las configuraciones están en `pyproject.toml`:
- Dependencias del proyecto
- Herramientas de desarrollo (pytest, black, isort, ruff, mypy)
- Configuración de cada herramienta

## Docker

El Dockerfile usa `uv` para instalar dependencias:

```dockerfile
RUN uv pip install --system -e .
```

