# Guía de Determinación de Condición IVA desde Constancia de Inscripción AFIP

## Índice
1. [Estructura de Datos del Servicio](#estructura-de-datos-del-servicio)
2. [Identificación de Impuestos Clave](#identificación-de-impuestos-clave)
3. [Lógica de Determinación de Condición IVA](#lógica-de-determinación-de-condición-iva)
4. [Casos Especiales y Conflictos](#casos-especiales-y-conflictos)
5. [Implementación Recomendada](#implementación-recomendada)
6. [Mapeo a Condiciones IVA del Sistema](#mapeo-a-condiciones-iva-del-sistema)

---

## Estructura de Datos del Servicio

El servicio `ws_sr_constancia_inscripcion` devuelve tres bloques principales de datos:

### 1. datosGenerales
Información básica del contribuyente (nombre, domicilio, estado, etc.)

### 2. datosRegimenGeneral
Impuestos y actividades del régimen general:
```json
{
  "datosRegimenGeneral": {
    "impuesto": [
      {
        "idImpuesto": "30",
        "descripcionImpuesto": "IVA",
        "estadoImpuesto": "AC",
        "motivo": "INSCRIPCIÓN TRAMITADA EN AGENCIA",
        "periodo": "202405"
      },
      {
        "idImpuesto": "32",
        "descripcionImpuesto": "IVA EXENTO",
        "estadoImpuesto": "EX",
        "motivo": "INSCRIPCIÓN NO TRAMITADA EN AGENCIA",
        "periodo": "202405"
      }
    ],
    "actividad": [...]
  }
}
```

### 3. datosMonotributo
Información del régimen de monotributo:
```json
{
  "datosMonotributo": {
    "impuesto": [
      {
        "idImpuesto": "20",
        "descripcionImpuesto": "MONOTRIBUTO",
        "estadoImpuesto": "AC",
        "motivo": "Recategorización",
        "periodo": "202503"
      }
    ],
    "actividadMonotributista": {...},
    "categoriaMonotributo": {...}
  }
}
```

---

## Identificación de Impuestos Clave

### IDs de Impuestos Relevantes

| ID | Descripción | Condición IVA |
|----|-------------|---------------|
| 20 | MONOTRIBUTO | Monotributista (MT) |
| 30 | IVA | Responsable Inscripto (RI) |
| 32 | IVA EXENTO | IVA Exento (EX) |
| 11 | GANANCIAS PERSONAS FISICAS | - |

### Estados de Impuesto (estadoImpuesto)

| Código | Significado | Acción |
|--------|-------------|--------|
| AC | Activo | ✅ Considerar para condición IVA |
| EX | Exento | ❌ No considerar (histórico/inactivo) |
| BA | Baja | ❌ No considerar |
| OT | Otros | ⚠️ Verificar caso a caso |

---

## Lógica de Determinación de Condición IVA

### Regla Principal

La condición IVA se determina **PRIORITARIAMENTE** por el impuesto ACTIVO en el siguiente orden:

```python
# Pseudocódigo de lógica de determinación
def determinar_condicion_iva(datos):
    """
    Determina la condición IVA basándose en la constancia de inscripción
    """
    
    # 1. Verificar MONOTRIBUTO activo (ID 20)
    if tiene_impuesto_activo(datos, id_impuesto=20):
        return "MT"  # Monotributista
    
    # 2. Verificar IVA activo (ID 30)
    if tiene_impuesto_activo(datos, id_impuesto=30):
        return "RI"  # Responsable Inscripto
    
    # 3. Verificar IVA EXENTO activo (ID 32)
    if tiene_impuesto_activo(datos, id_impuesto=32):
        return "EX"  # IVA Exento
    
    # 4. Si no tiene impuestos activos pero tiene datos en monotributo
    if tiene_datos_monotributo(datos) and not tiene_datos_regimen_general(datos):
        return "MT"  # Monotributista sin impuesto activo aún
    
    # 5. Si solo tiene datos en régimen general sin impuestos específicos
    if tiene_datos_regimen_general(datos):
        return "CF"  # Consumidor Final (por defecto)
    
    # 6. Fallback
    return "NC"  # No Categorizado

def tiene_impuesto_activo(datos, id_impuesto):
    """Verifica si existe un impuesto con estado 'AC' (Activo)"""
    # Buscar en datosRegimenGeneral
    for imp in datos.get("datosRegimenGeneral", {}).get("impuesto", []):
        if imp["idImpuesto"] == str(id_impuesto) and imp["estadoImpuesto"] == "AC":
            return True
    
    # Buscar en datosMonotributo
    for imp in datos.get("datosMonotributo", {}).get("impuesto", []):
        if imp["idImpuesto"] == str(id_impuesto) and imp["estadoImpuesto"] == "AC":
            return True
    
    return False
```

### ⚠️ IMPORTANTE: Prioridad del Monotributo

**Si un contribuyente tiene MONOTRIBUTO activo (ID 20, estado AC), su condición IVA es MT (Monotributista), independientemente de otros datos en régimen general.**

```python
# Ejemplo de prioridad
ejemplo_contribuyente = {
    "datosRegimenGeneral": {
        "impuesto": [
            {"idImpuesto": "32", "descripcionImpuesto": "IVA EXENTO", "estadoImpuesto": "EX"}
        ]
    },
    "datosMonotributo": {
        "impuesto": [
            {"idImpuesto": "20", "descripcionImpuesto": "MONOTRIBUTO", "estadoImpuesto": "AC"}
        ]
    }
}
# Resultado: MT (Monotributista) - El monotributo activo tiene prioridad
```

---

## Casos Especiales y Conflictos

### Caso 1: Ambos Regímenes con Datos

```json
{
  "datosRegimenGeneral": {
    "impuesto": [
      {"idImpuesto": "30", "estadoImpuesto": "AC", "descripcionImpuesto": "IVA"}
    ]
  },
  "datosMonotributo": {
    "impuesto": [
      {"idImpuesto": "20", "estadoImpuesto": "AC", "descripcionImpuesto": "MONOTRIBUTO"}
    ]
  }
}
```
**Resultado**: MT (Monotributista) - El monotributo activo tiene prioridad sobre IVA.

### Caso 2: IVA Exento vs Monotributo Inactivo

```json
{
  "datosRegimenGeneral": {
    "impuesto": [
      {"idImpuesto": "32", "estadoImpuesto": "EX", "descripcionImpuesto": "IVA EXENTO"}
    ]
  },
  "datosMonotributo": {
    "impuesto": [
      {"idImpuesto": "20", "estadoImpuesto": "AC", "descripcionImpuesto": "MONOTRIBUTO"}
    ]
  }
}
```
**Resultado**: MT (Monotributista) - Aunque tenga IVA Exento registrado, el monotributo está ACTIVO.

### Caso 3: Solo Régimen General con IVA Activo

```json
{
  "datosRegimenGeneral": {
    "impuesto": [
      {"idImpuesto": "30", "estadoImpuesto": "AC", "descripcionImpuesto": "IVA"}
    ]
  },
  "datosMonotributo": null
}
```
**Resultado**: RI (Responsable Inscripto)

### Caso 4: Solo Monotributo sin Impuestos Activos

```json
{
  "datosRegimenGeneral": null,
  "datosMonotributo": {
    "impuesto": [],
    "actividadMonotributista": {...},
    "categoriaMonotributo": null
  }
}
```
**Resultado**: MT (Monotributista) - Si tiene datos de monotributo, asumimos MT

### Caso 5: Contribuyente sin Impuestos Específicos

```json
{
  "datosRegimenGeneral": {
    "impuesto": [
      {"idImpuesto": "11", "estadoImpuesto": "AC", "descripcionImpuesto": "GANANCIAS PERSONAS FISICAS"}
    ]
  },
  "datosMonotributo": null
}
```
**Resultado**: CF (Consumidor Final) o NC (No Categorizado) - No tiene IVA ni Monotributo

---

## Implementación Recomendada

### Función Python Completa

```python
from typing import Dict, Optional
from enum import Enum

class IvaCondition(str, Enum):
    RI = "RI"  # Responsable Inscripto
    MT = "MT"  # Monotributista
    EX = "EX"  # IVA Exento
    NA = "NA"  # No Alcanzado
    CF = "CF"  # Consumidor Final
    NC = "NC"  # No Categorizado

class ImpuestosID:
    MONOTRIBUTO = "20"
    IVA = "30"
    IVA_EXENTO = "32"
    GANANCIAS_PF = "11"

class EstadoImpuesto:
    ACTIVO = "AC"
    EXENTO = "EX"
    BAJA = "BA"

def determinar_condicion_iva_from_padron(padron_data: Dict) -> IvaCondition:
    """
    Determina la condición IVA basándose en los datos del padrón de AFIP.
    
    Args:
        padron_data: Diccionario con la respuesta del servicio getPersona_v2
        
    Returns:
        IvaCondition: Condición IVA del contribuyente
    """
    
    # Extraer bloques de datos
    datos_regimen_general = padron_data.get("datosRegimenGeneral", {})
    datos_monotributo = padron_data.get("datosMonotributo", {})
    
    # Obtener listas de impuestos
    impuestos_rg = datos_regimen_general.get("impuesto", [])
    impuestos_mt = datos_monotributo.get("impuesto", [])
    
    # Normalizar a lista si es un solo elemento (no array)
    if isinstance(impuestos_rg, dict):
        impuestos_rg = [impuestos_rg]
    if isinstance(impuestos_mt, dict):
        impuestos_mt = [impuestos_mt]
    
    # 1. Verificar MONOTRIBUTO activo (ID 20) - PRIORIDAD MÁXIMA
    for imp in impuestos_mt:
        if (imp.get("idImpuesto") == ImpuestosID.MONOTRIBUTO and 
            imp.get("estadoImpuesto") == EstadoImpuesto.ACTIVO):
            return IvaCondition.MT
    
    # 2. Verificar IVA activo (ID 30)
    for imp in impuestos_rg:
        if (imp.get("idImpuesto") == ImpuestosID.IVA and 
            imp.get("estadoImpuesto") == EstadoImpuesto.ACTIVO):
            return IvaCondition.RI
    
    # 3. Verificar IVA EXENTO activo (ID 32)
    for imp in impuestos_rg:
        if (imp.get("idImpuesto") == ImpuestosID.IVA_EXENTO and 
            imp.get("estadoImpuesto") == EstadoImpuesto.ACTIVO):
            return IvaCondition.EX
    
    # 4. Si no tiene impuestos activos pero tiene datos en monotributo
    if datos_monotributo and not datos_regimen_general:
        return IvaCondition.MT
    
    # 5. Si solo tiene datos en régimen general sin impuestos IVA específicos
    if datos_regimen_general:
        return IvaCondition.CF
    
    # 6. Fallback
    return IvaCondition.NC


def validar_consistencia_iva(cliente_iva: str, padron_data: Dict) -> tuple:
    """
    Valida si la condición IVA del cliente coincide con el padrón de AFIP.
    
    Returns:
        tuple: (es_valido: bool, iva_correcto: str, mensaje: str)
    """
    iva_padron = determinar_condicion_iva_from_padron(padron_data).value
    
    if cliente_iva == iva_padron:
        return True, iva_padron, "Condición IVA correcta"
    
    # Caso especial: Cliente como MT pero padrón como EX
    if cliente_iva == "MT" and iva_padron == "EX":
        return False, iva_padron, (
            f"El contribuyente está registrado como IVA EXENTO en AFIP, "
            f"pero su condición actual es MONOTRIBUTISTA. "
            f"Por favor, actualice la condición IVA del cliente a EX."
        )
    
    # Caso especial: Cliente como EX pero padrón como MT
    if cliente_iva == "EX" and iva_padron == "MT":
        return False, iva_padron, (
            f"El contribuyente está registrado como MONOTRIBUTISTA en AFIP, "
            f"pero su condición actual es IVA EXENTO. "
            f"Por favor, actualice la condición IVA del cliente a MT."
        )
    
    return False, iva_padron, (
        f"La condición IVA del cliente ({cliente_iva}) no coincide con "
        f"el padrón de AFIP ({iva_padron}). "
        f"Por favor, actualice la información del cliente."
    )
```

---

## Mapeo a Condiciones IVA del Sistema

### Mapeo Final

| Padrón AFIP | Condición IVA Sistema | Tipo Factura A | Tipo Factura B | Tipo Factura C |
|-------------|----------------------|----------------|----------------|----------------|
| Monotributo Activo (ID 20, AC) | MT | ❌ | ✅ | ❌ |
| IVA Activo (ID 30, AC) | RI | ✅ | ✅ | ❌ |
| IVA Exento (ID 32, AC) | EX | ✅ | ✅ | ❌ |
| Sin IVA ni Monotributo | CF | ❌ | ✅ | ✅ |
| Otros casos | NC | ❌ | ✅ | ❌ |

### Tipos de Factura según Condición IVA

```python
# Mapeo automático de condición IVA a tipo de factura
IVA_TO_RECEIPT_TYPE = {
    "RI": ReceiptType.INVOICE_A,      # Responsable Inscripto → Factura A
    "MT": ReceiptType.INVOICE_B,      # Monotributista → Factura B
    "EX": ReceiptType.INVOICE_B,      # Exento → Factura B
    "NA": ReceiptType.INVOICE_B,      # No Alcanzado → Factura B
    "CF": ReceiptType.INVOICE_C,      # Consumidor Final → Factura C
    "NC": ReceiptType.INVOICE_B,      # No Categorizado → Factura B
}

# Para MiPyMEs (FCE)
IVA_TO_RECEIPT_TYPE_FCE = {
    "RI": ReceiptType.FCE_INVOICE_A,
    "MT": ReceiptType.FCE_INVOICE_B,
    "EX": ReceiptType.FCE_INVOICE_B,
    "NA": ReceiptType.FCE_INVOICE_B,
    "CF": ReceiptType.FCE_INVOICE_C,
    "NC": ReceiptType.FCE_INVOICE_B,
}
```

---

## Resumen de Reglas de Negocio

### 1. Prioridad de Régimen
1. **Monotributo Activo** → Siempre MT (Monotributista)
2. **IVA Activo** → RI (Responsable Inscripto)
3. **IVA Exento Activo** → EX (IVA Exento)
4. **Datos de Monotributo sin impuestos** → MT (Monotributista)
5. **Régimen General sin IVA específico** → CF (Consumidor Final)

### 2. Validaciones Pre-Facturación

Antes de emitir cualquier factura, validar:

1. **Condición IVA del cliente** vs **Padrón de AFIP**
2. **Compatibilidad tipo de comprobante** vs **Condición IVA**
3. **Documento (DocTipo/DocNro)** según **monto y tipo de comprobante**

### 3. Caso del Contribuyente 27828940541

**Datos del Padrón:**
```json
{
  "datosRegimenGeneral": {
    "impuesto": [
      {"idImpuesto": "32", "descripcionImpuesto": "IVA EXENTO", "estadoImpuesto": "EX"}
    ]
  },
  "datosMonotributo": {
    "impuesto": [
      {"idImpuesto": "20", "descripcionImpuesto": "MONOTRIBUTO", "estadoImpuesto": "AC"}
    ]
  }
}
```

**Análisis:**
- IVA EXENTO (ID 32) está con estado "EX" (Exento/No activo)
- MONOTRIBUTO (ID 20) está con estado "AC" (Activo)

**Condición IVA Correcta**: MT (Monotributista)

**Problema**: El sistema lo tenía como MT, pero AFIP rechazaba porque estaba consultando condición EX en Factura B.

**Solución**: Verificar que el servicio de consulta de contribuyentes esté usando el mismo CUIT que se usa para facturar, y que la condición IVA enviada en el XML de facturación coincida con la determinada por el algoritmo anterior.

---

## Notas Finales

### Diferencia entre IVA EXENTO (ID 32) estado EX vs AC

- **ID 32, estado "EX"**: El contribuyente no es exento actualmente (el estado "EX" significa que no está activo en ese impuesto)
- **ID 32, estado "AC"**: El contribuyente es efectivamente IVA Exento

**IMPORTANTE**: No confundir `descripcionImpuesto` con `estadoImpuesto`. Un impuesto "IVA EXENTO" con estado "EX" no significa que el contribuyente sea exento, sino que ese registro está inactivo.

### Recomendación de Actualización

Implementar un job periódico (diario/semanal) que:
1. Consulte el padrón de AFIP para todos los clientes activos
2. Compare la condición IVA registrada vs la del padrón
3. Genere alertas cuando haya discrepancias
4. Permita actualización masiva de condiciones IVA

---

*Documento generado a partir del Manual del Servicio de Constancia de Inscripción - ws_sr_constancia_inscripcion v3.8*
