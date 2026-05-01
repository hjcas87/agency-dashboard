# Auditoría de bugs — Módulo AFIP

> Revisión hecha cruzando el código del módulo `apps/afip/` contra `manual_dev.md` (anexo oficial RG 4291 v4.0). Cada bug cita **archivo:línea** del código actual + **regla del manual** que viola + **código de error AFIP** que lo delata en producción.
>
> No son hipótesis. Son violaciones concretas detectables leyendo código vs manual.

---

## ✅ Resueltos

| # | Bug | Rama / PR |
|---|---|---|
| — | Cálculo USD→ARS con rate del día en factura y NC/ND | `fix/afip-usd-invoice-calculation` ✅ mergeado |
| 1 | `IVA_AFIP_CODES["NA"]: 3 → 15` (código 3 no existe en AFIP) | `fix/afip-validation-matrix` ✅ mergeado |
| 2+3 | Matriz `allowed_iva_map` y `_validate_receipt_type_compatibility` re-alineadas con **AFIP runtime** (no con el anexo escrito, que está desactualizado) | `fix/afip-validation-matrix` ✅ mergeado |
| 5 | `iva_condition_id` default silencioso → `AFIPValidationError` (billing.py) | `fix/afip-validation-matrix` ✅ mergeado |
| 6 | `DocType.CDI (87)` agregado al enum + whitelist | `fix/afip-validation-matrix` ✅ mergeado |
| 7 | Validator `validate_fce_no_categorizado` (código 10178) + mensaje friendly | `fix/afip-validation-matrix` ✅ mergeado |
| — | Management command `afip_iva_receptor_codes` para consultar AFIP runtime | `fix/afip-validation-matrix` ✅ mergeado |
| **14** | `Invoice.net_amount` + `Invoice.iva_amount` persisten el desglose que fue a AFIP. Fix del PDF cuando subtotal + IVA no cuadraba con total en facturas USD con rate distinto | `fix/afip-invoice-net-iva-fields` ✅ mergeado |
| **12** | Escape XML de todo campo string interpolado al SOAP (reference, CBU, transfer_type, date, token, sign). Helper `_xml_escape()` en `billing.py` | `fix/afip-xml-escape-and-padron-detection` ⏳ pendiente de merge |
| **13** | `_determine_iva_condition` reescrita con orden correcto (Monotributo prioridad máxima) y sin match textual sin verificar `status=AC` | `fix/afip-xml-escape-and-padron-detection` ⏳ pendiente de merge |

Tests acumulados: 229/229 en verde.

### Hallazgo crítico durante el fix de validation matrix

El **anexo escrito del manual** dice combinaciones distintas a las que AFIP acepta en runtime. La matriz corregida refleja la respuesta real de `FEParamGetCondicionIvaReceptor`:

- **Factura A**: solo 1 (RI), 6 (MT), 13 (MT Social), 16 (MT TIP).
- **Factura B**: solo 4 (EX), 5 (CF), 7 (NC), 8 (Prov Ext), 9 (Cli Ext), 10 (Liberado), 15 (NA).
- **Factura C**: todas las condiciones.

`manual_dev.md` actualizado para reflejar esta realidad runtime.

### Estado actual (abril 2026)

**Main ya contiene:** fix USD→ARS + matriz alineada con AFIP runtime + command de diagnóstico.
**Rama pendiente de merge:** `fix/afip-invoice-net-iva-fields` (neto/IVA persistidos + fix PDF). Al mergear: correr `python src/backend/manage.py migrate afip` y `cd src/frontend && npm run build`.

**Bugs abiertos aún sin atacar (todos no aplican a la operación actual):**
- **Bug 4** — alícuotas IVA hardcodeadas a 21%. Descartado para este cliente (rubro gráfico = siempre 21%).
- **Bug 8** — `valid_related_types` restrictivo para NC/ND sobre recibos. Solo si necesitan emitir NC sobre recibos.
- **Bug 10** — `ImpTotConc`/`ImpOpEx` fijos en 0. No aplica a la operación actual.
- **Bug 11** — falta `CanMisMonExt` si moneda ≠ PES. No aplica (facturan en pesos).

---

## 🔴 BUG CRÍTICO #1 — Código IVA "NA" mapeado a valor inexistente

**Archivo:** `apps/afip/enums.py:35-42`

```python
IVA_AFIP_CODES = {
    "RI": 1,
    "MT": 6,
    "EX": 4,
    "NA": 3,   # ❌ código 3 NO EXISTE en AFIP
    "CF": 5,
    "NC": 7,
}
```

