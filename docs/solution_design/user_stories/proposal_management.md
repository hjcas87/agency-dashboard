# User Story — Gestión de Presupuestos

## Descripción

Como usuario de la plataforma, necesito poder crear, editar y gestionar presupuestos compuestos por tareas con horas y valores, para poder cotizar proyectos de manera organizada y profesional.

## Contexto

Un presupuesto es un documento comercial que agrupa un conjunto dinámico de tareas (ítems de trabajo). Cada tarea tiene un nombre, descripción y cantidad de horas. El presupuesto define un valor por hora en pesos argentinos (ARS) que se convierte automáticamente a dólares estadounidenses (USD). El presupuesto puede tener un descuento o recargo porcentual (-100% a +100%) y puede estar asociado opcionalmente a un cliente.

---

## Historias de Usuario

### HU-1: Ver lista de presupuestos

**Como** usuario autenticado  
**Quiero** ver una tabla con todos mis presupuestos  
**Para** tener una vista general y poder acceder rápidamente a cualquiera

**Criterios de aceptación:**

- La tabla muestra: Nombre del presupuesto, Cliente asociado (o "—" si no tiene), Estado (Borrador, Enviado, Aceptado, Rechazado), Total ARS, Total USD (convertido), Fecha de creación
- La tabla soporta ordenamiento por columna
- La tabla soporta filtrado/búsqueda por nombre
- La tabla soporta paginación
- Si no hay presupuestos, se muestra un estado vacío con mensaje apropiado
- La página se accede desde el sidebar → "Presupuestos" (`/proposals`)

### HU-2: Crear un presupuesto nuevo

**Como** usuario autenticado  
**Quiero** crear un presupuesto con nombre, cliente opcional, valor por hora y lista de tareas  
**Para** generar una cotización profesional

**Criterios de aceptación:**

- El botón "Crear Presupuesto" está visible arriba a la derecha de la tabla
- El formulario de creación tiene:
  - **Nombre** del presupuesto (requerido)
  - **Cliente asociado** (opcional, dropdown con clientes existentes)
  - **Valor por hora en ARS** (requerido, numérico > 0)
  - **Tasa de cambio ARS/USD** (requerido, numérico > 0, por defecto un valor configurable)
  - **Porcentaje de ajuste** (-100% a +100%, por defecto 0%, donde negativo = descuento, positivo = recargo)
  - **Lista dinámica de tareas** con:
    - Nombre de la tarea (requerido)
    - Descripción de la tarea (textarea, opcional)
    - Cantidad de horas (requerido, numérico > 0)
  - Botón "Agregar tarea" para añadir filas
  - Cada tarea tiene botón de eliminar (icono de basura)
- Se muestra en tiempo real:
  - Total de horas (suma de todas las tareas)
  - Subtotal ARS (total_horas × valor_hora)
  - Monto de ajuste (subtotal × porcentaje_ajuste / 100)
  - Total ARS (subtotal + monto_ajuste)
  - Total USD (total_ars / tasa_cambio)
- Al guardar, se redirige a la lista de presupuestos
- Toast de éxito al crear

### HU-3: Editar un presupuesto existente

**Como** usuario autenticado  
**Quiero** modificar los datos de un presupuesto  
**Para** ajustar la cotización antes de enviarla

**Criterios de aceptación:**

- Cada fila de la tabla tiene un botón de edición (menú de acciones → Editar)
- El formulario de edición se abre en la misma pantalla de creación (`/proposals/{id}/edit`)
- Los campos se precargan con los datos existentes incluyendo todas las tareas
- Los cálculos se actualizan en tiempo real al modificar cualquier valor
- Al guardar, se redirige a la lista de presupuestos
- Toast de éxito al editar

### HU-4: Eliminar un presupuesto

**Como** usuario autenticado  
**Quiero** eliminar un presupuesto  
**Para** quitar cotizaciones que ya no necesito

**Criterios de aceptación:**

- Cada fila de la tabla tiene un botón de eliminar (menú de acciones → Eliminar)
- Se pide confirmación con AlertDialog antes de eliminar
- Se muestra un toast de éxito al eliminar
- La fila se elimina de la tabla sin recargar

### HU-5: Cambiar estado de un presupuesto

