# TASKS — Plan de ejecución paso a paso

Lista ordenada de tareas atómicas para ejecutar las features 003, 002, 004 y 005. La feature 001 (PDFs de presupuesto) queda pendiente para una sesión dedicada con la plantilla de Canva del socio.

## Cómo usar este archivo (instrucciones para el agente que ejecuta)

1. **Leer primero**: `CLAUDE.md` (raíz), `AGENTS.md`, `ARCHITECTURE.md`, y los docs de skills relevantes en `docs/agents/skills/`.
2. **Pickear la siguiente tarea**: la primera `[ ]` cuyas dependencias estén todas en `[x]`.
3. **Antes de codear**: leer el doc de planning referenciado en cada tarea (`docs/planning/00X-*.md`) en la sección indicada. Eso da el contexto.
4. **Ejecutar**: hacer SOLO los pasos listados. No hacer cambios fuera del scope de la tarea (refactors, otros archivos, etc).
5. **Validar**: verificar el "Done" de la tarea antes de seguir.
6. **Marcar**: cambiar `[ ]` → `[x]` en este archivo.
7. **Commit**: un commit por tarea. Mensaje: `feat(<area>): <título de la tarea>`. Si la tarea explícitamente dice "no commitear hasta...", esperar.
8. **Si una tarea falla**: NO improvisar — anotar el problema en una sección "Notas" al final del archivo y parar.

## Convenciones

- **Backend**: `uv` para deps, alembic para migrations, modelo registrado en `app/models.py`, router registrado en `app/custom/features/__init__.py::get_custom_routers()`.
- **Frontend**: regenerar `lib/api/types.ts` después de cambios de schema (`make frontend-api-types`, backend tiene que estar corriendo).
- **No magic strings**: constantes en `constants.py` backend, mensajes en módulos dedicados frontend.
- **No `# noqa`** sin justificación escrita.
- **Sin comentarios** que expliquen el QUÉ del código (los identificadores ya lo dicen).

---

## Feature 003 — Presupuestos: validez 10 días

**Doc**: `docs/planning/003-presupuestos-validez.md`
**Orden**: primera, es la más chica.

### [x] T-003-1: Constante `PROPOSAL_VALIDITY_DAYS`

- **Depende de**: nada
- **Doc**: 003, sección "Service / lógica"
- **Archivos**: `backend/app/custom/features/proposals/constants.py` (crear si no existe)
- **Pasos**:
  1. Crear `constants.py` en `backend/app/custom/features/proposals/` si no existe.
  2. Agregar: `PROPOSAL_VALIDITY_DAYS: int = 10`.
- **Done**: constante importable desde el service.

### [x] T-003-2: Agregar `sent_at` al modelo `Proposal`

- **Depende de**: T-003-1
- **Doc**: 003, sección "Datos / migrations"
- **Archivos**: `backend/app/custom/features/proposals/models.py`
- **Pasos**:
  1. Agregar columna: `sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)`.
  2. Posicionarla después de `updated_at`.
- **Done**: modelo compila, `python -c "from app.custom.features.proposals.models import Proposal"` sin errores.

### [x] T-003-3: Migration `sent_at` con backfill

- **Depende de**: T-003-2
- **Doc**: 003, sección "Datos / migrations"
- **Archivos**: `backend/alembic/versions/<nueva>.py`
- **Pasos**:
  1. `cd backend && uv run alembic revision --autogenerate -m "add sent_at to proposals"`.
  2. Revisar la migration: debe tener `op.add_column('proposals', sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True))`.
  3. Agregar manualmente al `upgrade()`, después del `add_column`, el backfill: `op.execute("UPDATE proposals SET sent_at = updated_at WHERE status IN ('sent', 'accepted', 'rejected')")`.
  4. `uv run alembic upgrade head`.
  5. Verificar en DB: `SELECT id, status, sent_at FROM proposals` — los pre-existentes en estado sent/accepted/rejected tienen sent_at != NULL.
- **Done**: migration aplicada, backfill funcionó.

### [x] T-003-4: Service setea `sent_at` automático

