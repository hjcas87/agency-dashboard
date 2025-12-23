# MVP Features - Funcionalidades Mínimas Viables

## Objetivo del MVP

El MVP debe demostrar que el boilerplate funciona correctamente y puede ser extendido fácilmente para nuevos clientes.

## Funcionalidades Core MVP

### 1. Health Check System ✅
- **Endpoint**: `GET /api/v1/health`
- **Propósito**: Verificar estado de todos los servicios
- **Checks**:
  - Database connectivity
  - Kafka connectivity
  - N8N connectivity
- **Tests**: Integration tests con mocks

### 2. N8N Integration ✅
- **Endpoints**:
  - `POST /api/v1/n8n/trigger` - Disparar workflow asíncrono
  - `GET /api/v1/n8n/task/{task_id}` - Estado de tarea
- **Propósito**: Demostrar integración con automatizaciones
- **Tests**: 
  - Unit tests del service
  - Integration tests con N8N mocked
  - Tests de Celery tasks

### 3. Feature Example (CRUD Básico)
- **Feature**: `users` o `items` como ejemplo
- **Endpoints**:
  - `GET /api/v1/users` - Listar
  - `GET /api/v1/users/{id}` - Obtener uno
  - `POST /api/v1/users` - Crear
  - `PUT /api/v1/users/{id}` - Actualizar
  - `DELETE /api/v1/users/{id}` - Eliminar
- **Propósito**: Demostrar arquitectura por features completa
- **Tests**:
  - Tests de repository
  - Tests de service
  - Tests de endpoints (integration)

### 4. Message Broker (Kafka)
- **Funcionalidad**: Publicar y consumir mensajes
- **Propósito**: Demostrar mensajería asíncrona
- **Tests**:
  - Tests del KafkaBroker
  - Tests de publicación/consumo
  - Tests de health check

### 5. Background Tasks
- **Funcionalidad**: Ejecutar tareas en background
- **Propósito**: Demostrar procesamiento asíncrono
- **Tests**:
  - Tests de Celery tasks
  - Tests de task status

## Funcionalidades Opcionales (Post-MVP)

- Autenticación y autorización (JWT)
- Rate limiting
- Caching
- Logging estructurado
- Métricas y observabilidad
- WebSockets
- File uploads

## Criterios de Éxito del MVP

1. ✅ Todos los servicios se levantan correctamente
2. ✅ Health check funciona y reporta estado real
3. ✅ Se puede disparar un workflow de N8N
4. ✅ Se puede hacer CRUD completo de una entidad
5. ✅ Se pueden publicar/consumir mensajes en Kafka
6. ✅ Background tasks se ejecutan correctamente
7. ✅ Todos los tests pasan
8. ✅ Documentación completa

## Priorización

**P0 (Must Have)**:
1. Health Check
2. N8N Integration básica
3. Feature Example (CRUD)

**P1 (Should Have)**:
4. Message Broker (Kafka)
5. Background Tasks

**P2 (Nice to Have)**:
6. Autenticación
7. Caching
8. Métricas

