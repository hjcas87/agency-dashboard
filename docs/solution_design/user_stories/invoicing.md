# User Story — Facturación

## Descripción
Como usuario de la plataforma, necesito facturar mi trabajo a los clientes — partiendo desde un presupuesto aprobado o desde un formulario libre — y poder consultar el histórico de facturas emitidas con su estado fiscal (CAE, vencimiento, errores AFIP). Por ahora la agencia emite **únicamente Facturas C** (Monotributista emisor); el módulo está preparado para ampliar a A/B/FCE en el futuro pero queda fuera de scope de esta historia.

> Esta historia consume el módulo reutilizable `app.shared.afip` ya integrado (ver `backend/app/shared/afip/SETUP.md` para activación). La feature implementa la entidad de negocio `Invoice` que referencia al `AfipInvoiceLog` por FK.

## Historias de Usuario

### HU-1: Ver pantalla de facturación con secciones diferenciadas
**Como** usuario autenticado
**Quiero** entrar a la pantalla "Facturación" y ver dos secciones — *Presupuestos facturables* y *Facturas emitidas* — en pestañas o tarjetas
**Para** elegir rápidamente entre facturar un presupuesto existente o consultar lo ya emitido

**Criterios de aceptación:**
- La pantalla se accede desde el sidebar → "Facturación".
- La pantalla tiene dos vistas seleccionables (tabs o secciones):
  - **Presupuestos facturables**: tabla de presupuestos en estado `ACCEPTED` que **todavía no tienen factura emitida**.
  - **Facturas emitidas**: tabla de todas las facturas previamente emitidas.
- Si una vista está vacía, se muestra un estado vacío con mensaje y CTA apropiado.
- Botón visible "Facturar manualmente" arriba a la derecha — abre el flujo de la HU-3.

### HU-2: Facturar un presupuesto aprobado
**Como** usuario autenticado
**Quiero** clickear "Facturar" en un presupuesto aprobado y emitir una Factura C real contra AFIP
**Para** cerrar el ciclo comercial sin recargar datos

**Criterios de aceptación:**
- Cada fila en *Presupuestos facturables* tiene un botón "Facturar".
- Al clickear, abre un diálogo de confirmación con el detalle del presupuesto: cliente, total ARS, lista de tareas, fecha de emisión propuesta (hoy), tipo de comprobante (Factura C — fijo).
- El diálogo permite editar:
  - Fecha de emisión (default: hoy; rango permitido: hoy − 5 / hoy + 5 según AFIP para concepto "productos").
  - Concepto (productos / servicios / productos + servicios). Si el usuario elige servicios, debe poder definir las fechas del servicio prestado.
  - Referencia comercial (texto libre, opcional).
- Al confirmar, el backend:
  1. Construye `InvoiceRequest` con `receipt_type=INVOICE_C`, `iva_condition=CF`, `document_type=FINAL_CONSUMER`, `document_number=0` por default (Factura C a Consumidor Final). Si el cliente tiene CUIT cargado, lo usa.
  2. Calcula `base_amount` desde las tareas del presupuesto (horas × hourly_rate × adjustment_percentage).
  3. Llama a `AfipService.issue_invoice(...)`.
  4. Persiste la fila en `invoices` con FK a `proposal_id` y a `afip_invoice_log_id`.
- Al recibir la respuesta:
  - **Éxito** (`success=True`): toast "Factura C N°{numero} emitida — CAE {cae}", la fila desaparece de *Presupuestos facturables* y aparece en *Facturas emitidas*.
  - **Fallo de AFIP**: toast con el mensaje friendly traducido (`messages.translate_afip_error`), el log queda persistido (operador puede inspeccionarlo más tarde), el presupuesto queda en *Presupuestos facturables*.
  - **Fallo de configuración** (`AfipConfigurationError`): toast "AFIP no está configurado en este servidor — contactar al administrador" con link a `SETUP.md`.

### HU-3: Facturar manualmente sin presupuesto
**Como** usuario autenticado
**Quiero** abrir un formulario libre, completar datos del cliente y montos, y emitir una Factura C
**Para** facturar trabajos puntuales que no pasaron por el flujo de presupuestos

**Criterios de aceptación:**
- El botón "Facturar manualmente" abre una página o diálogo con el formulario.
- El formulario tiene los campos:
  - **Cliente**: combobox con búsqueda — selecciona uno existente (ver HU-1 de `client_afip_data.md`) o "Crear nuevo" abre un mini-form inline.
  - **Concepto**: select (productos / servicios / productos + servicios). Si servicios → `service_date_from` / `service_date_to` requeridos.
  - **Fecha de emisión**: date picker (default hoy).
  - **Detalle**: lista editable de líneas (descripción libre + monto ARS). Total se autocalcula.
  - **Referencia comercial** (opcional).
- El formulario valida en cliente:
  - Total > 0.
  - Si concepto es servicios, fechas de servicio presentes y `service_date_from <= service_date_to`.
- Al enviar, mismo flujo que HU-2 pero **sin** FK a presupuesto (`proposal_id = NULL`).
- Idéntico tratamiento de éxito/fallo en toasts.

