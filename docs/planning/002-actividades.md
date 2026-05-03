# 002 — Actividades

## Estado: pendiente
## Depende de: 003 (opcional, alimenta sugerencias auto)
## Bloquea: 004 (Google Calendar)

## Contexto

Hoy la `DataTable` del dashboard renderiza `data.json` placeholder. La pensamos como punto de entrada a un módulo de **Actividades**: una bandeja compartida entre los miembros de la agencia con cosas pendientes — llamados a clientes, recordatorios de seguimiento, reuniones, "presupuestar X antes del viernes". Mezcla items manuales con (eventualmente) reuniones traídas de Google Calendar y sugerencias auto-derivadas del estado del negocio.

El término "Actividades" es estándar en CRMs comerciales (HubSpot, Salesforce, Pipedrive lo usan así en español) y cubre tanto tareas manuales como reuniones y seguimientos.

### ¿Por qué no Jira / Asana / Linear?

Evaluado y descartado para v1:

- **Overhead técnico**: OAuth + webhooks + suscripción para 2 usuarios y CRUD de 3 endpoints es desproporcionado.
- **Acoplamiento**: pegarnos a un vendor para algo que no usa epics, sprints, story points ni issues anidados es matar moscas a cañonazos.
- **Migración fácil**: nuestra tabla `activities` es trivial — si el día de mañana superamos lo que hace, exportamos a Jira sin drama.

Si en seis meses sentimos que el módulo nuestro queda chico, se reconsidera.

## User stories

### HU-A-1: Ver actividades en página dedicada

**Como** miembro de la agencia  
**Quiero** una página `/actividades` con todas las actividades pendientes y completadas  
**Para** tener un panel de control de pendientes propio y de mi socio

**Criterios:**
- Tabla con columnas: título, descripción corta, vencimiento, asignado a (avatar + nombre), origen (Manual / Reunión), estado.
- Filtros: por asignado (Mías / De [socio] / Todas), por estado (pendientes / completadas / todas), por origen.
- Búsqueda por título.
- Acciones: editar, eliminar, marcar/desmarcar hecha.
- Drag-and-drop para reordenar (persiste `sort_order`).

### HU-A-2: Crear actividad

**Como** miembro de la agencia  
**Quiero** crear una actividad con título, descripción opcional, fecha, asignado  
**Para** registrar pendientes míos o asignar al socio

**Criterios:**
- Botón "+ Nueva actividad" en la página y en el widget del dashboard.
- Dialog con: título (req), descripción (opcional), fecha objetivo (opcional), asignado a (selector de usuarios, por defecto = el usuario actual).
- "Asignado a" puede quedar vacío (`Sin asignar`).
- Al guardar: `created_by_id = currentUser.id` automático.
- Toast: "Actividad creada".

### HU-A-3: Editar / eliminar / reasignar

**Como** miembro de la agencia  
**Quiero** editar cualquier actividad (no solo las mías)  
**Para** que si mi socio no puede, yo pueda completarla o reasignarla

**Criterios:**
- **Toda actividad es editable por cualquier usuario** (no hay "privadas"). Decisión explícita: la agencia es chica y la confianza es total.
- Mismo dialog que creación, precargado.
- El selector de "asignado a" permite cambiar el assignee.
- Eliminar pide confirmación con AlertDialog.
- Las actividades con `origin=meeting` solo permiten marcar hecha y editar título/notas locales — la fecha y datos del evento vienen del calendar y se sobrescriben en cada sync.

### HU-A-4: Widget "Esta semana" en el dashboard

**Como** miembro de la agencia  
**Quiero** ver de un vistazo en el dashboard las actividades de la semana en curso  
**Para** no abrir `/actividades` cada vez que entro a la app

**Criterios:**
- El widget reemplaza el `DataTable` placeholder actual del dashboard.
- **Misma estética exacta** que el `DataTable` actual: mismo row height, columnas, badges, drag-handle. Es el mismo primitive visual con datos reales.
- Filtra: actividades con `due_date` entre lunes y domingo de la semana en curso, **o** sin fecha pero asignadas a mí.
- Por defecto muestra las de **todos los usuarios** (para que se vean también las del socio). Toggle "Solo mías" disponible.
- Click en una fila → navega a `/actividades` (no abre dialog inline en el widget).
- Drag-and-drop disponible en el widget (sincroniza `sort_order` con la página).

### HU-A-5 (v1.5, opcional): Sugerencias auto-derivadas

**Como** miembro de la agencia  
**Quiero** ver mezcladas en la actividad cosas que el sistema detecta solo  
**Para** no olvidarme de seguir un presupuesto enviado o enviar el PDF de una factura

**Criterios:**
- Computadas, no persistidas (al menos en v1.5). Endpoint dedicado `/activities/suggestions` que las devuelve.
- Reglas iniciales:
  - Presupuesto en `sent` hace 5–10 días → "Hacer seguimiento de [nombre]"
  - Presupuesto en `sent` hace >10 días → "Re-emitir o cerrar [nombre]"
  - Presupuesto en `accepted` con `remaining > 0` → "Facturar [nombre]"
  - Factura emitida hace >1 día sin email enviado → "Enviar factura por email a [cliente]"
- En la UI aparecen con badge "Sugerida" y NO son editables. Se pueden marcar hechas (silencia la sugerencia hasta que la condición vuelva a aparecer) o postpone 24h (localStorage).
- **Es opcional para v1**. Si llegamos solo con manual + reuniones, está bien.

## Alcance v1

