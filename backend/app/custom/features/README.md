# Custom Features

Este directorio contiene features personalizados específicos del cliente.

## Estructura de un Feature

Cada feature debe ser autocontenido con la siguiente estructura:

```
feature_name/
├── __init__.py
├── routes.py          # Endpoints FastAPI
├── schemas.py         # Schemas Pydantic
├── service.py         # Lógica de negocio
├── repository.py      # Acceso a datos (opcional)
├── models.py          # Modelos SQLAlchemy (opcional)
└── README.md          # Documentación del feature
```

## Ejemplo de Feature

Ver `app/core/features/n8n/` como referencia de estructura.

## Registro de Features

Para registrar un feature custom, agregarlo en `app/custom/features/__init__.py`:

```python
from app.custom.features.my_feature.routes import router as my_feature_router
routers.append(my_feature_router)
```

## Mejores Prácticas

1. **Separación de responsabilidades**: Routes → Service → Repository → Model
2. **Dependency Injection**: Usar FastAPI dependencies para servicios
3. **Interfaces**: Usar interfaces de `app/shared/interfaces/` cuando sea posible
4. **Error Handling**: Manejar errores apropiadamente en cada capa
5. **Testing**: Agregar tests para cada feature