- **Depende de**: T-003-3
- **Doc**: 003, sección "Service / lógica"
- **Archivos**: `backend/app/custom/features/proposals/service.py`
- **Pasos**:
  1. Identificar el método que cambia status (probablemente `update_status` o similar — leer el service primero).
  2. Después del cambio de status y antes del commit, agregar:
     - Si nuevo status es `sent` o `accepted` y `proposal.sent_at` es None → setear `sent_at = datetime.now(timezone.utc)`.
     - Si nuevo status es `sent` y old status era `draft` → actualizar `sent_at = datetime.now(timezone.utc)`.
  3. NO modificar otros flujos del service.
- **Done**: cambiar status de un draft a sent (vía API o test) deja `sent_at` con timestamp actual.

### [x] T-003-5: Schema response con `sent_at` y `days_until_expiry`

- **Depende de**: T-003-4
- **Doc**: 003, sección "API"
- **Archivos**: `backend/app/custom/features/proposals/schemas.py`
- **Pasos**:
  1. Agregar `sent_at: datetime | None` al `ProposalResponse`.
  2. Agregar `days_until_expiry: int | None` al `ProposalResponse`.
  3. En el service o repository, computar `days_until_expiry`: si `sent_at` es None → None; si no, `(sent_at + timedelta(days=PROPOSAL_VALIDITY_DAYS) - now()).days`.
  4. Importar `PROPOSAL_VALIDITY_DAYS` desde `constants.py`.
- **Done**: response del endpoint `GET /api/v1/proposals/{id}` incluye ambos campos.

### [x] T-003-6: Test backend de set `sent_at`

- **Depende de**: T-003-5
- **Doc**: 003, sección "Criterios de done"
- **Archivos**: `backend/tests/custom/features/proposals/test_service.py` (o donde estén los tests del service)
- **Pasos**:
  1. Test 1: crear proposal en draft, cambiar a sent → `sent_at` no es None.
  2. Test 2: crear proposal en draft, cambiar directo a accepted → `sent_at` no es None.
  3. Test 3: cambiar de sent a draft y de vuelta a sent → `sent_at` se actualiza al timestamp más reciente.
- **Done**: tests pasan con `make test`.

### [x] T-003-7: Regenerar API types frontend

- **Depende de**: T-003-5
- **Doc**: CLAUDE.md, sección "Frontend API types"
- **Archivos**: `frontend/lib/api/types.ts` (autogenerado, NO editar a mano)
- **Pasos**:
  1. Asegurar backend corriendo (`make dev` + `cd backend && uv run uvicorn app.main:app --reload`).
  2. `make frontend-api-types`.
  3. Verificar que `types.ts` ahora incluye `sent_at` y `days_until_expiry` en los tipos de proposal.
- **Done**: types regenerados sin edit manual.

### [x] T-003-8: Componente `ValidityBadge`

- **Depende de**: T-003-7
- **Doc**: 003, HU-V-2
- **Archivos**: `frontend/components/custom/features/proposals/validity-badge.tsx` (crear)
- **Pasos**:
  1. Componente recibe prop `daysUntilExpiry: number | null`.
  2. Si null: no renderiza nada.
  3. Si `> 5`: badge gris/azul "Vigente".
  4. Si `1..5`: badge ámbar "Vence en X días".
  5. Si `<= 0`: badge rojo "Vencido hace X días".
  6. Reusar el componente `Badge` de `core/ui/badge.tsx`.
  7. Strings en módulo de mensajes, NO inline.
- **Done**: componente renderiza correctamente los 4 estados al pasar valores de prueba (verificar visualmente o con storybook si existe).

### [x] T-003-9: Usar `ValidityBadge` en tabla de presupuestos

- **Depende de**: T-003-8
- **Doc**: 003, HU-V-2
- **Archivos**: `frontend/components/custom/features/proposals/proposals-table.tsx` (o equivalente)
- **Pasos**:
  1. Agregar columna nueva "Vigencia" (o integrar el badge inline en la columna de estado).
  2. Pasar `proposal.days_until_expiry` al componente.
- **Done**: tabla muestra el badge correcto en cada fila enviada.

### [x] T-003-10: Lint + build frontend

- **Depende de**: T-003-9
- **Archivos**: ninguno (solo verificar)
- **Pasos**:
  1. `cd frontend && npm run lint`.
  2. `cd frontend && npm run build`.
- **Done**: ambos pasan sin errores. Si hay warnings nuevos por el cambio, corregirlos.

---

## Feature 002 — Actividades

**Doc**: `docs/planning/002-actividades.md`
**Orden**: después de 003. Es la más grande.

