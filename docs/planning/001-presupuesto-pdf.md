# 001 — PDFs de presupuesto

## Estado: pendiente
## Depende de: nada
## Bloquea: nada (pero es lo más viejo en cola, prioridad alta)

## Contexto

El user story **HU-PDF-1** ya está descripto en `docs/solution_design/user_stories/pdf_generation.md`. Lo que falta es la implementación. La pipeline de PDFs de facturas ya está montada (reportlab platypus, fonts, layout matemático, A4 con footer pinned, etc.) — vamos a reutilizarla.

## Alcance v1

- Renderer dedicado en `backend/app/shared/pdf/renderers/proposal.py` (siguiendo el patrón de `invoice.py`).
- Layout simple, sobrio, alineado al de facturas pero **sin AFIP**:
  - Header con logo + datos del emisor + número de presupuesto + fecha.
  - Datos del cliente (si está asociado).
  - Tabla de tareas: nombre, descripción, horas.
  - Bloque de totales: total horas, subtotal ARS, ajuste, total ARS, total USD (con tasa).
  - Footer con condiciones (validez 10 días — ver doc 003).
- Endpoint `GET /api/v1/pdf/proposals/{id}` que stream-ea el PDF (existe ruta declarada en HU-PDF-1, falta implementación).
- Botón "PDF" en `proposals-table.tsx` (acción que abre el PDF en nueva pestaña).
- Acción server `getProposalPdf(id)` o uso directo del endpoint vía proxy.

## Fuera de alcance

- Editor de plantilla de PDF de presupuesto (eso es otra feature aparte si alguna vez aparece).
- Firma digital / sello del cliente.
- Versionado del PDF (cada generación es on-the-fly).
- Preview interactivo (HU-PDF-1 lo menciona pero queda para v2; en v1 alcanza con descargar).

## Datos / migrations

- Ninguna nueva. Toda la info ya está en `proposals` + `proposal_tasks` + `clients`.
- **Excepción**: si para el footer queremos mostrar "Válido hasta 2026-05-12", necesitamos `sent_at` (ver doc 003). Si 003 todavía no entró, el footer dice solo "Válido por 10 días desde la emisión".

## Implementación (orden)

1. Crear `backend/app/shared/pdf/renderers/proposal.py` con el renderer.
2. Crear `backend/app/custom/features/pdf/routes.py` endpoint `/proposals/{id}` (o extender existente).
3. Tests unitarios mínimos: renderer no explota con presupuesto sin cliente, sin descripción, sin ajuste.
4. Frontend: botón PDF en `proposals-table.tsx` action menu.
5. Verificar visual contra un presupuesto real antes de declarar done.

## Criterios de done

- [ ] PDF se descarga en menos de 2 segundos para un presupuesto de 10 tareas.
- [ ] Layout legible en A4 impreso y en pantalla.
- [ ] Maneja correctamente: sin cliente, descripciones largas con wrap, ajuste 0 / negativo / positivo, totales redondeados.
- [ ] Botón PDF visible en cada fila de la tabla de presupuestos.
- [ ] No rompe la pipeline de PDFs de facturas (regresión visual).

## Notas técnicas

- Usar las mismas fonts/styles que `invoice.py` para coherencia visual entre presupuestos y facturas.
- CJK wordWrap en `IssuerName` y `Value` styles para nombres largos.
- Los textos fijos (footer, condiciones) van en un módulo de mensajes — no inline (regla del repo: no magic strings).