### HU-4: Ver detalle de una factura emitida
**Como** usuario autenticado
**Quiero** clickear una fila en *Facturas emitidas* y ver el detalle completo
**Para** auditar lo que se mandó a AFIP y obtener el CAE / vencimiento para mostrar al cliente

**Criterios de aceptación:**
- La fila tiene columnas: Número, Tipo, Cliente, Fecha emisión, Total, CAE, Vto. CAE, Estado.
- Estado posible: `Aprobada` (verde), `Rechazada` (rojo), `Con observaciones` (amarillo).
- Click en la fila abre un panel/diálogo con:
  - Datos del cliente facturado.
  - Detalle completo (tareas o líneas manuales).
  - CAE + fecha vencimiento.
  - Observaciones AFIP (si existen) en lista.
  - Errores AFIP (si la factura está rechazada) con código + mensaje friendly.
  - Link al PDF (si la integración con `shared/pdf/` está activa) — ver scope.
  - Para facturas asociadas a presupuesto: link al presupuesto original.

### HU-5: Reintentar emisión de una factura rechazada
**Como** usuario autenticado
**Quiero** ver las facturas rechazadas y poder corregir + reintentar
**Para** no perder el trabajo cuando AFIP rechaza por un dato corregible

**Criterios de aceptación:**
- En el detalle de una factura rechazada hay un botón "Reintentar".
- El botón abre el formulario de la HU-2 o HU-3 precargado con los datos previos, marcando los campos relevantes según el código de error AFIP (ej. 10015 → resaltar el CUIT del cliente, 10243 → resaltar la condición IVA).
- Al reenviar, se crea una nueva fila en `invoices` (no se sobreescribe la anterior — se mantiene el historial completo de intentos).

## Estructura de Datos

Esta historia introduce el modelo `Invoice` en `backend/app/custom/features/invoices/`. **No** modifica `shared/afip/` — que es agnóstico de proyecto.

### Invoice (entidad de negocio)
| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| id | Integer | Auto | Identificador único |
| proposal_id | Integer (FK proposals) | No | Presupuesto que origina la factura. NULL si es manual. |
| client_id | Integer (FK clients) | Sí | Cliente facturado |
| afip_invoice_log_id | Integer (FK afip_invoice_log) | Sí | Apunta al registro AFIP — fuente de CAE, errores, observaciones, raw XML |
| receipt_type | Integer | Sí | `CbteTipo` AFIP — siempre 11 (INVOICE_C) en este scope |
| concept | Integer | Sí | 1=productos, 2=servicios, 3=ambos |
| issue_date | Date | Sí | Fecha de emisión que se mandó a AFIP |
| service_date_from | Date | No | Solo para concepto 2/3 |
| service_date_to | Date | No | Solo para concepto 2/3 |
| total_amount_ars | Numeric(12,2) | Sí | Monto total ARS |
| document_type | Integer | Sí | `DocTipo` AFIP — 99 si CF, 80 si CUIT |
| document_number | BigInteger | Sí | 0 si CF, CUIT si DocTipo=80 |
| line_items | JSONB | Sí | Lista de líneas: `[{"name": str, "amount": str}, ...]` (string para preservar Decimal) |
| commercial_reference | Text | No | Referencia comercial libre |
| created_at | DateTime | Auto | |
| updated_at | DateTime | Auto | |

### Migración
- Alembic `--autogenerate` después de declarar el modelo.
- Imports en `backend/app/models.py`.

## URLs

| Ruta frontend | Descripción |
|---|---|
| `/invoices` | Pantalla principal con tabs *Facturables* / *Emitidas* |
| `/invoices/new` | Formulario de facturación manual |
| `/invoices/{id}` | Detalle de factura emitida |

| API endpoint | Método | Descripción |
|---|---|---|
| `/api/v1/invoices` | GET | Lista de facturas emitidas (con filtros) |
| `/api/v1/invoices` | POST | Crear factura (issue contra AFIP — sirve para HU-2 y HU-3) |
| `/api/v1/invoices/{id}` | GET | Detalle de factura |
| `/api/v1/invoices/billable-proposals` | GET | Lista de presupuestos en `ACCEPTED` sin factura emitida |

## Dependencias

- **`shared/afip`** ya activado en el server (ver `SETUP.md`). Si no está configurado, la pantalla de facturación carga pero los botones devuelven `AfipConfigurationError`.
- **`proposal_status_change.md`** — para que un presupuesto pueda llegar al estado `ACCEPTED` (precondición de HU-2).
- **`client_afip_data.md`** — opcional. Sin esto, las Facturas C salen contra Consumidor Final (`DocTipo=99 / DocNro=0`), que es válido y suficiente para Monotributistas con cliente sin CUIT.

## Fuera de scope

- Facturas A, B y FCE — el módulo `shared/afip` los soporta pero la UI los introduce en una historia futura.
- Notas de crédito y débito — historia separada.
- Generación de PDF de la factura — historia separada (consume `shared/pdf`).
- Envío automático de la factura por email al cliente — historia separada (consume `shared/email`).
- Multi-cotización (USD) — el `shared/afip` lo soporta parcial pero queda diferido.
- Reintentos automáticos de AFIP rechazada — solo reintento manual (HU-5).
