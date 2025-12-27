# Guía de Extensión

Esta guía explica cómo extender el boilerplate para crear funcionalidad específica de cliente sin romper la capacidad de actualizar desde el repositorio original.

## Principio Fundamental

**Nunca modifiques código en `core/`**. Todo el código personalizado debe ir en `custom/`.

## Estructura de Directorios

```
app/
├── core/          # ❌ NO MODIFICAR - Actualizado desde repo original
├── custom/        # ✅ MODIFICAR AQUÍ - Código específico del cliente
└── shared/        # ⚠️ USAR CON PRECAUCIÓN - Código compartido
```

## Extender el Backend

### Agregar Nuevos Endpoints

1. Crear router en `backend/app/custom/api/router.py`:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-endpoint")
async def my_custom_endpoint():
    return {"message": "Custom endpoint"}
```

2. El router se incluye automáticamente en `app/core/router.py` si existe.

### Agregar Modelos de Base de Datos

1. Crear modelos en `backend/app/custom/features/<feature>/models.py`:

```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class CustomModel(Base):
    __tablename__ = "custom_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

2. Importar en `backend/app/models.py` para asegurar que SQLAlchemy puede resolver relaciones

3. **CRÍTICO**: Crear migración con Alembic:

```bash
cd backend
uv run alembic revision --autogenerate -m "Add custom model"
uv run alembic upgrade head
```

**⚠️ REGLA CRÍTICA**: Los modelos SQLAlchemy DEBEN estar siempre sincronizados con las tablas de la base de datos:
- **SIEMPRE** crear migraciones al modificar modelos
- **NUNCA** modificar modelos sin actualizar la base de datos mediante migraciones
- **SIEMPRE** ejecutar `alembic upgrade head` después de crear/modificar migraciones
- Si hay discrepancias, corregirlas inmediatamente mediante migraciones o ajustando el modelo

### Agregar Tareas Celery Personalizadas

**IMPORTANTE**: Las tasks deben ser autocontenidas dentro de cada feature, no en un módulo centralizado.

1. Crear tareas en `backend/app/custom/features/<feature>/tasks.py`:

```python
from app.core.tasks.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def my_custom_task(self, data):
    # Tu lógica aquí
    return {"result": "success"}
```

2. Celery descubrirá automáticamente las tasks usando `autodiscover_tasks` configurado en `celery_app.py`

**Estructura correcta:**
```
backend/app/custom/features/
└── my_feature/
    ├── routes.py
    ├── service.py
    └── tasks.py  # ✅ Tasks aquí, dentro del feature
```

**❌ Incorrecto:**
```
backend/app/custom/tasks/  # ❌ NO crear módulo centralizado
```

## Extender el Frontend

### Agregar Componentes Personalizados

1. Crear componentes en `frontend/components/custom/`:

```tsx
// frontend/components/custom/MyComponent.tsx
export function MyComponent() {
  return <div>Custom Component</div>
}
```

2. Usar en tus páginas:

```tsx
import { MyComponent } from '@/components/custom/MyComponent'
```

### Agregar Páginas Personalizadas

1. Crear páginas en `frontend/app/`:

```tsx
// frontend/app/custom/page.tsx
export default function CustomPage() {
  return <div>Custom Page</div>
}
```

## Actualizar desde el Repo Original

Cuando quieras actualizar el código core desde el repositorio original:

1. Agregar el repo original como remoto:

```bash
git remote add upstream https://github.com/original-repo/core.git
```

2. Fetch y merge:

```bash
git fetch upstream
git merge upstream/main
```

3. Resolver conflictos si los hay (solo deberían aparecer en `custom/`)

4. Los cambios en `core/` se aplicarán automáticamente

## Mejores Prácticas

1. **Separación clara**: Mantén `core/` y `custom/` completamente separados
2. **No importar desde core**: Evita importar internals de `core/` que puedan cambiar
3. **Usar interfaces públicas**: Usa solo las APIs públicas expuestas por `core/`
4. **Documentar extensiones**: Documenta tus extensiones en `custom/README.md`
5. **Tests**: Agrega tests para tu código custom en `custom/tests/`

## Ejemplos Completos

Ver los READMEs en:
- `backend/app/custom/README.md`
- `frontend/components/custom/README.md`