- Tabla `activities` en backend, CRUD básico, multi-usuario.
- Página `/actividades` con tabla, filtros, drag-and-drop.
- Widget "Esta semana" en el dashboard reemplazando el `DataTable` placeholder.
- Selector de usuarios para assignee (necesita endpoint `GET /api/v1/users` listando usuarios — verificar si ya existe).
- Soporte de `origin` (`manual`, `meeting`) preparado en el modelo, pero solo `manual` se usa en v1. `meeting` se activa en doc 004.

## Fuera de alcance

- Sugerencias auto-derivadas (HU-A-5, queda v1.5).
- Notificaciones push/email cuando una actividad vence.
- Recurrencia ("todos los lunes hacer X").
- Múltiples asignados por actividad (uno solo en v1).
- Comentarios / threads sobre actividades.
- Adjuntos.
- Historial / audit log.
- Sync con Google Calendar (eso es doc 004).

## Datos / migrations

Nueva tabla `activities`:

| Campo           | Tipo                                        | Notas                                          |
| --------------- | ------------------------------------------- | ---------------------------------------------- |
| id              | int PK                                      |                                                |
| title           | varchar(255) NOT NULL                       |                                                |
| description     | text NULL                                   |                                                |
| due_date        | date NULL                                   | Solo fecha; las reuniones usan `due_at`        |
| due_at          | timestamptz NULL                            | Para items con hora (reuniones del calendar)   |
| assignee_id     | int FK users(id) ON DELETE SET NULL NULL    | NULL = sin asignar                             |
| created_by_id   | int FK users(id) ON DELETE SET NULL NULL    | Auto en creación                               |
| done_at         | timestamptz NULL                            | NULL = pendiente                               |
| sort_order      | int NOT NULL DEFAULT 0                      | Para drag-and-drop                             |
| origin          | enum('manual', 'meeting') NOT NULL DEFAULT 'manual' |                                        |
| external_id     | varchar(255) NULL                           | Idempotency key para sync de calendar          |
| created_at      | timestamptz NOT NULL DEFAULT now()          |                                                |
| updated_at      | timestamptz NOT NULL                        |                                                |

Constraint: `UNIQUE(origin, external_id) WHERE external_id IS NOT NULL` — para que el sync de Google Calendar sea idempotente.

## API

| Método | Endpoint                                   | Descripción                                        |
| ------ | ------------------------------------------ | -------------------------------------------------- |
| GET    | `/api/v1/activities`                       | Listar (filtros `?assignee_id`, `?show_done`, `?week=current`, `?origin`) |
| POST   | `/api/v1/activities`                       | Crear                                              |
| PATCH  | `/api/v1/activities/{id}`                  | Editar (incluye toggle `done_at`, reasignar)       |
| DELETE | `/api/v1/activities/{id}`                  | Eliminar                                           |
| POST   | `/api/v1/activities/reorder`               | Body: `{ ids: [int, int, ...] }` actualiza `sort_order` |

Para HU-A-5 (v1.5):

| Método | Endpoint                                   | Descripción                                        |
| ------ | ------------------------------------------ | -------------------------------------------------- |
| GET    | `/api/v1/activities/suggestions`           | Lista derivada (no persiste) de auto-actividades   |

Endpoint de soporte (verificar si existe en `core`):

| Método | Endpoint               | Descripción                                  |
| ------ | ---------------------- | -------------------------------------------- |
| GET    | `/api/v1/users`        | Lista usuarios (id, name, email, avatar_url) |

## UI / pantallas

- **`/actividades`** (nueva página, custom): tabla full con filtros, dialog de creación/edición.
- **Dashboard `/`**: widget "Esta semana" reemplaza `DataTable` placeholder.
- **Sin** sub-páginas de detalle: el dialog de edición es suficiente.

## Componentes

- `frontend/components/custom/features/activities/activities-table.tsx`
- `frontend/components/custom/features/activities/activity-form-dialog.tsx`
- `frontend/components/custom/features/activities/week-activities-widget.tsx` (en dashboard)
- `frontend/components/custom/features/activities/assignee-selector.tsx`
- `frontend/app/(private)/(custom)/actividades/page.tsx`
- `frontend/app/actions/custom/activities.ts`
- `backend/app/custom/features/activities/{models,schemas,service,repository,routes,constants}.py`

## Riesgos / preguntas abiertas

- **¿La DataTable `core/` queda muerta?** Sí, en este fork. La dejamos viva en `core/` por si otro fork la usa, pero el dashboard custom deja de importarla. Si nunca nadie la usa, en otra iteración se evalúa borrar.
- **`drag-and-drop`**: la `DataTable` actual usa `dnd-kit`. Reusamos esa librería (ya instalada).
- **Endpoint `/api/v1/users`**: hay que verificar si existe. Si no, se agrega como parte de esta feature (debería ir en `core/features/users/` ya que es generic).
- **Selector de usuarios** vs dropdown: si en algún momento somos 5+ usuarios, el dropdown se queda chico — en v1 con 2-3 usuarios funciona bien.
- **Reordenar entre `manual` y `meeting`**: ¿se pueden mezclar al reordenar? Sí, `sort_order` es global. Las meetings se reordenan junto con todo lo demás.

## Criterios de done v1

- [ ] Migration aplicada, modelo en `app/models.py`.
- [ ] CRUD funcional desde la API.
- [ ] Endpoint `/api/v1/users` disponible (creado o verificado).
- [ ] Página `/actividades` con tabla, filtros, dialog de creación/edición, drag-and-drop.
- [ ] Widget "Esta semana" en dashboard funcionando con misma estética que la `DataTable` original.
- [ ] Asignación funciona: cualquier usuario puede crear y reasignar actividades.
- [ ] Tipos de API regenerados en frontend (`npm run generate-api-types`).
- [ ] Lint + tests pasan.
- [ ] No rompe el resto del dashboard (chart + cards siguen pixel-igual).
