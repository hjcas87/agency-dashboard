# Planning — Roadmap de features

Planning docs cortos por feature: contexto, alcance v1, fuera de alcance, datos/migrations, criterios de done. No reemplazan los user stories detallados de `docs/solution_design/user_stories/` — los complementan con foco en *qué entra y qué no en la próxima iteración*.

## Estado actual (2026-05-02)

| #   | Doc                              | Estado          | Notas                                                      |
| --- | -------------------------------- | --------------- | ---------------------------------------------------------- |
| 001 | `001-presupuesto-pdf.md`         | **Pospuesto**   | Plantilla Canva del socio compleja — sesión dedicada después. |
| 002 | `002-actividades.md`             | Pendiente       | Módulo de actividades multi-usuario + widget "Esta semana" en dashboard. |
| 003 | `003-presupuestos-validez.md`    | Pendiente       | Validez visual de 10 días (no restrictiva).                |
| 004 | `004-google-calendar.md`         | Pendiente       | Sync manual de reuniones de cuenta centralizada → actividades. |
| 005 | `005-calidad-batch.md`           | Pendiente       | Tech debt batched: anulados toggle, UNIQUE email, etc.     |

## Orden de ejecución (sin 001)

1. **003 Validez 10 días** — primero, es lo más chico.
2. **002 Actividades** — sección nueva + widget dashboard. Reemplaza `DataTable` placeholder.
3. **004 Google Calendar** — depende de 002 (necesita la tabla `activities`). Sync manual.
4. **005 Calidad batch** — cierre.

## Plan de ejecución paso a paso

Las tareas atómicas para una sesión Sonnet están en **`TASKS.md`**. Cada tarea referencia el doc de planning relevante y especifica archivos, pasos y criterios de done.

## Convenciones

- Formato corto: ~150 líneas máximo por doc.
- User stories con `**Como** / **Quiero** / **Para**` cuando hay UX nueva.
- "Fuera de alcance" es tan importante como "alcance" — define qué NO hacemos para no scope-creep.
- Si la feature ya tiene un user story en `docs/solution_design/user_stories/`, este doc solo lista pasos de implementación.
