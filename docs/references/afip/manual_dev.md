# Manual de Facturación Electrónica AFIP/ARCA — Guía de Desarrollo

> **Fuente normativa:** Manual del Desarrollador ARCA — Facturación Electrónica, RG 4291, Proyecto FE v4.0, revisión 17-Mar-2025.
> **Servicio:** WSFEv1 (Web Service de Factura Electrónica, método de autenticación "wsfe").
> **Modalidades de autorización:** CAE (tiempo real) y CAEA (informe posterior).
> **Este documento describe exclusivamente CAE** (el sistema usa CAE).

---

## Índice

1. [Endpoints y autenticación](#endpoints-y-autenticación)
2. [Tipos de Comprobante (código `CbteTipo`)](#tipos-de-comprobante-código-cbtetipo)
3. [Condición frente al IVA del Receptor](#condición-frente-al-iva-del-receptor)
4. [Tipos de Documento (`DocTipo`)](#tipos-de-documento-doctipo)
5. [Campos principales del request](#campos-principales-del-request)
6. [Validaciones por clase de comprobante](#validaciones-por-clase-de-comprobante)
7. [Umbral RG 4444 (monto dinámico para identificación del receptor)](#umbral-rg-4444-monto-dinámico-para-identificación-del-receptor)
8. [Notas de Crédito y Débito (comunes)](#notas-de-crédito-y-débito-comunes)
9. [Facturas MiPyMEs — FCE](#facturas-mipymes--fce)
10. [Códigos Opcionales](#códigos-opcionales)
11. [Comprobantes asociados (matriz)](#comprobantes-asociados-matriz)
12. [`CondicionIVAReceptorId` (RG 5616)](#condicionivareceptorid-rg-5616)
13. [Códigos de error críticos](#códigos-de-error-críticos)
14. [Casos especiales](#casos-especiales)
15. [Checklist de implementación](#checklist-de-implementación)

---

## Endpoints y autenticación

```
WSAA  (auth)   Prod → https://wsaa.afip.gov.ar/ws/services/LoginCms
               Homo → https://wsaahomo.afip.gov.ar/ws/services/LoginCms
WSFEv1 (fact.) Prod → https://servicios1.afip.gov.ar/wsfev1/service.asmx
               Homo → https://wswhomo.afip.gov.ar/wsfev1/service.asmx
```

- Para WSAA el `service` del `LoginTicketRequest` debe ser `wsfe`. El TA tiene **12 h** de duración.
- Todas las llamadas al WSFEv1 requieren `Token`, `Sign` y `Cuit` del emisor (o representado).

### Operaciones principales usadas

| Método | Propósito |
|--------|-----------|
| `FECAESolicitar` | Solicitar CAE para 1 o N comprobantes (1 para FCE) |
| `FECompUltimoAutorizado` | Último comprobante autorizado por (CbteTipo, PtoVta) |
| `FECompConsultar` | Consultar un comprobante por (CbteTipo, PtoVta, Nro) |
| `FEParamGetTiposCbte` | Tipos de comprobante vigentes |
| `FEParamGetTiposDoc` | Tipos de documento vigentes |
| `FEParamGetTiposIva` | Alícuotas IVA vigentes |
| `FEParamGetTiposMonedas` | Monedas |
| `FEParamGetCotizacion` | Cotización de moneda (acepta fecha opcional) |
| `FEParamGetTiposOpcional` | Catálogo de códigos Opcionales |
| `FEParamGetCondicionIvaReceptor` | Condiciones IVA receptor y clases válidas |
| `FEParamGetPtosVenta` | Puntos de venta habilitados |

---

## Tipos de Comprobante (código `CbteTipo`)

Lista completa habilitada en WSFEv1 (código de validación **10007**):

### Clase A

| `CbteTipo` | Descripción |
|:---:|-------------|
| 1 | Factura A |
| 2 | Nota de Débito A |
| 3 | Nota de Crédito A |
| 4 | Recibo A |
| 5 | Notas de Venta al Contado A |
| 34 | Cbtes. A del Anexo I, Apartado A, inc. f) RG 1415 |
| 39 | Otros Cbtes. A no especificados |
| 60 | Cta. de venta y líquido prod. A |
| 63 | Liquidación A |
| 201 | **FCE A** (Factura de Crédito Electrónica MiPyMEs) |
| 202 | **ND FCE A** |
| 203 | **NC FCE A** |

### Clase B

| `CbteTipo` | Descripción |
|:---:|-------------|
| 6 | Factura B |
| 7 | Nota de Débito B |
| 8 | Nota de Crédito B |
| 9 | Recibo B |
| 10 | Notas de Venta al Contado B |
| 35 | Cbtes. B del Anexo I, Apartado A, inc. f) RG 1415 |
| 40 | Otros Cbtes. B no especificados |
| 61 | Cta. de venta y líquido prod. B |
| 64 | Liquidación B |
| 206 | **FCE B** |
| 207 | **ND FCE B** |
| 208 | **NC FCE B** |

### Clase C

| `CbteTipo` | Descripción |
|:---:|-------------|
| 11 | Factura C |
| 12 | Nota de Débito C |
| 13 | Nota de Crédito C |
| 15 | Recibo C |
| 211 | **FCE C** |
| 212 | **ND FCE C** |
| 213 | **NC FCE C** |

### Clase M (solo CAEA, observada en CAE)

| `CbteTipo` | Descripción |
|:---:|-------------|
| 51 | Factura M |
| 52 | Nota de Débito M |
| 53 | Nota de Crédito M |
| 54 | Recibo M |

### Bienes Usados

| `CbteTipo` | Descripción |
|:---:|-------------|
| 49 | Comprobante de Compra de Bienes Usados a Consumidor Final |

---

## Condición frente al IVA del Receptor

> ⚠️ **El anexo escrito del manual está desactualizado respecto al runtime de AFIP.** La verdad operativa es lo que devuelve `FEParamGetCondicionIvaReceptor`. Esta sección refleja la respuesta runtime verificada (abril 2026). Consultable localmente con:
>
> ```bash
> python src/backend/manage.py afip_iva_receptor_codes A   # o B, C, M, BU
> ```

### Factura A — solo contribuyentes que discriminan IVA (4 opciones)

| Id | Descripción |
|:---:|---|
| 1  | IVA Responsable Inscripto |
| 6  | Responsable Monotributo |
| 13 | Monotributista Social |
| 16 | Monotributo Trabajador Independiente Promovido |

### Factura B — solo contribuyentes que NO discriminan IVA (7 opciones)

| Id | Descripción |
|:---:|---|
| 4  | IVA Sujeto Exento |
| 5  | Consumidor Final |
| 7  | Sujeto No Categorizado |
| 8  | Proveedor del Exterior |
| 9  | Cliente del Exterior |
| 10 | IVA Liberado – Ley N° 19.640 |
| 15 | IVA No Alcanzado |

### Factura C — todas las condiciones (11 opciones)

Todas las condiciones listadas arriba son válidas para Factura C. AFIP la acepta como "comodín" (emisor Monotributo/Exento a cualquier receptor).

### FCE (MiPyMEs) — reglas extra más estrictas (código 1474/10177)

- **FCE A** (201, 202, 203): receptor activo en IVA (1) o Monotributo (6).
- **FCE B y FCE C** (206, 207, 208, 211, 212, 213): receptor activo en IVA (1), Monotributo (6) o Exento (4).

### Claves prácticas

- **RI y MT reciben A, nunca B.** AFIP rechaza B con CondicionIVAReceptorId=1 o 6 con código 10243.
- **Exento recibe B, nunca A.** Mismo error 10243 si intentás A.
- **CF recibe B o C**, nunca A.
- **C es el "comodín"** — acepta cualquier receptor.

---

## Tipos de Documento (`DocTipo`)

Los valores vigentes se obtienen vía `FEParamGetTiposDoc`. Los más comunes:

| Código | Documento |
|:---:|---|
| 80 | CUIT (11 dígitos) |
| 86 | CUIL (11 dígitos) |
| 87 | CDI (11 dígitos) |
| 96 | DNI (hasta 8 dígitos) |
| 99 | Consumidor Final (valor `DocNro = 0`) |
| 30 | Documento extranjero — Persona jurídica |
| 91 | Documento extranjero — Persona física |
| 94 | Pasaporte |

**Longitud `DocNro`**: entre 0 y 99.999.999.999 para tipo B/C (código **1405**); entre 20.000.000.000 y 60.000.000.000 para tipo A (código **1421**).

---

## Campos principales del request

Estructura `FECAEDetRequest` (detalle por comprobante). Campos obligatorios salvo nota contraria:

| Campo | Tipo | Detalle |
|---|---|---|
| `Concepto` | Int | 1=Productos, 2=Servicios, 3=Productos y Servicios (código 713) |
| `DocTipo` | Int | Ver tabla anterior |
| `DocNro` | Long | Número de documento del receptor |
| `CbteDesde` / `CbteHasta` | Long | Rango del lote (iguales para Clase A, C y FCE — código **711** y **1433**) |
| `CbteFch` | String (yyyymmdd) | Ver rangos de fecha más abajo |
| `ImpTotal` | Double (13+2) | = ImpTotConc + ImpNeto + ImpOpEx + ImpIVA + ImpTrib (código **10048**) |
| `ImpTotConc` | Double | Neto no gravado. Para Clase C debe ser 0 (código **1434**) |
| `ImpNeto` | Double | Neto gravado. Para Clase C = subtotal (código **1436**) |
| `ImpOpEx` | Double | Exento. Para Clase C debe ser 0 (código **1435**) |
| `ImpIVA` | Double | Suma de `Iva.AlicIva.Importe`. Para Clase C debe ser 0 (código **1438**) |
| `ImpTrib` | Double | Suma de `Tributos.Tributo.Importe` |
| `MonId` | String (3) | PES para pesos, USD, etc. (código 1401) |
| `MonCotiz` | Double | 1 si MonId=PES; sino > 0 (código **10039** / **10119**) |
| `CanMisMonExt` | String (1) | "S" o "N" — cancelación en misma moneda extranjera (código **10239/10241**). No informar si PES. |
| `CondicionIVAReceptorId` | Int | Ver [sección RG 5616](#condicionivareceptorid-rg-5616) |
| `FchVtoPago` | String | Obligatorio para Concepto 2/3 **o** FCE Factura (código **10163**) |
| `FchServDesde` / `FchServHasta` | String | Obligatorios para Concepto 2/3 |

### Rango de fechas `CbteFch` (código **10016**)

| Tipo | Rango permitido (N = fecha de envío) |
|---|---|
| Concepto 1 (productos) común | N-5 a N+5 (no puede exceder mes de presentación) |
| Concepto 2/3 (servicios) común | N-10 a N+10 |
| **FCE Factura** | **N-5 a N+1** |
| **FCE ND/NC** | Hasta N-5, y ≥ fecha del comprobante asociado |

---

## Validaciones por clase de comprobante

### Clase A (códigos 1, 2, 3, 201, 202, 203)

```
DocTipo = 80 (CUIT)                                      # 10013 / 1403
DocNro  ∈ padrón AFIP activo                             # 10017 (observación) / 10063
ImpIVA  > 0 si ImpNeto > 0                               # 10018 / 10070
Receptor: condición IVA válida A/M                       # 10243
CbteDesde = CbteHasta                                    # 711
```

### Clase B (códigos 6, 7, 8, 206, 207, 208)

Ver [Umbral RG 4444](#umbral-rg-4444-monto-dinámico-para-identificación-del-receptor). Resumen:

```
Si ImpTotal/registros < RG4444 y pedido múltiple:
    DocTipo = 99, DocNro = 0                             # 10015 caso 1 / 1415

Si ImpTotal < RG4444 (individual):
    DocTipo = 99 → DocNro = 0                            # 10015 caso 2 / 1418
    DocTipo ∈ {80, 86, 87} → DocNro en padrón            # 10015 caso 3 / 1420

Si ImpTotal ≥ RG4444 (individual):
    DocTipo ≠ 99                                         # 10015 caso 4 / 1417
    DocNro > 0                                           # 1419
    DocTipo = 80 → DocNro en padrón (excepción: 23000000000 "No Categorizado")

Bloque IVA obligatorio si ImpNeto > 0                    # 10070
```

### Clase C (códigos 11, 12, 13, 211, 212, 213)

```
ImpTotConc = 0, ImpOpEx = 0, ImpIVA = 0                  # 1434, 1435, 1438
ImpNeto    = subtotal                                    # 1436
No informar array Iva                                    # 1443 / 10071
ImpTotal   = ImpNeto + ImpTrib                           # 1439

Documento:
    DocTipo = 99, DocNro = 0    (consumidor final)       # 10015
    DocTipo = 80 requerido si ImpTotal ≥ RG4444          # 1417
    CbteDesde = CbteHasta                                # 1433
```

> **IMPORTANTE:** la "excepción de $10.000.000" que circulaba en versiones previas de este documento **no existe en el manual**. El umbral que obliga a informar CUIT es el de **RG 4444 vigente** (mismo umbral que para Clase B), actualizado por RG posteriores.

### Clase 49 (Bienes Usados)

```
Emisor debe estar empadronado en bienes usados          # 10000
Concepto = 1 (Productos) obligatorio                    # 10085
DocTipo ∈ {80, 86, 87} y en padrón                      # 10015
Opcionales obligatorios: 91 (nombre), 92 (país), 93 (domicilio)  # 10076-10084
Si emisor es Monotributista:
    ImpNeto = 0 / no informar
    ImpTotConc = subtotal
    No informar array Iva                                # 10075
```

---

## Umbral RG 4444 (monto dinámico para identificación del receptor)

**No usar un valor hardcodeado.** El monto en pesos se deriva de la RG 4444/2019 y sus actualizaciones (RG 5616 entre otras). ARCA no expone el valor por WS; se debe:

1. Consultarlo en el micrositio de Facturación Electrónica, o
2. Configurarlo como variable del sistema y actualizarlo cuando ARCA publique cambios.

El cálculo base para pedidos múltiples: `ImpTotal * MonCotiz / (CbteHasta - CbteDesde + 1)`.

---

## Notas de Crédito y Débito (comunes)

### Mapeo Factura → Nota

| Factura | → ND | → NC |
|:---:|:---:|:---:|
| 1 (A) | 2 | 3 |
| 6 (B) | 7 | 8 |
| 11 (C) | 12 | 13 |
| 201 (FCE A) | 202 | 203 |
| 206 (FCE B) | 207 | 208 |
| 211 (FCE C) | 212 | 213 |

### Reglas

- Toda ND/NC **debe asociar** el comprobante original vía `CbtesAsoc` (salvo casos específicos, código **10040**).
- Fecha de la nota **≥** fecha del comprobante asociado.
- Si el comprobante asociado es electrónico y tiene fecha posterior al que se autoriza, ambos deben ser del **mismo mes/año** (código **10210**).
- Importes: la **NC no puede superar** el monto del comprobante asociado (observación **10237**).
- Para ND/NC Clase A/B: los montos de IVA y base pueden ajustarse proporcionalmente en notas parciales.
- Para ND/NC Clase C: no lleva IVA.

---

## Facturas MiPyMEs — FCE

Régimen establecido por la Ley 27.440. Los comprobantes FCE tienen validaciones específicas además de las de su clase (A, B o C).

### Cuándo corresponde emitir FCE

La observación **10188** / **10192** / **1485** se dispara cuando la categorización de las CUITs emisora/receptora y el monto superan el tope → se debería facturar con FCE en vez de comprobante común.

### Requisitos del emisor

- Registrado como **PYME régimen FCE** (o habrá error 10000 mensaje "10").
- Con **domicilio fiscal electrónico** activo (10000 mensaje "11").
- Al menos una actividad económica activa.

### Requisitos del receptor

| Validación | Regla |
|---|---|
| 1487 | `DocTipo` **debe** ser 80 (CUIT) |
| 1475/10178 | `DocNro` **no puede** ser 23000000000 ("No Categorizado") |
| 1446/10176 | `DocNro` debe estar en padrón AFIP, activo |
| 1458/10161 | Receptor debe tener **domicilio fiscal electrónico** activo |
| 1476/10180 | Receptor debe estar caracterizado como **GRANDE** o haber **optado por PYME** (actividad principal alcanzada) |
| 1474/10177 A | Receptor activo en IVA o Monotributo |
| 1474/10177 B | Receptor activo en IVA, Monotributo o Exento |
| 1474/10177 C | Receptor activo en IVA, Monotributo o Exento |

### Límites operativos

- **1 comprobante por request** (código **10003**).
- `CbteDesde` = `CbteHasta` siempre (código **711**).

### Datos obligatorios por subtipo FCE

| Campo / Código Opcional | FCE Factura (201, 206, 211) | FCE ND/NC (202, 203, 207, 208, 212, 213) |
|---|:---:|:---:|
| `FchVtoPago` | ✅ Obligatorio (10163) | ❌ NO informar, salvo si *es de anulación* (10175) |
| `CbtesAsoc` | Opcional (solo remitos 91, 990, 991, 993, 994, 995 — código 10040) | ✅ Obligatorio (10153) |
| Opcional **2101** (CBU, 22 numéricos) | ✅ Obligatorio (10168) | ❌ NO informar (10172) |
| Opcional **2102** (ALIAS, 6–20 alfanum) | Opcional, complementario al CBU (10166) | ❌ NO informar (10172) |
| Opcional **27** (transferencia SCA/ADC) | ✅ Obligatorio (10216) | ❌ NO informar (10172) |
| Opcional **22** (anulación S/N) | ❌ NO informar (10171) | ✅ Obligatorio (10173) |
| Opcional **23** (referencia comercial, 50 char) | Opcional (10189) | Opcional |

> **Al menos uno de 2101 / 22 / 27** debe informarse en todo FCE (código **10170**).
> **CBU**: debe estar **registrado en AFIP, vigente y pertenecer al emisor** (código **10174**). No se puede "saltar" este requisito; es estructural del régimen FCE.

### `FchVtoPago` en FCE (código 10164)

Debe ser **posterior o igual** a la mayor entre `CbteFch` y la fecha actual (fecha de presentación).

### Transferencia (Opcional 27)

Valores únicos permitidos (código **10215**):

| Valor | Significado |
|:---:|---|
| `SCA` | Transferencia al Sistema de Circulación Abierta |
| `ADC` | Agente de Depósito Colectivo |

Son **excluyentes** (se informa uno u otro, no ambos).

### Comprobantes asociables en ND/NC FCE (código 10040 y 10157)

| Nota FCE | Puede asociar |
|---|---|
| 202 / 203 (A) | 201, 202, 203 |
| 207 / 208 (B) | 206, 207, 208 |
| 212 / 213 (C) | 211, 212, 213 |

Además, sobre la **anulación** (Opcional 22):
- `S` (anulación) → ND asocia NC, NC asocia factura o ND (código 10183).
- Para ND/NC de anulación Clase A solo se asocia crédito A (código **10186**); igual para B (10187) y C (10193).

### Moneda en ND/NC FCE (código 10181)

Debe tener la **misma moneda** que el comprobante asociado, o ser **PES** para ajuste por diferencia de cambio post aceptación/rechazo.

### Saldo de cuenta corriente (código 10184)

El monto de la NC FCE no puede superar el saldo actual de la cuenta corriente FCE del emisor.

---

## Códigos Opcionales

Array `Opcionales` del request. Solo se puede informar si `CbteTipo` ∈ {1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 15, 49, 51, 52, 53, 54, 201, 202, 203, 206, 207, 208, 211, 212, 213} (código **10068**).

| Id | Descripción | Clase / Contexto |
|:---:|---|---|
| 2 | Nº identificador proyecto Prom. Industrial | A/B solo (1,2,3,6,7,8) |
| 5 | EXCEPCION RG 3668 (2 char) | A |
| 7 | Carácter firmante RG 3668 | A |
| 10 | RG 3368 Educación pública gestión privada | A/B/C |
| 11 | RG 2820 Bienes inmuebles | A/B/C |
| 12 | RG 3687 Locación temporaria turística | A/B/C |
| 13 | RG 2863 Representantes de modelos | — |
| 14 | RG 2863 Agencias de publicidad | — |
| 15 | RG 2863 Modelos | — |
| 17 | RG 4004-E Alquiler casa-habitación | B/C |
| 22 | **FCE — Anulación** (S / N) | FCE ND/NC |
| 23 | Referencia comercial (alfanum 50) | Cualquier tipo habilitado |
| 27 | **FCE — Transferencia** (SCA / ADC) | FCE Factura |
| 61 | RG 3668 Tipo doc firmante | A |
| 62 | RG 3668 N° doc firmante (11 char) | A |
| 91 | Nombre y apellido (Bienes Usados) | 49 |
| 92 | Código país (Bienes Usados) | 49 |
| 93 | Domicilio (Bienes Usados) | 49 |
| 1011 / 1012 | Tipo/N° doc titular de pago (RG 3368) | A (si id=10 valor=1) |
| 1801 / 1802 | CUIT / Denominación cotitular (RG 4004-E) | B/C |
| **2101** | **CBU (22 numéricos)** | FCE Factura |
| **2102** | **ALIAS (6–20 alfanum)** | FCE Factura |

### Regla clave (10169)

Si el comprobante **NO** es FCE, **no informar** los códigos 2101, 2102, 22, 27. Emitiría error.

---

## Comprobantes asociados (matriz)

Tabla de asociaciones permitidas (código **10040** y **10157**):

| `CbteTipo` a autorizar | Puede asociar |
|---|---|
| 2, 3 (ND/NC A) | 1, 2, 3, 4, 5, 34, 39, 60, 63, 88, 991 |
| 7, 8 (ND/NC B) | 6, 7, 8, 9, 10, 35, 40, 61, 64, 88, 991 |
| 12, 13 (ND/NC C) | 11, 12, 13, 15 |
| 52, 53 (ND/NC M) | 51, 52, 53, 54, 88, 991 |
| 1, 6, 51 (Facturas A/B/M) | 88, 991 (remitos) |
| 201, 206, 211 (FCE Facturas) | 91, 990, 991, 993, 994, 995 |
| 202, 203 (FCE ND/NC A) | 201, 202, 203 |
| 207, 208 (FCE ND/NC B) | 206, 207, 208 |
| 212, 213 (FCE ND/NC C) | 211, 212, 213 |

Para asociados 91, 88, 988, 990, 991, 993, 994, 995, 996, 997: deben estar registrados, confirmados, y el receptor del asociado = receptor del comprobante a autorizar (códigos **10120, 10121, 10122**).

---

## `CondicionIVAReceptorId` (RG 5616)

Campo nuevo agregado en la v4.0 (17-Mar-2025).

- **Opcional desde 06-Abr-2025**.
- **Obligatorio** cuando ARCA lo reglamente (aviso en manual).
- Los valores válidos son los de la [tabla del Anexo](#condición-frente-al-iva-del-receptor).
- Validaciones:
  - **10242** — valor no permitido.
  - **10243** — valor no válido para la clase de comprobante informado.
  - **10246** — campo obligatorio (cuando entre en vigencia).
  - **10245** — observación informativa de obligatoriedad próxima.

**Recomendación**: enviarlo siempre. Ya está operativo y evita observaciones/rechazos cuando se active la obligatoriedad.

---

## Códigos de error críticos

### `<Auth>` / CUIT emisor

| Código | Motivo |
|---|---|
| 10000 | CUIT emisor no registrada/activa. El `Msg` incluye 01..11: 01 no es RI, 02 no habilitado, 03 problema domicilio, 04 no habilitado para A/FCE, 05 CUIT no registrada, 06 sin actividad, 07 no habilitado bienes usados, 08 no exento, 09 no habilitado M, **10 no registrada como PYME FCE**, **11 domicilio fiscal electrónico inactivo**. |

### Documento del receptor

| Código | Motivo |
|---|---|
| 10013 / 1403 | Clase A/M: `DocTipo` debe ser 80 (CUIT) |
| 10015 / 1417-1419 / 1415 / 1422 | Combinación inválida `DocTipo`/`DocNro`/monto RG 4444 |
| 10017 | Observación: `DocNro` A/M no está en padrón activo |
| 10063 | Observación: receptor A/M no activo en IVA/Monotributo |
| 10069 | `DocNro` receptor = emisor (prohibido) |
| 10238 | CUIT receptora no existe |
| 1487 | FCE: documento receptor debe ser 80 (CUIT) |
| 1475 / 10178 | FCE: no se permite `DocNro` 23000000000 |

### Condición IVA receptor

| Código | Motivo |
|---|---|
| 10242 | `CondicionIVAReceptorId` no es valor permitido |
| 10243 | `CondicionIVAReceptorId` no válido para la clase |
| 10246 | Campo obligatorio (RG 5616 en vigencia) |

### Montos e IVA

| Código | Motivo |
|---|---|
| 10018 | Si `ImpIVA=0`, array IVA solo con `Id=3` (iva 0%) |
| 10023 | Suma de `AlicIva.Importe` ≠ `ImpIVA` |
| 10048 | `ImpTotal` ≠ suma de subtotales |
| 10061 | Suma de `AlicIva.BaseImp` ≠ `ImpNeto` |
| 10070 | Si `ImpNeto>0`, array IVA obligatorio |
| 10071 / 1443 | Clase C no debe informar array IVA |
| 1434-1438 | Clase C: `ImpTotConc`/`ImpOpEx`/`ImpIVA`=0, `ImpNeto`=subtotal |
| 10119 | Cotización fuera de rango (-2%, +400%) |

### Comprobantes asociados

| Código | Motivo |
|---|---|
| 10040 | `CbteTipo` no puede llevar asociados / tipo asociado inválido |
| 10041 | Asociado electrónico no existe en bases |
| 10151 | CUIT en `CbteAsoc` inválido (<>11 dígitos) |
| 10210 | Asociado posterior → ambos deben ser mismo mes/año |

### FCE específicos

| Código | Motivo |
|---|---|
| 10153 | FCE ND/NC: asociado obligatorio |
| 10154 | FCE ND/NC: falta código 22 de anulación |
| 10155 | FCE: CUIT emisor del asociado ≠ CUIT emisor |
| 10156 | FCE ND/NC no de anulación: asociar 1 factura |
| 10161 | FCE: receptor sin domicilio fiscal electrónico |
| 10162 | FCE: `Opcionales` obligatorio |
| 10163 | FCE Factura: `FchVtoPago` obligatorio |
| 10164 | FCE: `FchVtoPago` ≥ `CbteFch` y ≥ fecha actual |
| 10165 | FCE: CBU (2101) debe ser numérico 22 |
| 10166 | FCE: ALIAS (2102) alfanum 6–20 |
| 10167 | FCE: código 22 debe ser "S" o "N" |
| 10168 | FCE Factura: CBU obligatorio |
| 10169 | NO-FCE: no informar 2101/2102/22/27 |
| 10170 | FCE: al menos uno de 2101/22/27 |
| 10171 | FCE Factura: no informar código 22 |
| 10172 | FCE ND/NC: no informar CBU/ALIAS/Transferencia |
| 10173 | FCE ND/NC: código 22 obligatorio |
| 10174 | FCE: CBU debe estar registrado, vigente y pertenecer al emisor |
| 10175 | `FchVtoPago` solo en FCE Factura o ND/NC de anulación |
| 10180 | FCE: receptor debe ser GRANDE o PYME |
| 10183 | FCE ND/NC: emisores y receptores deben coincidir |
| 10184 | FCE NC: monto > saldo cuenta corriente |
| 10194 | FCE: no se permiten `Compradores` |
| 10196 | FCE: no se permite `PeriodoAsoc` |
| 10214 | FCE: código 27 debe ser alfanum 3 caracteres |
| 10215 | FCE: código 27 valores SCA o ADC |
| 10216 | FCE Factura: `Opcionales` con id=27 obligatorio |

### Observaciones (no bloqueantes)

| Código | Motivo |
|---|---|
| 10017 | `DocNro` A/M no está en padrón activo |
| 10041 | Asociado electrónico no en bases |
| 10063 | Receptor A/M no activo en IVA/Monotributo |
| 10188 | Por categorización + monto, corresponde FCE |
| 10195 | CUIT receptor en consulta de facturas apócrifas |
| 10217 | Crédito fiscal a Monotributista — computar solo en régimen transición |
| 10234 | F.H. comprobantes pendiente / anterior a alta IVA |
| 10235 | Monto excede máximo Monotributo (exclusión automática) |
| 10236 | Monto excede categoría Monotributo (recategorización) |
| 10237 | NC supera monto del asociado |

---

## Casos especiales

### Receptor Monotributista (cód. IVA 6)

**Post Ley 27.618 (desde 01-Jun-2021):**

- **PUEDE** recibir Factura A. Se observa con 10217.
- PUEDE recibir Factura B.
- PUEDE recibir FCE A si está activo en Monotributo (validación 1474/10177).
- PUEDE recibir FCE B.
- **NO** recibe Factura C (la emisión a RI/Mon/Ex con C no es el caso típico; C se emite cuando el **emisor** es Monotributista/Exento a cualquier receptor salvo RI).

### Receptor Consumidor Final (cód. IVA 5)

- Factura B, Factura C, Bienes Usados (49).
- **No** puede recibir FCE (todos los FCE exigen receptor CUIT categorizado).

### No Categorizado (`DocNro = 23000000000`)

- Permitido en Clase B (código 10015 excepción).
- **NO** se valida contra padrón (código 10015 excepción).
- Requiere `ImpTrib > 0` en Clase B con montos altos (código **10067 / 1425**).
- **Prohibido en FCE** (código 10178/1475).

### Emisor Exento en IVA

- Punto de venta específico: "COMPROBANTES – EXENTO EN IVA – WEB SERVICES" (código **10096**).
- Puede emitir C y B.

### Factura A a cliente del exterior

- Válido (cód. IVA receptor 8 o 9). Es el esquema de exportación vía factura E en realidad; el WSFEv1 soporta el flujo si la CUIT emisora está habilitada.

### Bienes Usados (`CbteTipo = 49`)

- Emisor debe estar empadronado en el régimen de bienes usados (código 10000 mensaje 07).
- Emisor Monotributista: `ImpTotConc` = subtotal, sin IVA (códigos 10043, 10075).
- Opcionales obligatorios: **91** (nombre), **92** (país), **93** (domicilio) del vendedor.

---

## Checklist de implementación

### Pre-request (validaciones en el sistema antes de llamar a AFIP)

- [ ] Resolver `CbteTipo` según clase del emisor y condición IVA del receptor (consultar `FEParamGetCondicionIvaReceptor`).
- [ ] Validar `DocTipo`/`DocNro` contra el monto y la clase (ver sección [Validaciones por clase](#validaciones-por-clase-de-comprobante)).
- [ ] Para Clase A: verificar que el receptor tenga CUIT y esté en padrón (cachear respuesta del padrón por X horas).
- [ ] Calcular `ImpTotal = ImpTotConc + ImpNeto + ImpOpEx + ImpIVA + ImpTrib` con tolerancia `<= 0.01`.
- [ ] Para Clase C: forzar `ImpTotConc=0`, `ImpOpEx=0`, `ImpIVA=0`, omitir array IVA.
- [ ] Obtener `CbteDesde` = `FECompUltimoAutorizado + 1` (y para Clase A/C/FCE también `CbteHasta`).
- [ ] Validar rango de `CbteFch` según tipo y concepto.
- [ ] Setear `CondicionIVAReceptorId` (recomendado).

### Específico FCE

- [ ] Verificar que el emisor esté empadronado como PYME FCE.
- [ ] Verificar que el receptor sea GRANDE o PYME (consulta padrón).
- [ ] Validar que el receptor tenga domicilio fiscal electrónico activo.
- [ ] Si **FCE Factura** (201/206/211):
  - [ ] Informar `FchVtoPago` (posterior a emisión y fecha actual).
  - [ ] Armar `Opcionales` con:
    - `Id=2101` → CBU del emisor (22 dígitos, registrado en AFIP, vigente).
    - `Id=27` → "SCA" o "ADC".
    - (Opcional) `Id=2102` → ALIAS.
    - (Opcional) `Id=23` → referencia comercial.
  - [ ] No informar `Id=22`.
- [ ] Si **FCE ND/NC** (202, 203, 207, 208, 212, 213):
  - [ ] Asociar la Factura FCE original en `CbtesAsoc`.
  - [ ] Informar `Opcionales` con:
    - `Id=22` → "S" (anulación) o "N" (no anulación).
  - [ ] NO informar 2101, 2102, 27.
  - [ ] Informar `FchVtoPago` solo si es de anulación.

### Manejo de respuesta

- [ ] Si `Resultado = A`: guardar `CAE` y `CAEFchVto` del response.
- [ ] Si `Resultado = R`: loggear `Errors` (cada `Code` + `Msg`) y propagar al usuario.
- [ ] Si `Resultado = P` (parcial en lote): procesar cada item, los posteriores al rechazo quedan "no procesados" por correlatividad.
- [ ] Ante time-out / error de comunicación: **NO reintentar ciegamente**. Consultar `FECompConsultar` con `CbteTipo`/`PtoVta`/`Nro` antes de reenviar, para evitar duplicados.
- [ ] Mapear los códigos de error a mensajes legibles para el operador.

### Mantenimiento periódico

- [ ] Refrescar cache de `FEParamGetTiposCbte`, `FEParamGetTiposDoc`, `FEParamGetTiposOpcional`, `FEParamGetCondicionIvaReceptor` (p.ej. semanalmente).
- [ ] Verificar **monto RG 4444 vigente** como parámetro configurable.
- [ ] Monitorear el aviso de obligatoriedad de `CondicionIVAReceptorId` (RG 5616) y ajustar cuando ARCA confirme.
- [ ] Alertar cuando se reciban códigos observacionales relevantes (10217, 10234-10237).

---

## Referencias

- **Manual oficial:** `manual_dev.txt` en este directorio (revisión 17-Mar-2025, Proyecto FE v4.0).
- **Fuente web:** https://www.afip.gob.ar/ws/documentacion/manuales/manual-desarrollador-ARCA-COMPG-v4-0.pdf
- **Normativa clave:** RG 4291, RG 4444, RG 4540, RG 5259 (remitos cárnicos), RG 5264 (remitos harineros), RG 5616 (CondicionIVAReceptor), Ley 27.440 (FCE), Ley 27.618 (transición Monotributo).
