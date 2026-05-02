# CUITs de prueba — AFIP/ARCA homologación

Listado de CUITs registrados en homologación (entorno de testing oficial
de ARCA). Usar siempre uno de estos al probar `Padrón A5` o emitir
contra `wsfehomo` — los CUITs de producción **no existen** en
homologación y devuelven `No existe persona con ese Id`.

> **Fuente única en código**: `backend/tests/fixtures/afip_homo_cuits.py`.
> Cualquier cambio se hace ahí; este documento es la referencia legible.

## Monotributo

| CUIT |
|---|
| 20431203422 |
| 20700538673 |
| 27139277908 |
| 24766312108 |
| 20313369154 |

## Personas Físicas

| CUIT |
|---|
| 20907332064 |
| 27242151459 |
| 24952244155 |
| 20020833042 |
| 27828940541 |
| 20483704276 |
| 24491994602 |

## Personas Jurídicas

| CUIT |
|---|
| 33561767209 |
| 30243719581 |
| 30229554324 |
| 30392474036 |
| 30643411861 |

## Cómo usarlos

### Smoke test rápido (ver conexión + Padrón end-to-end)

```bash
cd backend
uv run python scripts/afip_homo_smoke_test.py
```

### En tests pytest

```python
from tests.fixtures.afip_homo_cuits import (
    SAMPLE_MONOTRIBUTO,
    HOMO_CUITS_PERSONA_JURIDICA,
)
```

## Notas operativas

- En homologación **no se cobra ni se factura realmente** — los CAEs
  devueltos no tienen valor fiscal.
- El CUIT del emisor (`AFIP_CUIT` en `.env`) **también** debe estar
  habilitado al WSAA homo. Si tu certificado no fue emitido para ese
  CUIT, WSAA devuelve `loginCms returns null` o falta de permisos.
- Si AFIP rota la lista de CUITs disponibles en homo (lo hace muy de
  vez en cuando), actualizar `backend/tests/fixtures/afip_homo_cuits.py`
  y este documento juntos.