**Regla del manual:** el anexo oficial "Condición frente al IVA del Receptor" lista: 1, 4, 5, 6, 7, 8, 9, 10, 13, **15**, 16. **No existe código 3.** El código para "IVA No Alcanzado" es **15**.

**Síntoma en producción:** todo cliente con `IvaChoices.NA` genera error AFIP **10242** ("El campo de identificación de la Condición de IVA del receptor no es un valor permitido"). La factura es rechazada antes de emitirse.

**Fix:** `"NA": 15`.

---

## 🔴 BUG CRÍTICO #2 — Matriz `allowed_iva_map` incompleta y con código inválido

**Archivo:** `apps/afip/services/validations.py:22-36`

```python
allowed_iva_map = {
    ReceiptType.INVOICE_A: [1, 4],                  # ❌ faltan 6, 8, 9, 10
    ReceiptType.INVOICE_B: [3, 4, 5, 6, 7],         # ❌ código 3 inválido, faltan 8, 9, 10, 13, 15, 16
    ...
}
```

**Regla del manual** (anexo tabla): Factura A/M admite `{1, 4, 6*, 8, 9, 10}` (* Monotributo post Ley 27.618 queda observada con 10217, no rechazada). Factura B admite `{1, 4, 5, 6, 7, 8, 9, 10, 13, 15, 16}`.

**Síntoma en producción:**
- Facturar a Proveedor/Cliente del Exterior (cód 8/9): **rechazado localmente** por esta validación antes de llegar a AFIP (que sí lo permite).
- Facturar a Monotributista/Exento/NA con Factura A: rechazado localmente.
- Facturar a Monotributo Social (13), IVA No Alcanzado (15), Monotributo TIP (16): rechazado localmente.

**Fix:** alinear las listas con el anexo. Eliminar `3` y agregar `15`.

---

## 🔴 BUG CRÍTICO #3 — Matriz `_validate_receipt_type_compatibility` desalineada con emisores RI

**Archivo:** `apps/afip/services/invoice_service.py:347-369`

```python
valid_combinations = {
    IvaChoices.RI: standard_types + [FCE_INVOICE_A, FCE_INVOICE_B, FCE_INVOICE_C],
    IvaChoices.MT: standard_types + [FCE_INVOICE_B, FCE_INVOICE_C],
    IvaChoices.EX: standard_types + [FCE_INVOICE_B, FCE_INVOICE_C],
    IvaChoices.NA: standard_types + [FCE_INVOICE_B, FCE_INVOICE_C],
    IvaChoices.CF: standard_types + [FCE_INVOICE_B, FCE_INVOICE_C],  # ❌ CF no recibe FCE
    IvaChoices.NC: standard_types + [FCE_INVOICE_C],                 # ❌ NC no recibe A ni FCE C
}
```

Donde `standard_types = [INVOICE_A, INVOICE_B, INVOICE_C]`.

**Regla del manual:**
- FCE solo admite receptores categorizados GRANDE o PYME con CUIT (código 10180 / 1476). **Un CF nunca puede recibir FCE** (necesita CUIT, y código 1487 obliga DocTipo=80).
- FCE C requiere receptor activo en IVA, Monotributo o Exento (código 10177 / 1474). Un No Categorizado no aplica (10178 prohíbe DocNro 23000000000).
- Monotributo como receptor **sí puede** recibir FCE A (código 1474 A: "activo en IVA o Monotributo").

**Síntoma:** código permite combinaciones que AFIP rechaza y rechaza otras que AFIP acepta. Errores 10180 / 10243 en producción.

**Fix:** reescribir la matriz usando la tabla del anexo + validaciones FCE específicas 1474, 10177, 10180, 1487.

---

## 🟠 BUG #4 — `_build_iva_block` hardcodea alícuota 21%

**Archivo:** `apps/afip/services/billing.py:389-404`

```python
iva_id = 5  # ID 5 = 21% (tasa general)
```

**Regla del manual:** AFIP expone múltiples alícuotas vía `FEParamGetTiposIva` (Id 3=0%, 4=10.5%, 5=21%, 6=27%, 8=5%, 9=2.5%). Una factura puede tener múltiples líneas de IVA.

**Síntoma:** si el cliente debe emitir con 10.5% (salud, libros), 27% (telecomunicaciones, energía), 0% (exportación) o tasas mixtas, **no puede**. Hoy todo va a 21% hardcoded. Si `iva_amount` no coincide con 21% × base, AFIP rechaza con código 10051 ("importes AlicIVA no corresponden al tipo").

