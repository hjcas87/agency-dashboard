# User Story — Cambio de estado de Presupuestos

## Descripción
Como usuario de la plataforma, hoy puedo crear presupuestos y nacen en estado `DRAFT`, pero no tengo forma de moverlos por el ciclo de vida (`SENT → ACCEPTED / REJECTED`). Esto bloquea el flujo de facturación: la pantalla de Facturación lista solamente presupuestos en estado `ACCEPTED` (ver `invoicing.md`), por lo que sin esta historia ninguno aparece como facturable. Necesito poder cambiar el estado desde la UI con confirmación y dejar registro de cuándo cambió.

## Historias de Usuario

### HU-1: Cambiar el estado del presupuesto desde su detalle
**Como** usuario autenticado
**Quiero** ver el estado actual del presupuesto y un selector para cambiarlo
**Para** mover el presupuesto por su ciclo de vida sin tocar la base de datos a mano

**Criterios de aceptación:**
- En la página de detalle / edición del presupuesto, hay un badge prominente con el estado actual y un botón "Cambiar estado".
- El botón abre un menú/dialog con las transiciones permitidas desde el estado actual (matriz abajo).
- Cada transición pide confirmación corta (one-click → dialog "¿Marcar este presupuesto como Enviado?").
- El cambio se persiste vía `PATCH /api/v1/proposals/{id}` con `{status: "..."}`.
- El backend valida que la transición sea legal — rechaza con `400` y mensaje claro si no lo es.
- En éxito, el badge de estado actualiza en tiempo real (sin recargar) y aparece toast de confirmación.

### HU-2: Mostrar el estado en la lista de presupuestos
**Como** usuario autenticado
**Quiero** ver el estado de cada presupuesto como un badge en la lista
**Para** identificar visualmente cuáles están pendientes, enviados, aprobados o rechazados sin entrar al detalle

**Criterios de aceptación:**
- La columna "Estado" se muestra con colores por estado:
  - `DRAFT` — gris, label "Borrador".
  - `SENT` — azul, label "Enviado".
  - `ACCEPTED` — verde, label "Aceptado".
  - `REJECTED` — rojo, label "Rechazado".
- La columna está visible por default y es ordenable.
- Filtro por estado en el toolbar de la tabla (multi-select).

### HU-3: Bloquear edición destructiva en estados terminales
**Como** usuario autenticado
**Quiero** que un presupuesto en `ACCEPTED` o `REJECTED` no se pueda editar libremente
**Para** preservar la integridad del documento que ya fue compartido o cerrado con el cliente

**Criterios de aceptación:**
- En estado `ACCEPTED`:
  - Los campos del presupuesto y las tareas son read-only por default.
  - Hay un botón "Habilitar edición" que requiere confirmación; al activar, el presupuesto vuelve a `DRAFT` automáticamente y se permite editar (registra el cambio de estado).
- En estado `REJECTED`:
  - Mismo comportamiento que `ACCEPTED` — read-only con escape vía "Habilitar edición → DRAFT".
- En `DRAFT` y `SENT`: edición libre.
- En la pantalla de Facturación (`invoicing.md` HU-1): si un presupuesto `ACCEPTED` se vuelve a `DRAFT`, desaparece de "Presupuestos facturables".

### HU-4: Auditar cambios de estado (opcional, diferible)
**Como** usuario autenticado
**Quiero** ver cuándo cambió de estado un presupuesto y quién lo hizo
**Para** auditar el flujo comercial

**Criterios de aceptación:**
- En el detalle del presupuesto, sección "Historial" — lista cronológica de transiciones: `Estado anterior → Estado nuevo, fecha, usuario`.
- Diferible: si la complejidad de agregar un modelo de eventos justifica su propia historia, este HU se mueve a una US separada. La implementación mínima viable se limita a registrar `updated_at` (ya existe).

## Matriz de transiciones permitidas

| Desde \ Hacia | DRAFT | SENT | ACCEPTED | REJECTED |
|---|:---:|:---:|:---:|:---:|
| **DRAFT** | — | ✅ | ✅ | ✅ |
| **SENT** | ✅ (vuelve a draft, sin advertencia) | — | ✅ | ✅ |
| **ACCEPTED** | ✅ (con confirmación, vuelve a DRAFT) | ❌ | — | ❌ |
| **REJECTED** | ✅ (con confirmación, vuelve a DRAFT) | ❌ | ❌ | — |

> Reglas de diseño:
> - No hay transición directa `ACCEPTED ↔ REJECTED`: hay que volver a `DRAFT` primero. Eso evita que el operador "rebote" presupuestos sin una pausa explícita.
> - Volver a `DRAFT` desde estados terminales requiere confirmación porque desbloquea edición destructiva.
> - El backend (`Proposal.service.update_status`) implementa la matriz como un dispatch dict, no como `if/else` anidados (regla del repo).

## Bloqueo cruzado con facturación

- Solo presupuestos en `ACCEPTED` aparecen en "Presupuestos facturables" (HU-1 de `invoicing.md`).
- Si se factura un presupuesto y la factura emitida es exitosa, el presupuesto se queda en `ACCEPTED` pero deja de aparecer como facturable (porque ya tiene factura). Esa lógica vive en `invoicing.md` (filtro), no acá.
- Si se intenta volver a `DRAFT` un presupuesto que ya tiene factura emitida exitosamente, el backend lo permite **pero** muestra advertencia: "Este presupuesto ya tiene la Factura N°XXX emitida — el cambio no afecta a la factura, pero perderás la trazabilidad si editás los datos". El usuario decide.

## API Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/v1/proposals/{id}` | PATCH | Acepta `{status}`. Valida transición. Rechaza con 400 + mensaje si la transición no es legal. |
| `/api/v1/proposals/{id}/state-history` | GET | (HU-4 opcional) Lista de transiciones |

## URLs

Sin cambios a las URLs existentes.

## Fuera de scope

- HU-4 (historial detallado con usuario) si su complejidad justifica una historia separada.
- Notificaciones automáticas al cliente cuando cambia el estado.
- Estados adicionales (`CANCELLED`, `EXPIRED`, etc.).
- Workflows configurables por cliente.