### [x] T-002-0: Verificar / crear endpoint `GET /api/v1/users`

- **Depende de**: nada
- **Doc**: 002, sección "Riesgos / preguntas abiertas"
- **Archivos**: `backend/app/core/features/users/routes.py` (verificar)
- **Pasos**:
  1. Buscar si ya existe ruta `GET /api/v1/users` que devuelva la lista de usuarios.
  2. Si existe: verificar que devuelve al menos `id`, `name`, `email`. Marcar tarea done.
  3. Si NO existe: crear endpoint en `users` core que devuelva `list[UserListResponse]` con esos campos. **Ojo**: este es un cambio en `core/`, requiere ir por branch `dev` (ver CLAUDE.md "Git workflow"). Si el agente no puede hacer core changes, parar y avisar.
- **Done**: endpoint disponible y devuelve los campos requeridos.

### [x] T-002-1: Crear estructura backend de feature `activities`

- **Depende de**: nada
- **Doc**: 002, sección "Componentes"
- **Archivos**: `backend/app/custom/features/activities/__init__.py` (crear)
- **Pasos**:
  1. Crear directorio `backend/app/custom/features/activities/`.
  2. Crear archivos vacíos: `__init__.py`, `models.py`, `schemas.py`, `service.py`, `repository.py`, `routes.py`, `constants.py`.
- **Done**: estructura existe.

### [x] T-002-2: Constantes de `activities`

- **Depende de**: T-002-1
- **Doc**: 002, sección "Datos / migrations"
- **Archivos**: `backend/app/custom/features/activities/constants.py`
- **Pasos**:
  1. Definir `class ActivityOrigin(str, Enum)` con `MANUAL = "manual"`, `MEETING = "meeting"`.
  2. Definir mensajes de error/éxito (mensajes de la feature, no inline).
- **Done**: enum importable.

### [x] T-002-3: Modelo `Activity`

- **Depende de**: T-002-2
- **Doc**: 002, sección "Datos / migrations"
- **Archivos**: `backend/app/custom/features/activities/models.py`
- **Pasos**:
  1. Crear modelo `Activity` con todos los campos del doc 002 (sección "Datos / migrations").
  2. Usar `Mapped[...]` y tipos modernos (`int | None`, no `Optional`).
  3. FK `assignee_id` y `created_by_id` apuntan a `users.id` con `ON DELETE SET NULL`.
  4. Constraint único compuesto: `UniqueConstraint('origin', 'external_id', name='uq_activity_origin_external')` (PostgreSQL ignora rows con `NULL` en columnas del UNIQUE por default — verificar; si no, usar índice parcial).
- **Done**: modelo compila.

### [x] T-002-4: Registrar modelo en `app/models.py`

- **Depende de**: T-002-3
- **Doc**: CLAUDE.md sección "Backend layout"
- **Archivos**: `backend/app/models.py`
- **Pasos**:
  1. Importar `Activity` desde `app.custom.features.activities.models`.
  2. Agregar a `__all__`.
- **Done**: import explícito y `__all__` actualizados.

### [x] T-002-5: Schemas Pydantic de `activities`

- **Depende de**: T-002-3
- **Doc**: 002, sección "API"
- **Archivos**: `backend/app/custom/features/activities/schemas.py`
- **Pasos**:
  1. `ActivityCreate`: `title`, `description?`, `due_date?`, `due_at?`, `assignee_id?`.
  2. `ActivityUpdate`: todos opcionales + `done_at?`.
  3. `ActivityResponse`: todos los campos del modelo + `assignee` y `created_by` como sub-objetos `UserMini` (id, name).
  4. `ReorderRequest`: `ids: list[int]`.
  5. `SyncResponse` (para doc 004 después): `synced`, `created`, `updated`, `removed`, `last_sync_at`.
- **Done**: schemas importables.

### [x] T-002-6: Repository de `activities`

- **Depende de**: T-002-5
- **Doc**: 002, sección "API"
- **Archivos**: `backend/app/custom/features/activities/repository.py`
- **Pasos**:
  1. CRUD básico: `list(filters)`, `get(id)`, `create(data)`, `update(id, data)`, `delete(id)`.
  2. Método `bulk_update_sort_order(ids: list[int])`.
  3. Filtros en `list()`: `assignee_id`, `show_done`, `week=current` (lunes-domingo de la semana actual), `origin`.
