# Setup con uv

Este proyecto usa [uv](https://github.com/astral-sh/uv) para gestión de dependencias Python. uv es un gestor de paquetes extremadamente rápido escrito en Rust.

## ¿Por qué uv?

- ⚡ **10-100x más rápido** que pip
- 🔒 **Lock files** determinísticos
- 📦 **Gestión moderna** de dependencias
- 🛠️ **Compatibilidad** con pip y PyPI
- 🎯 **Mejor resolución** de dependencias

## Instalación

### macOS/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Con pip

```bash
pip install uv
```

## Uso Básico

### Instalar dependencias

```bash
# Instalar dependencias de producción
uv pip install -e .

# Instalar dependencias de desarrollo también
uv pip install -e ".[dev]"

# O usar uv sync (recomendado si tienes uv.lock)
uv sync
```

### Generar lock file

```bash
# Generar uv.lock para dependencias determinísticas
uv lock
```

### Ejecutar comandos

```bash
# Ejecutar cualquier comando Python
uv run pytest
uv run black app
uv run uvicorn app.main:app --reload
```

## Configuración en pyproject.toml

Todas las dependencias y configuraciones están en `pyproject.toml`:

```toml
[project]
dependencies = [
    "fastapi==0.104.1",
    # ...
]

[project.optional-dependencies]
dev = [
    "pytest==7.4.3",
    # ...
]

[tool.uv]
dev-dependencies = [
    "pytest==7.4.3",
    # ...
]
```

## Herramientas Configuradas

Todas las herramientas están configuradas en `pyproject.toml`:

- **pytest**: Tests y coverage
- **black**: Formateo de código
- **isort**: Ordenamiento de imports
- **ruff**: Linting rápido
- **mypy**: Type checking

### Ejecutar herramientas

```bash
# Formatear código
uv run black app

# Ordenar imports
uv run isort app

# Linting
uv run ruff check app
uv run ruff check --fix app  # Fix automático

# Type checking
uv run mypy app

# Tests
uv run pytest
```

## Docker

El Dockerfile usa uv:

```dockerfile
RUN pip install uv
RUN uv pip install --system -e .
```

## CI/CD

GitHub Actions usa uv:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v2

- name: Install dependencies
  run: uv pip install -e ".[dev]"
```

## Migración desde requirements.txt

Si venías usando `requirements.txt`:

1. ✅ Ya migrado a `pyproject.toml`
2. ✅ `requirements.txt` puede eliminarse (opcional, mantenido por compatibilidad)
3. ✅ Usar `uv pip install -e .` en lugar de `pip install -r requirements.txt`

## Ventajas sobre pip

| Característica | pip | uv |
|---------------|-----|-----|
| Velocidad | 1x | 10-100x |
| Lock files | No nativo | Sí |
| Resolución | Básica | Avanzada |
| Instalación | Lenta | Muy rápida |

## Recursos

- [Documentación oficial de uv](https://github.com/astral-sh/uv)
- [Guía de migración](https://github.com/astral-sh/uv/blob/main/docs/requirements-txt.md)

