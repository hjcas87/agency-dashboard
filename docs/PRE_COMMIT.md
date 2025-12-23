# Pre-commit Hooks Configuration

Esta guía explica cómo funciona la configuración de pre-commit hooks en el proyecto.

## ¿Qué es Pre-commit?

Pre-commit es un framework para gestionar y mantener hooks de Git multi-lenguaje. Los hooks se ejecutan automáticamente antes de cada commit para asegurar que el código cumple con los estándares del proyecto.

## Instalación

### Requisitos Previos

- Python 3.11+ (para instalar pre-commit)
- Node.js y npm (para hooks del frontend)

### Pasos de Instalación

```bash
# Opción 1: Usar Makefile
make pre-commit-install

# Opción 2: Manualmente
# Instalar pre-commit
uv pip install pre-commit
# o
pip install pre-commit

# Instalar los hooks en el repositorio
pre-commit install
```

## Hooks Configurados

### Commit Message Validation

#### **Conventional Commits Validator**
- **Qué hace**: Valida que los mensajes de commit sigan el formato de Conventional Commits
- **Cuándo**: En el hook `commit-msg` (antes de completar el commit)
- **Formato esperado**: `<type>[optional scope]: <description>`
- **Tipos permitidos**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

Ver [Conventional Commits Guide](./CONVENTIONAL_COMMITS.md) para más detalles.

### Backend (Python)

#### 1. **Black** - Formateador de Código
- **Qué hace**: Formatea código Python según estándares
- **Archivos**: `backend/**/*.py`
- **Configuración**: Line length = 100

#### 2. **isort** - Ordenador de Imports
- **Qué hace**: Ordena y organiza imports de Python
- **Archivos**: `backend/**/*.py`
- **Configuración**: Profile = black, line length = 100

#### 3. **Ruff** - Linter
- **Qué hace**: Detecta errores y problemas de estilo
- **Archivos**: `backend/**/*.py`
- **Configuración**: Auto-fix habilitado

#### 4. **MyPy** - Type Checker
- **Qué hace**: Verifica tipos estáticos
- **Archivos**: `backend/**/*.py` (excluye tests y alembic)
- **Configuración**: Python 3.11, ignore missing imports

#### 5. **Pytest Unit Tests**
- **Qué hace**: Ejecuta solo tests unitarios (rápidos)
- **Archivos**: Detecta cambios en `backend/**/*.py`
- **Marcador**: `-m unit`

### Frontend (Next.js/TypeScript)

#### 1. **Prettier** - Formateador
- **Qué hace**: Formatea código TypeScript/JavaScript, JSON, CSS, Markdown
- **Archivos**: `frontend/**/*.{ts,tsx,js,jsx,json,css,md}`
- **Excluye**: `node_modules`, `.next`, `out`, `build`

#### 2. **ESLint** - Linter
- **Qué hace**: Detecta errores y problemas de código
- **Archivos**: `frontend/**/*.{ts,tsx,js,jsx}`
- **Configuración**: Next.js config, auto-fix habilitado

#### 3. **TypeScript Type Check**
- **Qué hace**: Verifica tipos de TypeScript
- **Archivos**: `frontend/**/*.{ts,tsx}`
- **Comando**: `npm run type-check`

### Hooks Generales

- **Trailing whitespace**: Elimina espacios al final de líneas
- **End of file fixer**: Asegura nueva línea al final de archivos
- **YAML/JSON/TOML checker**: Valida sintaxis
- **Large files**: Previene commits de archivos muy grandes (>1MB)
- **Merge conflict**: Detecta marcadores de conflictos
- **Case conflict**: Detecta conflictos de mayúsculas/minúsculas
- **Mixed line ending**: Normaliza finales de línea a LF

## Uso

### Ejecución Automática

Los hooks se ejecutan automáticamente:

**Antes del commit (pre-commit):**
- Formateo, linting, type checking, tests

**Durante el commit (commit-msg):**
- Validación del mensaje de commit (Conventional Commits)