- **Done**: métodos importables y testeable manualmente vía REPL.

### [x] T-002-7: Service de `activities`

- **Depende de**: T-002-6
- **Doc**: 002, secciones "API" y "Riesgos"
- **Archivos**: `backend/app/custom/features/activities/service.py`
- **Pasos**:
  1. Inyecta repository.
  2. `create(data, current_user)`: setea `created_by_id = current_user.id`. Si `assignee_id` no viene, queda NULL.
  3. `update(id, data, current_user)`: actualiza solo campos provistos. Si `done_at` se manda como `True`/`now`, lo setea; si `False`/`None`, lo limpia.
  4. `delete(id)`.
  5. `reorder(ids: list[int])`: actualiza sort_order = position en el array.
  6. Validación: las activities con `origin=meeting` solo permiten editar `done_at`, `sort_order`, `assignee_id`. Si vienen otros campos en update, ignorarlos o rechazar (decidir: rechazar con 400 más claro).
- **Done**: service compila y maneja todos los casos.

### [x] T-002-8: Routes de `activities`

- **Depende de**: T-002-7
- **Doc**: 002, sección "API"
- **Archivos**: `backend/app/custom/features/activities/routes.py`
- **Pasos**:
  1. Router con prefix `/api/v1/activities`, tag `Activities`.
  2. Endpoints: GET (con query params), POST, PATCH `/{id}`, DELETE `/{id}`, POST `/reorder`.
  3. Cada endpoint usa `Depends(get_current_user)` para auth.
  4. Mensajes de error desde `constants.py`.
- **Done**: rutas declaradas.

### [x] T-002-9: Registrar router en `custom/features/__init__.py`

- **Depende de**: T-002-8
- **Doc**: CLAUDE.md, sección "Backend layout"
- **Archivos**: `backend/app/custom/features/__init__.py`
- **Pasos**:
  1. Agregar import `activities_router`.
  2. Agregar a la lista `routers`.
- **Done**: router registrado.

### [x] T-002-10: Migration `activities`

- **Depende de**: T-002-9
- **Doc**: 002, sección "Datos / migrations"
- **Archivos**: `backend/alembic/versions/<nueva>.py`
- **Pasos**:
  1. `cd backend && uv run alembic revision --autogenerate -m "create activities table"`.
  2. Revisar: tabla con todas las columnas, FKs, unique constraint.
  3. `uv run alembic upgrade head`.
  4. Verificar en DB: `\d activities` muestra la estructura.
- **Done**: tabla creada en DB.

### [x] T-002-11: Tests backend mínimos

- **Depende de**: T-002-10
- **Doc**: 002, "Criterios de done"
- **Archivos**: `backend/tests/custom/features/activities/test_routes.py` (crear)
- **Pasos**:
  1. Test: crear activity con todos los campos.
  2. Test: editar activity (cambia título).
  3. Test: marcar hecha (set `done_at`).
  4. Test: eliminar.
  5. Test: filtro `?show_done=true` y `?show_done=false`.
  6. Test: reorder cambia sort_order correctamente.
- **Done**: `make test` pasa, cobertura >80%.

### [x] T-002-12: Regenerar API types frontend

- **Depende de**: T-002-11
- **Doc**: CLAUDE.md, sección "Frontend API types"
- **Archivos**: `frontend/lib/api/types.ts` (autogenerado)
- **Pasos**:
  1. Backend corriendo.
  2. `make frontend-api-types`.
- **Done**: types incluyen `Activity`, `ActivityCreate`, etc.

### [ ] T-002-13: Server actions `activities.ts`

- **Depende de**: T-002-12
- **Doc**: 002, sección "Componentes"
- **Archivos**: `frontend/app/actions/custom/activities.ts` (crear)
- **Pasos**:
  1. Funciones: `listActivities(filters)`, `createActivity(data)`, `updateActivity(id, data)`, `deleteActivity(id)`, `reorderActivities(ids)`.
  2. Cada una usa `'use server'`, types de `lib/api/types.ts`.
  3. Error handling: try/catch con throw para que el componente lo capture.
- **Done**: funciones tipadas y exportadas.

### [ ] T-002-14: Componente `AssigneeSelector`