**Como** usuario autenticado  
**Quiero** cambiar el estado de un presupuesto entre Borrador, Enviado, Aceptado y Rechazado  
**Para** llevar control del proceso comercial

**Criterios de aceptación:**

- En la tabla se muestra el estado con un Badge con color semántico
- En la vista de edición se puede cambiar el estado con un Select
- Los estados posibles son: `draft` (Borrador), `sent` (Enviado), `accepted` (Aceptado), `rejected` (Rechazado)
- Se muestra toast de confirmación al cambiar estado

---

## Estructura de Datos

### Proposal (Presupuesto)

| Campo                 | Tipo        | Requerido | Descripción                             |
| --------------------- | ----------- | --------- | --------------------------------------- |
| id                    | int         | Auto      | Identificador único                     |
| name                  | string      | Sí        | Nombre del presupuesto                  |
| client_id             | int \| null | No        | FK al cliente asociado                  |
| status                | enum        | Sí        | `draft`, `sent`, `accepted`, `rejected` |
| hourly_rate_ars       | decimal     | Sí        | Valor por hora en pesos argentinos      |
| exchange_rate         | decimal     | Sí        | Tasa de cambio ARS → USD (ej: 1200.00)  |
| adjustment_percentage | decimal     | Sí        | -100 a +100 (descuento o recargo)       |
| created_at            | datetime    | Auto      | Fecha de creación                       |
| updated_at            | datetime    | Auto      | Fecha de última modificación            |

### ProposalTask (Tarea del presupuesto)

| Campo       | Tipo         | Requerido | Descripción                         |
| ----------- | ------------ | --------- | ----------------------------------- |
| id          | int          | Auto      | Identificador único                 |
| proposal_id | int          | Sí        | FK al presupuesto                   |
| name        | string       | Sí        | Nombre de la tarea                  |
| description | text \| null | No        | Descripción detallada               |
| hours       | decimal      | Sí        | Cantidad de horas estimadas         |
| sort_order  | int          | Sí        | Orden de la tarea en el presupuesto |

### Cálculos derivados (no se almacenan, se calculan)

| Campo                 | Fórmula                                      |
| --------------------- | -------------------------------------------- |
| total_hours           | SUM(hours) de todas las tareas               |
| subtotal_ars          | total_hours × hourly_rate_ars                |
| adjustment_amount_ars | subtotal_ars × (adjustment_percentage / 100) |
| total_ars             | subtotal_ars + adjustment_amount_ars         |
| total_usd             | total_ars / exchange_rate                    |

---

## URLs

| Ruta                   | Descripción                            |
| ---------------------- | -------------------------------------- |
| `/proposals`           | Lista de presupuestos (tabla)          |
| `/proposals/new`       | Formulario de creación                 |
| `/proposals/{id}/edit` | Formulario de edición (incluye tareas) |

---

## API Endpoints

| Método | Endpoint                        | Descripción                               |
| ------ | ------------------------------- | ----------------------------------------- |
| GET    | `/api/v1/proposals`             | Listar todos los presupuestos             |
| POST   | `/api/v1/proposals`             | Crear un nuevo presupuesto (con tareas)   |
| GET    | `/api/v1/proposals/{id}`        | Obtener un presupuesto con sus tareas     |
| PUT    | `/api/v1/proposals/{id}`        | Actualizar presupuesto (reemplaza tareas) |
| DELETE | `/api/v1/proposals/{id}`        | Eliminar un presupuesto                   |
| PATCH  | `/api/v1/proposals/{id}/status` | Cambiar estado del presupuesto            |

---

## Mensajes de Usuario (español)

### Éxito

- Creación: "Presupuesto creado correctamente"
- Edición: "Presupuesto actualizado correctamente"
- Eliminación: "Presupuesto eliminado correctamente"
- Estado: "Estado actualizado a {estado_label}"

### Error

- Creación: "No se pudo crear el presupuesto. Intentalo de nuevo."
- Edición: "No se pudo actualizar el presupuesto. Intentalo de nuevo."
- Eliminación: "No se pudo eliminar el presupuesto. Intentalo de nuevo."
- Validación: "El nombre es requerido", "El valor por hora debe ser mayor a 0", "La tasa de cambio debe ser mayor a 0", "Agregá al menos una tarea", "Cada tarea debe tener un nombre y horas válidas"