**Fix:** que `_build_iva_block` reciba una lista de alícuotas desde `invoice_data` (no hoy disponible en el DTO). Requiere extender `InvoiceData.iva_breakdown: list[(id, base, importe)]`.

---

## 🟠 BUG #5 — Default silencioso a código `5` (Consumidor Final)

**Archivo:** `apps/afip/services/billing.py:251`

```python
iva_condition_id = IVA_AFIP_CODES.get(invoice_data.iva_condition, 5)
```

**Problema:** si `invoice_data.iva_condition` no está en `IVA_AFIP_CODES` (bug de data, nueva condición agregada sin mapear, etc.), el sistema silenciosamente manda `5` (Consumidor Final) a AFIP. Oculta errores de configuración.

**Fix:** si no está en el mapa, `raise AFIPValidationError(...)` con mensaje claro.

---

## 🟠 BUG #6 — Falta tipo de documento CDI (87) en enum

**Archivo:** `apps/afip/enums.py:12-16`

```python
class DocType(Enum):
    CUIT = 80
    CUIL = 86
    DNI = 96
    FINAL_CONSUMER = 99
    # ❌ falta CDI = 87 (Clave de Identificación)
```

**Regla del manual:** `FEParamGetTiposDoc` devuelve CDI (87) como válido. Manual cita 87 en validaciones 10015, 1420 para Facturas B. También faltan 30 (Exterior Persona Jurídica), 91 (Exterior Persona Física), 94 (Pasaporte).

**Síntoma:** si un cliente tiene sólo CDI cargado (algunos extranjeros residentes), no se puede emitir factura porque el enum no lo tiene. Hoy probablemente cae al `else` en `invoice_service.py:127` y manda `FINAL_CONSUMER`, enmascarando el caso.

**Fix:** agregar al enum, agregar al `valid_doc_types` en `billing.py:186`.

---

## 🟠 BUG #7 — Falta validación preventiva FCE con DocNro 23000000000

**Archivo:** `apps/afip/services/validations.py` / `invoice_service.py`

**Regla del manual (códigos 10178 / 1475):** FCE no permite informar DocNro = 23000000000 ("No Categorizado"). Es rechazo excluyente.

**Estado actual:** ninguna validación local detecta esto. Si el cliente tiene CUIT ficticio 23000000000 (No Categorizado) y se intenta FCE, AFIP rechaza con 10178.

**Fix:** agregar validator en `validations.py`:

```python
def validate_fce_docnro(invoice_data):
    if invoice_data.receipt_type.is_fce and str(invoice_data.document_number) == "23000000000":
        return False, 10178, None
    return True, None, None
```

---

## 🟠 BUG #8 — `valid_related_types` demasiado restrictivo para NC/ND

**Archivo:** `apps/afip/services/billing.py:209`

```python
valid_related_types = [1, 6, 11, 201, 206, 211]
```

**Regla del manual (código 10040):**
- ND/NC A (2, 3) puede asociar: `1, 2, 3, 4, 5, 34, 39, 60, 63, 88, 991`.
- ND/NC B (7, 8) puede asociar: `6, 7, 8, 9, 10, 35, 40, 61, 64, 88, 991`.
- ND/NC C (12, 13) puede asociar: `11, 12, 13, 15`.
- FCE ND/NC puede asociar NC/ND previas (para anulación) — códigos 10186 / 10187 / 10193.

**Síntoma:** no se puede emitir NC sobre un recibo (4, 9, 15), ni anular una NC con otra ND, ni asociar remitos (88, 991). AFIP lo permite; nosotros lo rechazamos localmente.

**Fix:** reconstruir la lista por tipo de comprobante a emitir (ND/NC A vs B vs C vs FCE).

---

## 🟡 BUG #9 — Validación Factura A requiere CUIT sin contemplar CUIL/CDI

**Archivo:** `apps/afip/services/validations.py:46-56`

```python
def validate_cuit_for_type_a(invoice_data):
    if receipt_type.letter == "A" and document_type != DocType.CUIT:
        return False, None, "Invoice A requires CUIT (80)"
```

**Regla del manual (código 10013):** "Para comprobantes clase A y M el campo DocTipo tenga valor **80 (CUIT)**". Textual.

Entonces este validator está correcto en la regla — solo 80 vale para A. **Este bug no es bug.** Lo dejo anotado para que quede confirmado en la auditoría.

---

## 🟡 BUG #10 — `ImpTotConc` e `ImpOpEx` hardcoded en 0

