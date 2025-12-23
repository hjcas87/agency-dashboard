# Users Feature

Feature ejemplo completo que demuestra la arquitectura por features con CRUD completo.

## Estructura

```
users/
├── models.py      # Modelo SQLAlchemy
├── schemas.py     # Schemas Pydantic
├── repository.py  # Repository con métodos custom
├── service.py     # Service con lógica de negocio
├── routes.py      # Endpoints FastAPI
└── README.md      # Esta documentación
```

## Endpoints

- `POST /api/v1/users` - Crear usuario
- `GET /api/v1/users` - Listar usuarios (con paginación, filtros, búsqueda)
- `GET /api/v1/users/{id}` - Obtener usuario por ID
- `PUT /api/v1/users/{id}` - Actualizar usuario
- `DELETE /api/v1/users/{id}` - Eliminar usuario

## Características

- ✅ CRUD completo
- ✅ Validación de email único
- ✅ Búsqueda por nombre o email
- ✅ Filtro de usuarios activos
- ✅ Paginación
- ✅ Manejo de errores apropiado
- ✅ Tests completos (unit, integration, e2e)

## Uso

```python
# Crear usuario
POST /api/v1/users
{
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true
}

# Listar usuarios
GET /api/v1/users?skip=0&limit=10&active_only=true&search=John

# Obtener usuario
GET /api/v1/users/1

# Actualizar usuario
PUT /api/v1/users/1
{
  "name": "Jane Doe"
}

# Eliminar usuario
DELETE /api/v1/users/1
```

## Tests

Ver `tests/integration/api/test_users_routes.py` y `tests/integration/features/test_users_feature.py` para ejemplos de tests.