- **Depende de**: T-002-13 (y T-002-0)
- **Doc**: 002, HU-A-2
- **Archivos**: `frontend/components/custom/features/activities/assignee-selector.tsx`
- **Pasos**:
  1. Server action `getUsers()` (en actions/custom o core, según donde esté el endpoint).
  2. Componente client-side con dropdown (reusar `Select` de shadcn).
  3. Muestra: avatar (si hay) + nombre. Opción "Sin asignar".
- **Done**: selector funcional, integrable en otros forms.

### [ ] T-002-15: Componente `ActivityFormDialog`

- **Depende de**: T-002-14
- **Doc**: 002, HU-A-2 y HU-A-3
- **Archivos**: `frontend/components/custom/features/activities/activity-form-dialog.tsx`
- **Pasos**:
  1. Dialog (shadcn) con form: título, descripción, due_date (date picker), assignee (selector).
  2. Modo `create` y `edit`.
  3. Validación: título requerido.
  4. Botones: Cancelar / Guardar (Crear o Actualizar según modo).
  5. Toast en éxito y error.
- **Done**: crear y editar funcionan end-to-end.

### [ ] T-002-16: Componente `ActivitiesTable` (página)

- **Depende de**: T-002-15
- **Doc**: 002, HU-A-1
- **Archivos**: `frontend/components/custom/features/activities/activities-table.tsx`
- **Pasos**:
  1. TanStack Table con columnas: checkbox done, drag-handle, título, descripción corta, vencimiento, asignado (avatar+nombre), origen (badge), acciones.
  2. Filtros: assignee (selector), show_done (toggle), origen (selector multi).
  3. Búsqueda por título.
  4. Drag-and-drop con `dnd-kit` (mismo patrón que la `DataTable` core).
  5. Acciones por fila: Editar (abre dialog), Eliminar (AlertDialog).
- **Done**: tabla funcional con todos los filtros y acciones.

### [ ] T-002-17: Página `/actividades`

- **Depende de**: T-002-16
- **Doc**: 002, sección "UI / pantallas"
- **Archivos**: `frontend/app/(private)/(custom)/actividades/page.tsx`
- **Pasos**:
  1. Página server component que fetchea activities iniciales.
  2. Renderiza header "Actividades" + botón "+ Nueva actividad" + `ActivitiesTable`.
  3. Agregar entrada en el sidebar de navegación (verificar dónde se declara el sidebar — `frontend/components/custom/...` o similar).
- **Done**: navegando a `/actividades` se ve la tabla, se pueden hacer todas las operaciones.

### [ ] T-002-18: Componente `WeekActivitiesWidget`

- **Depende de**: T-002-16
- **Doc**: 002, HU-A-4
- **Archivos**: `frontend/components/custom/features/activities/week-activities-widget.tsx`
- **Pasos**:
  1. Componente que recibe `activities: Activity[]` filtradas a la semana actual.
  2. Renderiza con la **misma estética** que la `DataTable` core actual: mismo row height, columnas, drag-handle, badges. Reusar primitives visuales (`Table`, `Badge`, etc.).
  3. Toggle "Solo mías" (default off, muestra todas).
  4. Click en una fila → `router.push('/actividades')`.
  5. Drag-and-drop persiste sort_order vía server action.
- **Done**: visualmente idéntico al DataTable actual del dashboard pero con datos reales.

### [ ] T-002-19: Wire widget en dashboard

- **Depende de**: T-002-18
- **Doc**: 002, sección "Componentes"
- **Archivos**: `frontend/app/(private)/page.tsx`
- **Pasos**:
  1. Importar `WeekActivitiesWidget`.
  2. Reemplazar `<DataTable data={data} />` por `<WeekActivitiesWidget activities={...} />`.
  3. Quitar import de `DataTable` y de `data.json`.
  4. Server-side fetch de activities de la semana actual.
- **Done**: dashboard muestra las activities reales, el resto del dashboard sigue pixel-igual.

### [ ] T-002-20: Lint + build frontend + tests backend

- **Depende de**: T-002-19
- **Pasos**:
  1. `make lint` (debe pasar).
  2. `make test` (debe pasar).
  3. `cd frontend && npm run build` (debe pasar).
- **Done**: todo verde.

---

## Feature 004 — Google Calendar sync

**Doc**: `docs/planning/004-google-calendar.md`
**Orden**: después de 002 (necesita la tabla `activities`).

### [ ] T-004-1: Agregar dependencia `google-api-python-client`

