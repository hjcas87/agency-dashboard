# 003 — Presupuestos: validez 10 días

## Estado: pendiente
## Depende de: nada
## Bloquea: nada (pero alimenta sugerencias auto del doc 002)

## Contexto

Hoy un presupuesto enviado no tiene noción de "vencimiento". Idealmente vale 10 días desde que se manda — pasado eso, los precios pueden moverse, la tasa de cambio bailó, etc. **No es restrictivo**: el sistema tiene que seguir permitiendo facturar contra un presupuesto vencido sin trabar nada. Es solo una señal visual y un disparador de sugerencias.

## User stories

### HU-V-1: Capturar fecha de envío

**Como** dueño-operador  
**Quiero** que el sistema registre cuándo cambio un presupuesto a "enviado"  
**Para** poder calcular su vigencia

**Criterios:**
- Cuando `status` pasa de `draft` → `sent`, el backend setea `sent_at = now()` automáticamente.
- Si vuelve a `draft` y luego a `sent` otra vez, **se actualiza** `sent_at` (es la "última vez que se envió"). Decisión simple para v1.
- `sent_at` permanece NULL para presupuestos en `draft`.
- Si el status pasa directo a `accepted` sin pasar por `sent` (caso raro, pero posible si el cliente acepta verbalmente), también se setea `sent_at = now()` para tener referencia.

### HU-V-2: Mostrar estado de validez

**Como** dueño-operador  
**Quiero** ver de un vistazo si un presupuesto está vigente, próximo a vencer o vencido  
**Para** decidir si hago seguimiento o re-emito

**Criterios:**
- Tabla de presupuestos: columna nueva "Vigencia" o badge inline en la columna estado.
- Detalle del presupuesto: badge prominente.
- Reglas visuales (sobre `sent_at + 10 días`):
  - **Vigente** (>5 días restantes): badge gris/azul "Vigente hasta DD/MM"
  - **Por vencer** (1–5 días restantes): badge ámbar "Vence en X días"
  - **Vencido** (días restantes ≤ 0): badge rojo "Vencido hace X días"
  - **Sin enviar** (`sent_at IS NULL`): sin badge (es draft, no aplica).
- **No bloquea ninguna acción** — facturar, editar, cambiar estado siguen funcionando.

### HU-V-3 (opcional, alimenta doc 002): Sugerir seguimiento

**Como** dueño-operador  
**Quiero** que la agenda me sugiera hacer seguimiento de presupuestos enviados sin respuesta  
**Para** no perder oportunidades por olvido

**Criterios:**
- En `/api/v1/tasks/suggestions` (ver doc 002): cualquier presupuesto con `status=sent` y `sent_at` entre 5 y 10 días atrás genera una sugerencia "Hacer seguimiento de [nombre]".
- Pasados los 10 días, la sugerencia cambia a "Re-emitir o cerrar [nombre]".

## Alcance v1

- Migration agregando `sent_at TIMESTAMPTZ NULL` a `proposals`.
- Service: hook al cambiar status para setear `sent_at`.
- Schema response incluye `sent_at` y campo derivado `days_until_expiry` (puede ser negativo).
- Frontend: badge de vigencia en tabla y detalle.

## Fuera de alcance

- Restricción de facturación contra presupuestos vencidos.
- Notificaciones cuando un presupuesto está por vencer.
- Renovar automáticamente la validez.
- Configuración del período (10 días queda hardcoded en v1; si en algún momento queremos por-cliente, se hace después).

## Datos / migrations

```sql
ALTER TABLE proposals ADD COLUMN sent_at TIMESTAMPTZ NULL;
```

**Backfill**: presupuestos existentes con `status IN ('sent', 'accepted', 'rejected')` reciben `sent_at = updated_at` como aproximación. Es lo mejor que tenemos sin histórico real. Documentar en la migration que es backfill aproximado.

## Service / lógica

En `ProposalService.update_status()`:

```python
if new_status in (sent, accepted) and proposal.sent_at is None:
    proposal.sent_at = datetime.now(timezone.utc)
elif new_status == sent and old_status == draft:
    # Re-envío: actualizar
    proposal.sent_at = datetime.now(timezone.utc)
```

Constante `PROPOSAL_VALIDITY_DAYS = 10` en `proposals/constants.py` (no magic number).

## API

Sin endpoints nuevos. El response existente de `GET /api/v1/proposals/{id}` y `GET /api/v1/proposals` agrega:

```json
{
  ...
  "sent_at": "2026-04-25T10:00:00Z",
  "days_until_expiry": 3
}
```

`days_until_expiry` es `None` si `sent_at` es `None`. Negativo si ya venció.

## Riesgos / preguntas abiertas

- ¿Qué hace `sent_at` si un presupuesto vuelve a `draft`? **Decisión**: lo dejamos seteado. Cuando se re-envíe, se actualiza. No se borra al volver a draft (el dato histórico es útil para analytics).
- ¿Qué pasa con presupuestos que nunca se enviaron pero se aceptaron de palabra y se facturaron directo? El service también setea `sent_at` al pasar a `accepted`. Caso cubierto.
- ¿Y si quiero renovar la validez sin cambiar status? **Out of scope v1**. Si emerge la necesidad, agregamos un botón "Renovar vigencia" que actualice `sent_at = now()`.

## Criterios de done

- [ ] Migration aplicada y backfill ejecutado en local + verificado.
- [ ] Setear `sent_at` automático al cambiar status.
- [ ] Constante `PROPOSAL_VALIDITY_DAYS` en `constants.py`.
- [ ] Badge de vigencia visible en tabla y detalle, con los 4 estados visuales.
- [ ] No bloquea ninguna acción existente (facturar, editar, cancelar).
- [ ] Tipo de API regenerado en frontend (`npm run generate-api-types`).
- [ ] Test: cambiar status a `sent` setea `sent_at`; pasar de `draft` a `accepted` también lo setea.
