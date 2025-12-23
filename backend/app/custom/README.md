# Custom Modules

Este directorio está destinado a módulos personalizados específicos del cliente.

## Estructura Recomendada

Usa la arquitectura por **features** autocontenidos:

```
custom/
└── features/          # Features personalizados
    └── my_feature/
        ├── routes.py      # Endpoints FastAPI
        ├── schemas.py     # Schemas Pydantic
        ├── service.py     # Lógica de negocio
        ├── repository.py  # Acceso a datos (opcional)
        └── models.py      # Modelos SQLAlchemy (opcional)
```

## Ejemplo de Feature Custom

Ver `app/custom/features/README.md` para la guía completa.

Ejemplo básico:

```python
# app/custom/features/my_feature/routes.py
from fastapi import APIRouter
from app.custom.features.my_feature.schemas import MyFeatureRequest
from app.custom.features.my_feature.service import MyFeatureService

router = APIRouter(prefix="/my-feature", tags=["custom"])

@router.post("/endpoint")
async def my_endpoint(
    request: MyFeatureRequest,
    service: MyFeatureService = Depends(get_my_feature_service),
):
    return await service.process(request)
```

## Registro de Features

Registra tu feature en `app/custom/features/__init__.py`:

```python
from app.custom.features.my_feature.routes import router as my_feature_router
routers.append(my_feature_router)
```

## Notas Importantes

- Los módulos en `core/` NO deben modificarse en forks de clientes
- Todos los cambios personalizados deben ir en `custom/features/`
- Cada feature debe ser autocontenido con su propia estructura
- Al actualizar desde el repo original, los cambios en `custom/` se preservan
- Usa interfaces de `app/shared/interfaces/` cuando sea posible