- **Depende de**: T-002-20
- **Doc**: 004, sección "Datos / migrations"
- **Archivos**: `backend/pyproject.toml`, `backend/uv.lock`
- **Pasos**:
  1. `cd backend && uv add google-api-python-client google-auth`.
  2. Commit ambos archivos.
- **Done**: deps instaladas, `import googleapiclient` funciona.

### [ ] T-004-2: Variables de entorno

- **Depende de**: T-004-1
- **Doc**: 004, sección "Datos / migrations"
- **Archivos**: `backend/app/core/config.py` (o donde estén las settings), `.env.example`
- **Pasos**:
  1. Agregar a settings: `GOOGLE_CALENDAR_ID: str | None`, `GOOGLE_SERVICE_ACCOUNT_JSON: str | None`.
  2. Documentar en `.env.example` con valores placeholder y comentario.
  3. Constantes en `activities/constants.py`: `GOOGLE_CALENDAR_SYNC_RANGE_DAYS_BACK = 7`, `GOOGLE_CALENDAR_SYNC_RANGE_DAYS_FORWARD = 30`.
- **Done**: settings cargadas, app no rompe si vienen None (sync simplemente devuelve error claro).

### [ ] T-004-3: Servicio `CalendarSyncService`

- **Depende de**: T-004-2
- **Doc**: 004, sección "Comportamiento del sync"
- **Archivos**: `backend/app/custom/features/activities/calendar_sync.py` (crear)
- **Pasos**:
  1. Class `CalendarSyncService` con método `sync()` que devuelve un dict con `synced`, `created`, `updated`, `removed`, `last_sync_at`.
  2. Lee eventos de Google Calendar usando service account credentials.
  3. Para cada evento: upsert en activities con `origin=meeting`, `external_id=event.id`.
  4. Eventos no presentes en calendar (vs los locales con origin=meeting en el rango) → marcar `done_at = now()`.
  5. Manejo de errores: credenciales inválidas, calendar no encontrado — raise `CalendarSyncError` con mensaje claro.
- **Done**: clase importable, lógica testeable con cliente mockeado.

### [ ] T-004-4: Endpoint `POST /api/v1/activities/sync-calendar`

- **Depende de**: T-004-3
- **Doc**: 004, sección "API"
- **Archivos**: `backend/app/custom/features/activities/routes.py`
- **Pasos**:
  1. Endpoint usa `CalendarSyncService.sync()`.
  2. Devuelve `SyncResponse` schema (definido en T-002-5).
  3. Errores de sync devuelven 502 con detail.
- **Done**: endpoint funcional. Probar manualmente con un calendar de prueba.

### [ ] T-004-5: Test `CalendarSyncService` con mock

- **Depende de**: T-004-4
- **Archivos**: `backend/tests/custom/features/activities/test_calendar_sync.py`
- **Pasos**:
  1. Test 1: evento nuevo → INSERT.
  2. Test 2: evento existente con cambio de título → UPDATE solo título.
  3. Test 3: evento existente con `done_at` y `assignee_id` puestos → UPDATE no toca esos campos.
  4. Test 4: evento local con origin=meeting que ya no está en calendar → marcado `done_at`.
  5. Test 5: dos llamadas seguidas con mismos eventos → idempotente, no duplica.
- **Done**: tests pasan.

### [ ] T-004-6: Server action y botón frontend

- **Depende de**: T-004-5
- **Doc**: 004, sección "UI"
- **Archivos**: `frontend/app/actions/custom/activities.ts`, `frontend/components/custom/features/activities/calendar-sync-button.tsx`
- **Pasos**:
  1. Server action `syncCalendar()` que llama al endpoint.
  2. Componente botón con icono refresh + label "Sincronizar reuniones".
  3. Loading state durante el request.
  4. Toast con resumen al terminar: "Sincronizado: X nuevas, Y actualizadas, Z canceladas".
  5. Error toast con mensaje claro.
- **Done**: botón funcional en `/actividades`.

### [ ] T-004-7: Indicador "Última sincronización"

- **Depende de**: T-004-6
- **Doc**: 004, sección "UI"
- **Archivos**: `frontend/components/custom/features/activities/calendar-sync-button.tsx`
- **Pasos**:
  1. Mostrar al lado del botón: "Última sincronización: hace X minutos".
  2. Persistir `last_sync_at` en localStorage (no necesitamos backend para esto).
  3. Si nunca se sincronizó: "Nunca sincronizado".