### Confirmación de eliminación

- "¿Estás seguro de que deseas eliminar este presupuesto? Esta acción no se puede deshacer."

### Estados (labels para UI)

- `draft` → "Borrador" (Badge gris)
- `sent` → "Enviado" (Badge azul)
- `accepted` → "Aceptado" (Badge verde)
- `rejected` → "Rechazado" (Badge rojo)

---

## Implementación sugerida

### Backend (`backend/app/custom/features/proposals/`)

```
proposals/
├── __init__.py
├── models.py          # Proposal, ProposalTask (SQLAlchemy)
├── schemas.py         # ProposalCreate, ProposalUpdate, ProposalResponse, ProposalTaskCreate, ProposalTaskResponse, etc.
├── repository.py      # ProposalRepository, ProposalTaskRepository
├── service.py         # ProposalService (con cálculos de totales)
├── routes.py          # FastAPI endpoints
└── tasks.py           # (opcional) tareas Celery si se necesita exportar PDF
```

### Frontend

- **Página lista**: `frontend/app/(private)/(custom)/proposals/page.tsx` (reemplazar la página en blanco actual)
- **Página crear**: `frontend/app/(private)/(custom)/proposals/new/page.tsx`
- **Página editar**: `frontend/app/(private)/(custom)/proposals/[id]/edit/page.tsx`
- **Componente tabla**: `frontend/components/custom/features/proposals/proposals-table.tsx` (reutilizar patrón de `clients-table.tsx`)
- **Componente form crear**: `frontend/components/custom/features/proposals/proposal-form.tsx`
- **Componente form editar**: `frontend/components/custom/features/proposals/proposal-edit-form.tsx`
- **Componente tareas**: `frontend/components/custom/features/proposals/task-list.tsx` (lista dinámica de tareas con add/remove)
- **Server actions**: `frontend/app/actions/custom/proposals.ts`

### Componentes shadcn a verificar/usar

- `Table` (ya instalada, reutilizar patrón de clients)
- `AlertDialog` (ya instalada, para confirmación de delete)
- `Select` (ya instalado, para cliente y estado)
- `Input` (ya instalado, para campos numéricos)
- `Textarea` (verificar instalación para descripción de tareas)
- `Badge` (ya instalado, para estados)
- `Button` (ya instalado)
- `Label` (ya instalado)

### No magic strings

- Estados del presupuesto → centralizados en `constants.py` (backend) y `messages.ts` (frontend)
- Mensajes de error/éxito → centralizados en `constants.py` (backend) y `messages.ts` (frontend)
- Labels de moneda → `"ARS"`, `"USD"` centralizados
- Claves de response → usar constantes tipadas

---

## Notas de diseño

1. **Formulario de tareas**: Las tareas se muestran como filas editables dentro del formulario del presupuesto. Cada fila tiene: nombre (input), descripción (textarea que se expande al hacer focus), horas (input numérico), botón eliminar. Un botón "Agregar tarea" añade una fila vacía al final.

2. **Panel de totales**: A la derecha o debajo del formulario, un panel fijo muestra los cálculos en tiempo real:

   ```
   Total horas:        40.00 hs
   Subtotal:      $ 400.000 ARS
   Ajuste (-10%):  -$  40.000 ARS
   ─────────────────────────────
   Total ARS:     $ 360.000 ARS
   Total USD:         300.00 USD
   ```

3. **Tasa de cambio**: Un campo numérico editable con un valor por defecto razonable (ej: 1200.00). Se puede agregar un tooltip explicando "1 USD = X ARS".

4. **Porcentaje de ajuste**: Un input numérico con stepper (-/+), rango -100 a +100. Se puede mostrar como "-10%" o "+5%". Un valor negativo muestra "Descuento" en rojo, uno positivo muestra "Recargo" en verde.

5. **Reutilización**: La tabla de presupuestos reutiliza el mismo patrón visual y componentes de `clients-table.tsx` (TanStack Table, búsqueda, paginación, menú de acciones). Los formularios reutilizan el patrón de una columna de `client-form.tsx`.
