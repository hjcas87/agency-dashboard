# Decisiones Arquitectónicas

## Features vs Modules: ¿Por qué Features?

### Opción 1: Por Features (Actual) ✅

```
app/
├── core/
│   └── features/
│       ├── users/          # Feature completo
│       │   ├── routes.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── models.py
│       ├── n8n/
│       └── health/
└── custom/
    └── features/
        └── (features personalizados)
```

**Ventajas:**
- ✅ **Alta cohesión**: Todo relacionado con un feature está junto
- ✅ **Bajo acoplamiento**: Features independientes entre sí
- ✅ **Escalabilidad**: Fácil agregar nuevos features sin afectar otros
- ✅ **Trabajo en equipo**: Cada feature puede ser un equipo diferente
- ✅ **DDD friendly**: Alineado con Domain-Driven Design
- ✅ **Fácil de encontrar**: Todo de "users" está en un lugar
- ✅ **Mejor para forks**: Fácil copiar/eliminar features completos
- ✅ **Testing**: Tests por feature son más claros

**Desventajas:**
- ⚠️ Puede haber duplicación de código entre features (pero se resuelve con `shared/`)
- ⚠️ Requiere disciplina para no acoplar features

### Opción 2: Por Modules (Alternativa)

```
app/
├── core/
│   ├── routes/         # Todos los endpoints
│   │   ├── users.py
│   │   ├── n8n.py
│   │   └── health.py
│   ├── services/       # Toda la lógica de negocio
│   │   ├── users.py
│   │   ├── n8n.py
│   │   └── health.py
│   ├── repositories/   # Todo el acceso a datos
│   │   ├── users.py
│   │   └── ...
│   └── models/         # Todos los modelos
│       ├── users.py
│       └── ...
└── custom/
    └── (mismo patrón)
```

**Ventajas:**
- ✅ Organización por tipo de código (más tradicional)
- ✅ Fácil ver todas las rutas en un lugar
- ✅ Bueno para proyectos pequeños

**Desventajas:**
- ❌ **Baja cohesión**: Código relacionado está disperso
- ❌ **Alto acoplamiento**: Cambios afectan múltiples archivos
- ❌ **Difícil de escalar**: Con muchos features, se vuelve caótico
- ❌ **Difícil de encontrar**: Para ver "users" completo, hay que abrir 4+ archivos
- ❌ **Trabajo en equipo**: Conflictos frecuentes en archivos compartidos
- ❌ **No DDD friendly**: No refleja el dominio de negocio
- ❌ **Testing**: Tests más dispersos

## Decisión: Features ✅

**Razones principales:**

### 1. Escalabilidad
Con modules, cuando tienes 20+ features:
- `routes/` tiene 20+ archivos
- `services/` tiene 20+ archivos
- Difícil navegar y mantener

Con features:
- Cada feature es una carpeta autocontenida
- Fácil encontrar y trabajar con un feature específico

### 2. Trabajo en Equipo
Con modules:
- Dos desarrolladores trabajando en features diferentes editan los mismos archivos
- Conflictos de merge frecuentes

Con features:
- Cada desarrollador trabaja en su feature
- Menos conflictos

### 3. Fork y Extensión
Para un boilerplate que se forkeará:
- Con features: Copiar/eliminar features es trivial
- Con modules: Tienes que editar múltiples archivos en diferentes carpetas

### 4. Testing
Con features:
```python
tests/
└── integration/
    └── features/
        └── users/      # Todos los tests de users juntos
            ├── test_routes.py
            ├── test_service.py
            └── test_repository.py
```

Con modules:
```python
tests/
├── routes/
│   └── test_users.py
├── services/
│   └── test_users.py
└── repositories/
    └── test_users.py
```

### 5. Principio de Responsabilidad Única
Features respetan mejor el principio:
- Un feature = una responsabilidad de negocio
- Todo lo necesario para esa responsabilidad está junto

## Híbrido: Features + Shared

La mejor práctica es **Features + Shared**:

```
app/
├── core/
│   ├── features/       # Features autocontenidos
│   │   ├── users/
│   │   └── n8n/
│   └── shared/         # Código compartido
│       ├── interfaces/
│       ├── services/   # Servicios compartidos (Kafka, N8N)
│       └── repositories/  # BaseRepository
```

**Cuándo usar `shared/`:**
- Interfaces comunes (IMessageBroker, IExternalService)
- Servicios compartidos (KafkaBroker, N8NService)
- Repositorios base (BaseRepository)
- Utilidades comunes

**Cuándo usar `features/`:**
- Lógica de negocio específica
- Endpoints específicos
- Modelos de dominio
- Tests específicos

## Comparación Práctica

### Agregar un nuevo feature "orders"

**Con Features:**
```bash
mkdir -p app/core/features/orders
# Crear: routes.py, schemas.py, service.py, repository.py, models.py
# Todo en un lugar, autocontenido
```

**Con Modules:**
```bash
# Editar routes/orders.py
# Editar services/orders.py
# Editar repositories/orders.py
# Editar models/orders.py
# Registrar en múltiples lugares
```

### Eliminar un feature

**Con Features:**
```bash
rm -rf app/core/features/orders
# Listo, todo eliminado
```

**Con Modules:**
```bash
# Eliminar routes/orders.py
# Eliminar services/orders.py
# Eliminar repositories/orders.py
# Eliminar models/orders.py
# Limpiar imports en múltiples archivos
```

## Recomendación Final

**Usar Features** porque:
1. ✅ Mejor para proyectos escalables
2. ✅ Mejor para trabajo en equipo
3. ✅ Mejor para forks y extensiones
4. ✅ Mejor alineado con DDD
5. ✅ Más fácil de mantener y testear
6. ✅ Mejor para el caso de uso (boilerplate reutilizable)

**Modules** solo si:
- Proyecto muy pequeño (< 5 features)
- Equipo muy pequeño (1-2 desarrolladores)
- No se va a escalar

## Referencias

- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Feature Folders](https://khalilabadi.github.io/feature-folders.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