- **Done**: indicador actualizado tras cada sync.

### [ ] T-004-8: Documentación de setup

- **Depende de**: T-004-7
- **Archivos**: `README.md` o `docs/setup/google-calendar.md`
- **Pasos**:
  1. Documentar paso a paso: crear service account en Google Cloud, descargar JSON, compartir el calendar centralizado con el email del service account, setear las env vars.
- **Done**: README/docs claro y reproducible.

---

## Feature 005 — Calidad batch

**Doc**: `docs/planning/005-calidad-batch.md`
**Orden**: cierre de la temporada.

### [ ] T-005-1: Toggle "Incluir anuladas" en filtros de facturas

- **Depende de**: nada
- **Doc**: 005, sección "005-A"
- **Archivos**: `frontend/components/custom/features/invoices/invoices-table.tsx`
- **Pasos**:
  1. Agregar Toggle/Checkbox "Incluir anuladas" en la toolbar.
  2. Estado por defecto: false.
  3. Cuando false: filtra rows con `cancelled_at !== null` (X) y `cancelled_by_invoice_id !== null` (AFIP con NC).
  4. Cuando true: muestra todo (estado actual).
- **Done**: toggle funciona, anuladas se ocultan por defecto, aparecen al activar.

### [ ] T-005-2: Migration `UNIQUE(client_id, email)` en `client_emails`

- **Depende de**: nada
- **Doc**: 005, sección "005-B"
- **Archivos**: `backend/alembic/versions/<nueva>.py`, `backend/app/custom/features/clients/service.py`
- **Pasos**:
  1. Crear migration con: 1) cleanup de duplicados (mantener el más viejo): `DELETE FROM client_emails WHERE id NOT IN (SELECT MIN(id) FROM client_emails GROUP BY client_id, email)`. 2) `ALTER TABLE client_emails ADD CONSTRAINT uq_client_emails_client_email UNIQUE (client_id, email)`.
  2. Aplicar migration.
  3. En el service de clients, capturar `IntegrityError` al insertar email y devolver mensaje "Ese email ya está cargado para este cliente" en lugar del error genérico.
- **Done**: migration aplicada, intentar duplicar email da mensaje claro.

### [ ] T-005-3: Sequence Postgres para numeración X

- **Depende de**: nada
- **Doc**: 005, sección "005-C"
- **Archivos**: `backend/alembic/versions/<nueva>.py`, `backend/app/custom/features/invoices/service.py`
- **Pasos**:
  1. Migration: `op.execute("CREATE SEQUENCE IF NOT EXISTS invoices_internal_number_seq")`. Setear `START WITH` al `MAX(internal_number) + 1` actual: `op.execute("SELECT setval('invoices_internal_number_seq', COALESCE((SELECT MAX(internal_number) FROM invoices WHERE is_internal = true), 0) + 1, false)")`.
  2. En el service, donde se calcula el siguiente `internal_number`, reemplazar por `db.execute(text("SELECT nextval('invoices_internal_number_seq')")).scalar()`.
  3. Test: dos calls concurrentes (o consecutivas en test) no devuelven el mismo número.
- **Done**: nuevo X usa sequence, números siguen correlativos.

### [ ] T-005-4: Lint pre-existente en `app/main.py`

- **Depende de**: nada
- **Doc**: 005, sección "005-D"
- **Archivos**: `backend/app/main.py`
- **Pasos**:
  1. `cd backend && uv run black app/main.py && uv run isort app/main.py`.
  2. `cd backend && uv run ruff check app/main.py`.
  3. Corregir los issues que queden.
  4. `make lint` debe pasar.
- **Done**: `make lint` pasa.

### [ ] T-005-5: Verificación final

- **Depende de**: T-005-1, T-005-2, T-005-3, T-005-4
- **Pasos**:
  1. `make lint`.
  2. `make test`.
  3. `cd frontend && npm run build`.
  4. Smoke test manual: crear cliente con email duplicado → mensaje claro. Crear comprobante X → numeración correcta. Filtrar facturas con/sin anuladas → comportamiento correcto.
- **Done**: todo verde, sin regresiones.

---

## Notas

(Si una tarea falla o tiene un problema imprevisto, agregar acá una entrada con: ID de tarea, qué pasó, qué se intentó, y parar la ejecución.)