```bash
git add .
git commit -m "feat: agregar nueva funcionalidad"
# Los hooks se ejecutan automáticamente aquí
# - Pre-commit: formateo, linting, tests
# - Commit-msg: validación del formato del mensaje
```

### Ejecución Manual

```bash
# Ejecutar todos los hooks en todos los archivos
make pre-commit-run

# O manualmente
pre-commit run --all-files

# Ejecutar un hook específico
pre-commit run black --all-files
pre-commit run prettier --all-files

# Ejecutar solo en archivos staged
pre-commit run
```

### Actualizar Hooks

Los hooks se actualizan automáticamente, pero puedes forzar actualización:

```bash
pre-commit autoupdate
```

## Configuración

El archivo de configuración está en `.pre-commit-config.yaml` en la raíz del proyecto.

### Agregar Nuevos Hooks

Edita `.pre-commit-config.yaml` y agrega un nuevo repositorio:

```yaml
repos:
  - repo: https://github.com/example/hook-repo
    rev: v1.0.0
    hooks:
      - id: hook-name
        files: ^path/to/files/.*\.ext$
```

Luego actualiza:

```bash
pre-commit install --install-hooks
```

### Deshabilitar un Hook Temporalmente

Comenta el hook en `.pre-commit-config.yaml`:

```yaml
# - repo: https://github.com/example/hook-repo
#   hooks:
#     - id: hook-name
```

## Troubleshooting

### Mensaje de Commit Inválido

Si el mensaje de commit no sigue el formato de Conventional Commits:

```bash
# ❌ Mensaje inválido
git commit -m "agregar feature"
# Error: commit message does not follow conventional commits format

# ✅ Mensaje válido
git commit -m "feat: agregar nueva funcionalidad"
```

Ver [Conventional Commits Guide](./CONVENTIONAL_COMMITS.md) para el formato correcto.

### Hook Falla en Commit

Si un hook falla, el commit se cancela. Revisa los errores y corrígelos:

```bash
# Ver errores
pre-commit run --all-files

# Corregir automáticamente (si el hook lo soporta)
# Ej: Black, isort, ruff, prettier, eslint tienen auto-fix
```

### Saltar Hooks (No Recomendado)

Solo en casos excepcionales:

```bash
git commit --no-verify
```

⚠️ **Advertencia**: Esto puede comprometer la calidad del código.

### Hook es Muy Lento

Algunos hooks pueden ser lentos (ej: type checking, tests). Considera:

1. **Ejecutar solo en archivos modificados**: Los hooks por defecto solo procesan archivos staged
2. **Mover hooks lentos a pre-push**: Edita `.pre-commit-config.yaml` y agrega `stages: [pre-push]`
3. **Usar caché**: Pre-commit cachea resultados automáticamente

### Problemas con Dependencias

Si un hook falla por dependencias faltantes:

```bash
# Reinstalar hooks
pre-commit uninstall
pre-commit install

# O actualizar dependencias
pre-commit autoupdate
```

### Frontend: npm Scripts Faltantes

Si el hook de TypeScript falla, asegúrate de tener el script en `package.json`:

```json
{
  "scripts": {
    "type-check": "tsc --noEmit"
  }
}
```

## Mejores Prácticas

1. **No saltar hooks**: Siempre corrige los errores antes de commitear
2. **Ejecutar manualmente antes de push**: `pre-commit run --all-files`
3. **Mantener hooks actualizados**: `pre-commit autoupdate` periódicamente
4. **Agregar hooks nuevos con cuidado**: Asegúrate de que sean rápidos y útiles
5. **Documentar hooks custom**: Si agregas hooks personalizados, documenta su propósito

## Integración con CI/CD

Los hooks de pre-commit también se pueden ejecutar en CI/CD:

```yaml
# .github/workflows/ci.yml
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

Esto asegura que el código en el repositorio siempre cumple con los estándares.

## Recursos

- [Pre-commit Documentation](https://pre-commit.com/)
- [Pre-commit Hooks Repository](https://github.com/pre-commit/pre-commit-hooks)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Prettier Documentation](https://prettier.io/)
- [ESLint Documentation](https://eslint.org/)

