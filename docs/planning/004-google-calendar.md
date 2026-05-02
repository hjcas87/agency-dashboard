# 004 — Google Calendar: sync de reuniones

## Estado: pendiente
## Depende de: 002 (necesita la tabla `activities` con `origin=meeting`)
## Bloquea: nada

## Contexto

La agencia centraliza las invitaciones a reuniones poniendo en CC una cuenta dedicada (ej. `agenda@miagencia.com`). Esa cuenta acumula los eventos de todos los miembros. Queremos traer esos eventos al panel de **Actividades** como ítems con `origin=meeting`, para que se vean junto con las tareas manuales en `/actividades` y en el widget "Esta semana" del dashboard.

**Volumen esperado**: bajo. No tenemos 100 reuniones por semana — son pocos eventos, sync manual es suficiente.

## Alcance v1

- Una cuenta de servicio de Google (Service Account o cuenta dedicada con OAuth) con acceso de lectura al calendar de la cuenta centralizada.
- Botón "Sincronizar reuniones" en `/actividades` (y opcionalmente en el dashboard) que dispara `POST /api/v1/activities/sync-calendar`.
- El backend lee los eventos del calendar (rango: hoy −7 días hasta +30 días), los upserta como `activities` con `origin=meeting` usando el `event_id` del calendar como `external_id`.
- Sync **manual**: no hay cron ni webhook en v1. El usuario aprieta el botón cuando quiera ver lo último.
- Read-only: nunca creamos, modificamos ni borramos eventos en Google Calendar.

## Fuera de alcance

- Sync automático (cron, webhook, push notifications de Google).
- Sync bidireccional (crear eventos desde la app).
- Múltiples calendarios (solo uno centralizado por ahora).
- Sync de calendarios personales por usuario.
- Asignación automática de reuniones a usuarios según invitados — todas quedan **sin asignar**, el usuario las reasigna manualmente si quiere.
- Manejo de eventos recurrentes complejos (cada instancia se trata como evento independiente).
- Notas de la reunión, attachments, links de Meet — solo título, descripción, fecha, hora.

## Datos / migrations

- **Ninguna nueva**. La tabla `activities` ya tiene `origin`, `external_id`, `due_at` (preparados en doc 002).
- Configuración (env vars):
  - `GOOGLE_CALENDAR_ID` — el calendar id de la cuenta centralizada.
  - `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` o `GOOGLE_SERVICE_ACCOUNT_JSON` — credenciales.
- Constante `GOOGLE_CALENDAR_SYNC_RANGE_DAYS_BACK = 7`, `..._FORWARD = 30` en `activities/constants.py`.

## API

| Método | Endpoint                              | Descripción                                              |
| ------ | ------------------------------------- | -------------------------------------------------------- |
| POST   | `/api/v1/activities/sync-calendar`    | Sincroniza eventos del calendar centralizado. Sin body.  |

Response:

```json
{
  "synced": 8,        // total de eventos procesados
  "created": 2,       // nuevos
  "updated": 5,       // actualizados (cambio de hora, título)
  "removed": 1,       // borrados del calendar → marcados done_at en activities
  "last_sync_at": "2026-05-02T15:30:00Z"
}
```

## Comportamiento del sync

Para cada evento del calendar en el rango configurado:

1. Buscar `activity` con `origin='meeting'` y `external_id=event.id`.
2. Si no existe → INSERT nuevo con:
   - `title = event.summary`
   - `description = event.description` (truncado si es muy largo)
   - `due_at = event.start.dateTime`
   - `due_date = event.start.date` (para events all-day)
   - `assignee_id = NULL`
   - `created_by_id = currentUser.id` (quien apretó el botón)
   - `origin = 'meeting'`
   - `external_id = event.id`
3. Si existe y los campos cambiaron → UPDATE solo los campos del calendar (`title`, `description`, `due_at`). NO tocar `assignee_id`, `done_at`, `sort_order` (esos los gestiona el usuario localmente).
4. Si existe en local pero ya no está en el calendar (cancelado/borrado) → marcar `done_at = now()` (no hard delete; queda registro). Documentado: si el evento se restaura en el calendar, el próximo sync lo reactiva (set `done_at = NULL`).

## UI

- Botón "Sincronizar reuniones" arriba de la tabla en `/actividades` (icono refresh + label).
- Indicador de "última sincronización: hace X minutos" al lado del botón.
- Spinner mientras corre el sync.
- Toast con resumen al terminar: "Sincronizado: 2 nuevas, 5 actualizadas, 1 cancelada".
- En el widget del dashboard, sin botón propio — se sincroniza desde `/actividades`.

## Riesgos / preguntas abiertas

- **Qué pasa si la cuenta de servicio no tiene permiso al calendar**: error claro, toast en frontend con instrucciones de a quién pedirle permisos.
- **Eventos recurrentes**: tratamos cada instancia como evento independiente (la API de Google ya las expande con `singleEvents=true`). Si un evento recurrente se modifica para todas las instancias, el sync detecta los cambios. Aceptable v1.
- **Privacidad**: si la cuenta centralizada también recibe invitaciones a reuniones sensibles (RR.HH., legales), TODAS aparecen en el panel. Decisión: la convención de la agencia es que la cuenta centralizada SOLO se pone en CC en reuniones de equipo/clientes. No se filtra por palabra clave.
- **Cuotas de Google Calendar API**: no son un problema con sync manual.

## Criterios de done v1

- [ ] Cuenta de servicio creada y configurada (vars de entorno documentadas en `.env.example`).
- [ ] Endpoint `POST /api/v1/activities/sync-calendar` funcional.
- [ ] Sync upserta correctamente: nuevos, actualizados, cancelados.
- [ ] Idempotente: dos clicks seguidos no duplican.
- [ ] Botón en `/actividades` con feedback visual (loading + toast resumen).
- [ ] Documentado en README cómo crear la service account y compartir el calendar con ella.
- [ ] Test integración mínimo: mock del cliente de Google Calendar, verificar upsert correcto.
