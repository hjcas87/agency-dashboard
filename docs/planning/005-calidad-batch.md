# 005 — Calidad batch (tech debt)

## Estado: pendiente
## Depende de: nada
## Bloquea: nada

## Contexto

Items chicos de calidad que se vienen acumulando. Ninguno bloquea features pero todos suman. Se hacen en una tanda corta (medio día) para cerrar la temporada de planning.

## Items

### 005-A: Toggle "Incluir anulados" en filtros de facturas

**Problema**: Hoy el filtro "Solo internos" en `/facturas` muestra también las anuladas (X soft-cancelled). No hay un toggle explícito para excluirlas.

**Solución**:
- Checkbox/Toggle "Incluir anuladas" en la toolbar de la tabla.
- Por defecto: **OFF** (excluir).
- Cuando OFF: filtra rows con `cancelled_at IS NOT NULL` (X) y `cancelled_by_invoice_id IS NOT NULL` (AFIP, ya tienen NC asociada).

**Archivos**: `frontend/components/custom/features/invoices/invoices-table.tsx`.

**Done**: Por defecto la tabla no muestra anulados; al activar el toggle aparecen con su estilo `line-through` actual.

---

### 005-B: `UNIQUE(client_id, email)` en `client_emails`

**Problema**: Hoy se pueden cargar dos emails iguales para el mismo cliente. No es un bug grande pero ensucia el CC en envíos.

**Solución**:
- Migration agregando constraint `UNIQUE(client_id, email)`.
- Antes del constraint: cleanup de duplicados existentes (mantener el más viejo, borrar el resto).
- Backend service: capturar `IntegrityError` y devolver mensaje claro ("Ese email ya está cargado para este cliente").

**Archivos**:
- `backend/alembic/versions/<nuevo>.py`
- `backend/app/custom/features/clients/service.py` (manejo de IntegrityError)

**Done**: No se puede cargar email duplicado, mensaje claro al usuario, duplicados existentes limpiados.

---

### 005-C: Numeración X con `SEQUENCE` Postgres

**Problema**: Hoy el `internal_number` de comprobantes X se calcula con `MAX(internal_number) + 1` en service. Bajo concurrencia podría dar dos invoices con el mismo número (raro con un solo emisor pero técnicamente posible).

**Solución**:
- Migration creando `CREATE SEQUENCE invoices_internal_number_seq START WITH (max actual + 1)`.
- Backend service usa `SELECT nextval('invoices_internal_number_seq')` para obtener el próximo número, en lugar de calcular MAX + 1.

**Archivos**:
- `backend/alembic/versions/<nuevo>.py`
- `backend/app/custom/features/invoices/service.py` (método que asigna `internal_number`)

**Done**: Nuevo X usa la sequence, dos requests concurrentes (test ad-hoc) reciben números distintos.

---

### 005-D: Lint pre-existente en `app/main.py`

**Problema**: 4 issues que arrastra hace tiempo (whitespace + import-order). No fueron introducidos por nosotros pero fallan `make lint`.

**Solución**:
- Ejecutar `make format` (black + isort) y verificar que arregla.
- Si quedan issues de ruff: corregir manualmente.

**Archivos**: `backend/app/main.py`.

**Done**: `make lint` pasa sin errores en `main.py`.

---

## Criterios de done global

- [ ] 005-A funcional (toggle anulados).
- [ ] 005-B migration aplicada + cleanup + handling de duplicados.
- [ ] 005-C sequence creada y service usa `nextval`.
- [ ] 005-D `make lint` pasa.
- [ ] Tests pasan.
- [ ] Sin regresiones visibles en facturas, clientes ni dashboard.
