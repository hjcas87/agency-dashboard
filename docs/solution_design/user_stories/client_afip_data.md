# User Story — Datos AFIP del Cliente (CUIT + condición IVA + búsqueda en padrón)

## Descripción
Como usuario de la plataforma, necesito poder cargar el CUIT y la condición frente al IVA de mis clientes — **siempre opcional** — y disparar una búsqueda al padrón de AFIP a partir del CUIT para que la mayoría de los datos se autocompleten. Esto permite emitir Facturas A/B en el futuro y mejora los datos comerciales del CRM, sin bloquear el flujo actual: la Factura C **no requiere** CUIT y debe seguir funcionando con clientes que solo tienen nombre y email.

## Historias de Usuario

### HU-1: Agregar campos AFIP al modelo Cliente
**Como** desarrollador
**Quiero** extender el modelo `Client` con `cuit` (str | null) y `iva_condition` (enum | null)
**Para** que la información esté disponible para facturación sin obligar a llenarla

**Criterios de aceptación:**
- Modelo `Client` extendido con:
  - `cuit: str | None` — 11 dígitos sin separadores. Si está presente debe ser numérico de longitud 11.
  - `iva_condition: IvaCondition | None` — enum reutilizado de `app.shared.afip.enums.IvaCondition` (RI / MT / EX / NA / CF / NC). Default NULL.
- Migración Alembic generada con `--autogenerate` (regla del repo).
- Schema Pydantic `ClientCreate` / `ClientUpdate` extendido. Validators:
  - CUIT acepta dashes/espacios y los normaliza (11 dígitos).
  - CUIT rechaza no numérico o longitud distinta.
- API endpoints existentes de `/clients` no rompen — los campos nuevos son opcionales en POST/PATCH.

### HU-2: Mostrar y editar campos AFIP en el formulario de cliente
**Como** usuario autenticado
**Quiero** ver y editar el CUIT y la condición IVA del cliente en el mismo formulario donde edito nombre/empresa/email/teléfono
**Para** mantener la información AFIP donde tiene contexto, sin pantallas adicionales

**Criterios de aceptación:**
- El formulario de cliente (creación y edición) tiene una sección colapsable "Datos AFIP (opcional)" que incluye:
  - Input de CUIT con máscara `XX-XXXXXXXX-X` (visual; el backend recibe sin separadores).
  - Select de condición IVA con los 6 valores del enum + opción "Sin especificar" (= NULL).
- La sección está colapsada por defecto cuando se crea un cliente nuevo (UX limpio para casos C-only).
- Cuando se edita un cliente que ya tiene CUIT cargado, la sección se expande automáticamente.
- La validación del CUIT se aplica solo si el campo no está vacío (opcional).
- En la tabla de clientes, agregar columna "CUIT" — oculta por defecto, configurable desde el menú de columnas (igual que el resto de la tabla).

### HU-3: Buscar en AFIP por CUIT y autocompletar
**Como** usuario autenticado
**Quiero** clickear un botón "Buscar en AFIP" al lado del input de CUIT y que se autocompleten razón social, condición IVA y otros datos disponibles
**Para** evitar tipear lo que AFIP ya sabe

**Criterios de aceptación:**
- El botón "Buscar en AFIP" está deshabilitado cuando el CUIT no es válido (no 11 dígitos).
- Al clickear, el frontend llama a `GET /api/v1/clients/lookup-cuit/{cuit}` (nuevo endpoint).
- El endpoint backend usa `AfipService.get_taxpayer(TaxpayerRequest(cuit=...))` y mapea el resultado a un payload simplificado:
  - `company_name` → autocompleta `Client.company` si está vacío.
  - `first_name` + `last_name` → autocompleta `Client.name` si está vacío.
  - Inferencia de `iva_condition` desde `monotributo` / `general_regime` según los impuestos activos:
    - Activo en Monotributo (impuesto 20 ó equivalente) → `MT`.
    - Activo en IVA (impuesto 30) → `RI`.
    - Activo en IVA Exento (impuesto 32 ó equivalente) → `EX`.
    - Sin información clara → no setear (deja al usuario elegir).
- En éxito, los campos del formulario se llenan **solo si están vacíos** — no se sobreescribe lo que el usuario ya tipeó.
- En fallo (CUIT no existe en AFIP, AFIP no configurado, network error): toast con mensaje friendly. El formulario sigue editable.
- El estado de loading del botón se muestra (spinner durante la consulta).
- Si AFIP no está configurado (`AfipConfigurationError`), el botón "Buscar en AFIP" se renderiza pero deshabilitado, con tooltip explicando el motivo.

### HU-4: La factura C sigue funcionando con clientes sin CUIT
**Como** usuario autenticado
**Quiero** poder cargar un cliente solo con nombre y email (sin CUIT) y facturarle Factura C
**Para** no bloquearme cuando el cliente no tiene CUIT registrado o no aplica

**Criterios de aceptación:**
- Crear cliente sin CUIT funciona igual que hoy (no es regresión).
- Al facturar (ver `invoicing.md`):
  - Si el cliente tiene CUIT y `iva_condition`, se usan en la Factura C como `DocTipo=80 / DocNro=<cuit>` y `CondicionIVAReceptorId` correspondiente. **Nota**: para Factura C es informativo — AFIP la acepta para cualquier condición.
  - Si el cliente **no** tiene CUIT, la Factura C va con `DocTipo=99 / DocNro=0` (Consumidor Final) — válido para Monotributista emisor.

## Estructura de Datos

Cambios a `Client`:
```
+ cuit            VARCHAR(11)   NULL
+ iva_condition   VARCHAR(2)    NULL  (enum: RI/MT/EX/NA/CF/NC)
```

Sin cambios al schema base de `Client` (id/name/company/email/phone/created_at/updated_at).

## API Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/v1/clients` | POST/PATCH | Acepta los nuevos campos opcionales |
| `/api/v1/clients/lookup-cuit/{cuit}` | GET | **Nuevo**. Devuelve `{cuit, company_name, first_name, last_name, iva_condition_inferred, status}` |

El nuevo endpoint vive en el feature `clients`, no en `shared/afip` (la fachada de AFIP no expone HTTP routes — regla del módulo). El feature `clients` depende de `AfipService` vía `Depends(get_afip_service)`.

## URLs

| Ruta frontend | Descripción |
|---|---|
| `/clientes/nuevo` | Formulario con sección "Datos AFIP" agregada |
| `/clientes/{id}/editar` | Idem, con expansión automática si ya hay CUIT |

## Dependencias

- **`shared/afip`** activado (`SETUP.md`) **solo para HU-3**. Si AFIP está apagado, HU-1, HU-2 y HU-4 funcionan igual; HU-3 muestra el botón deshabilitado.

## Fuera de scope

- Cache local del padrón AFIP (cada lookup va al WS).
- Sincronización masiva: importar todos los clientes existentes contra padrón.
- Validación cruzada: detectar inconsistencias entre `iva_condition` cargada y la que devuelve AFIP.