**Archivo:** `apps/afip/services/billing.py:265-267`

```python
imp_tot_conc = 0  # neto no gravado
imp_op_ex = 0     # operaciones exentas
```

**Regla del manual:** ambos campos son obligatorios pero pueden ser > 0. Por ejemplo Factura B a un Exento puede tener un componente `ImpOpEx > 0`.

**Síntoma:** si alguna operación tiene componentes no gravados o exentos (ej: venta de libros mezclada con productos gravados), no puede expresarlo. Hoy en el flujo desde quote probablemente no se presente, pero es una limitación.

**Fix:** extender `InvoiceData` con estos campos y propagarlos desde `invoice_service`.

---

## 🟡 BUG #11 — Falta `CanMisMonExt` cuando `MonId` ≠ PES

**Archivo:** `apps/afip/services/billing.py:291` (XML)

**Regla del manual (códigos 10239 / 10240 / 10241):**
- Si `MonId = PES`, no informar `CanMisMonExt` (código 10241).
- Si `MonId ≠ PES`, informar `CanMisMonExt = "S" | "N"` (código 10239).

**Estado actual:** el XML no incluye ni `CanMisMonExt`. Como `self._currency_id = "PES"` (settings), está "bien por accidente". Pero si algún día facturan en USD, faltaría.

Hoy **no es bug runtime** (no se factura en moneda extranjera), pero es deuda técnica documentada.

---

## 🟡 BUG #12 — XML construido con f-strings sin escape

**Archivo:** `apps/afip/services/billing.py:291-334`, `_build_reference_block`, `_build_opcionales_block`

Todas las concatenaciones de strings dentro del XML (reference, document_number, cbu, etc.) se hacen con f-strings crudos. Si alguno de esos valores contiene `<`, `>`, `&`, o `"`, se rompe el XML.

**Vectores concretos:**
- `invoice_data.reference` (línea 289) — viene del campo `reason` de NC, entrada de usuario.
- `invoice_data.cbu`, `transfer_type` — no deberían tener esos chars pero nadie lo valida.

**Regla del manual:** ninguna específica, pero el XML SOAP debe estar bien formado.

**Fix:** usar `html.escape()` o (mejor) construir el XML con `xml.etree.ElementTree` en vez de string templating.

---

## 🟢 Validaciones correctas confirmadas (no son bugs)

Para no dejar dudas, estos están bien:

- `validate_cuit_for_type_a` (validations.py:46) — coherente con código 10013.
- `validate_iva_block_consistency` (validations.py:73) — coherente con 10070 y 10071.
- `validate_no_categorizado` (validations.py:59) — coherente con 10067 para B con NC.
- `is_type_c` y `imp_iva = 0` en tipo C (billing.py:271) — coherente con 1438/10071.
- FCE validations en `_validate_invoice_data` (billing.py:227-244) — CBU 22 dígitos numéricos, transfer_type SCA/ADC, payment_due_date obligatorio. Coherentes con 10165, 10215, 10163.
- Estructura `Opcionales` para FCE (billing.py:354) — ids 2101, 27, 22 coherentes con 10168, 10216, 10173.

---

## Prioridad de fixes sugerida

| # | Severidad | Riesgo | Fix estimado |
|---|---|---|---|
| 1 | 🔴 Crítico | Rechazo AFIP hoy para cualquier cliente NA | 1 línea |
| 2 | 🔴 Crítico | Rechazos locales falsos para Exterior, Monotributo, etc. | ~20 líneas |
| 3 | 🔴 Crítico | Combinaciones inválidas permitidas / válidas rechazadas | ~30 líneas + tests |
| 5 | 🟠 | Oculta errores de configuración | 3 líneas |
| 7 | 🟠 | Mensaje de error confuso en caso específico | ~10 líneas |
| 6 | 🟠 | Clientes con CDI no facturables | ~5 líneas |
| 4 | 🟠 | Alícuotas distintas a 21% no soportadas | ~50 líneas + DTO |
| 8 | 🟠 | NC sobre recibos no soportada | ~15 líneas |
| 10, 11 | 🟡 | Limitaciones sin síntoma hoy | diferible |
| 12 | 🟡 | XML roto con caracteres especiales en referencia | escape o librería XML |

**Sugerencia:** meter los 3 rojos + 5 + 6 + 7 en una sola PR chica (todo apunta al mismo dominio: mapeo `IvaChoices ↔ CondicionIVAReceptorId` + matriz compatibilidad + DocTypes). Es el root cause del error 10243 que viste.
