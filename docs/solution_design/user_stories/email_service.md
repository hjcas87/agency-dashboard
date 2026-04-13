# User Story — Servicio de Email

## Descripción
Módulo reutilizable de envío de emails con plantillas configurables, variables dinámicas y soporte de adjuntos (PDFs). Accesible desde cualquier feature del sistema (clientes, presupuestos, facturas) tanto para envío directo como para respuestas manuales. Incluye pantalla independiente en el sidebar para componer emails.

---

## Historias de Usuario

### HU-MAIL-1: Enviar presupuesto por email desde la tabla de presupuestos
**Como** usuario autenticado  
**Quiero** enviar un presupuesto por email con PDF adjunto desde la lista  
**Para** compartirlo profesionalmente con el cliente

**Criterios de aceptación:**
- En la tabla de presupuestos, cada fila tiene un botón "Enviar Email" (icono de sobre)
- Al hacer clic se abre un **Drawer/Dialog** con:
  - **Destinatario**: precargado con email del cliente asociado (editable)
  - **Asunto**: precargado con plantilla (ej: "Presupuesto: [nombre]")
  - **Cuerpo del email**: textarea con plantilla editable y variables disponibles
  - **PDF adjunto**: checkbox marcado por defecto ("Adjuntar PDF del presupuesto")
  - **Vista previa del email**: botón para previsualizar cómo llegará
- Variables disponibles en el cuerpo: `{nombre_cliente}`, `{nombre_empresa}`, `{nombre_presupuesto}`, `{total_ars}`, `{total_usd}`, `{fecha}`
- Al enviar, se genera el PDF automáticamente y se adjunta al email
- Se muestra toast de éxito o error
- El email se envía usando la configuración SMTP del sistema

### HU-MAIL-2: Enviar email personalizado desde un cliente
**Como** usuario autenticado  
**Quiero** enviar un email a un cliente desde su ficha  
**Para** mantener comunicación profesional con registros

**Criterios de aceptación:**
- En la tabla de clientes (o vista de detalle), cada fila tiene un botón "Enviar Email"
- Se abre el mismo Drawer/Dialog de composición de emails
- El destinatario se precarga con el email del cliente
- Se puede **adjuntar un PDF de presupuesto** existente:
  - Dropdown "Adjuntar PDF" con lista de presupuestos del cliente
  - Opción "Seleccionar archivo" para subir un PDF externo
- El cuerpo del email usa la plantilla predeterminada pero es editable
- Se puede enviar sin adjuntos (solo texto)
- Se muestra toast de éxito o error

### HU-MAIL-3: Composición libre de emails (pantalla independiente)
**Como** usuario autenticado  
**Quiero** acceder a una pantalla de composición de emails desde el sidebar  
**Para** redactar emails personalizados a cualquier destinatario

**Criterios de aceptación:**
- Existe un ítem "Enviar Email" en el sidebar (debajo de Facturación)
- La pantalla tiene:
  - **Para**: campo de email (requerido)
  - **CC**: campo opcional
  - **Asunto**: campo de texto
  - **Plantilla**: selector de plantillas guardadas
  - **Cuerpo**: editor de texto enriquecido o textarea grande
  - **Adjuntar PDF**: selector para elegir un presupuesto y adjuntar su PDF
  - **Adjuntar archivo**: botón para subir archivos externos
  - **Enviar** y **Guardar borrador**
- Se puede previsualizar el email antes de enviar
- Las plantillas se pueden crear/editar desde esta misma pantalla

### HU-MAIL-4: Gestionar plantillas de email
**Como** usuario autenticado  
**Quiero** crear y editar plantillas de email reutilizables  
**Para** mantener consistencia en mis comunicaciones

**Criterios de aceptación:**
- Dentro de la pantalla de "Enviar Email" hay una sección "Plantillas"
- Se pueden crear nuevas plantillas con:
  - **Nombre** de la plantilla
  - **Asunto** predeterminado
  - **Cuerpo** del email con soporte de variables
  - **Marcar como predeterminada**
- Las variables disponibles se muestran como badges clickeables que se insertan en el texto
- Se puede previsualizar la plantilla con datos de ejemplo
- Las plantillas se listan con opción de editar, duplicar o eliminar
- La plantilla predeterminada se carga automáticamente al abrir el composer

### HU-MAIL-5: Enviar factura por email (futuro)
**Como** usuario autenticado  
**Quiero** enviar una factura por email con PDF adjunto  
**Para** mantener el mismo flujo profesional en todos los documentos

**Criterios de aceptación:**
- El módulo de email es independiente de la feature de presupuestos
- Las facturas usan el mismo composer de email
- Se puede adjuntar el PDF generado de la factura
- Las plantillas de email son compartidas entre features

---

## Arquitectura Técnica

### Backend — Módulo Reutilizable (`app/shared/email/`)

```
app/shared/email/
├── __init__.py
├── service.py           # EmailService — clase principal (NO depende de features)
├── template.py          # EmailTemplate model + CRUD
└── builders/
    ├── __init__.py
    ├── base.py          # EmailBuilder — interfaz abstracta
    └── proposal.py      # ProposalEmailBuilder — builder específico
```

**Clase base `EmailService`:**
```python
class EmailService:
    """Servicio de email reutilizable. No depende de features específicas."""

    def __init__(self, smtp_config: dict):
        self.smtp_config = smtp_config

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: list[Attachment] | None = None,
        cc: str | None = None,
    ) -> bool:
        """Envía un email con adjuntos opcionales."""
        # Renderiza variables en el body
        # Construye mensaje con attachments
        # Envía via SMTP
```

**Clase `Attachment`:**
```python
@dataclass
class Attachment:
    filename: str
    content: bytes        # Contenido del archivo
    mime_type: str        # "application/pdf", etc.
```

**Interfaz `EmailBuilder`:**
```python
class EmailBuilder(ABC):
    """Interfaz para builders específicos de cada contexto."""

    @abstractmethod
    def build_email(self, data: dict, template: EmailTemplate) -> EmailMessage:
        """Construye un EmailMessage completo."""
```

### Modelo de Datos

### EmailTemplate
| Campo | Tipo | Descripción |
|---|---|---|
| id | int | PK |
| name | string | Nombre de la plantilla |
| subject | string | Asunto predeterminado |
| body | text | Cuerpo del email (con variables) |
| is_default | bool | Plantilla activa por defecto |
| created_at | datetime | Auto |
| updated_at | datetime | Auto |

### Variables disponibles en plantillas

| Variable | Descripción |
|---|---|
| `{nombre_cliente}` | Nombre del cliente |
| `{nombre_empresa}` | Empresa del cliente |
| `{nombre_presupuesto}` | Nombre del presupuesto |
| `{total_ars}` | Total en pesos argentinos |
| `{total_usd}` | Total en dólares |
| `{fecha}` | Fecha de emisión |
| `{nombre_remitente}` | Nombre del usuario que envía |
| `{nombre_empresa_emisora}` | Nombre de tu empresa |

### Endpoints API

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/v1/email/send` | Enviar email (genérico) |
| POST | `/api/v1/email/proposals/{id}/send` | Enviar presupuesto por email (con PDF) |
| GET | `/api/v1/email-templates` | Listar plantillas |
| GET | `/api/v1/email-templates/{id}` | Obtener plantilla |
| POST | `/api/v1/email-templates` | Crear plantilla |
| PUT | `/api/v1/email-templates/{id}` | Actualizar plantilla |
| DELETE | `/api/v1/email-templates/{id}` | Eliminar plantilla |
| POST | `/api/v1/email-templates/{id}/preview` | Previsualizar email con datos de ejemplo |

### Frontend

```
frontend/
├── app/(private)/(custom)/email/page.tsx           # Pantalla de composición
├── app/actions/custom/email.ts                      # Server actions para email
├── lib/shared/email/
│   └── types.ts                                     # Tipos compartidos
└── components/custom/features/email/
    ├── email-composer.tsx                           # Composer principal (reutilizable)
    ├── email-template-form.tsx                      # Form de plantilla
    ├── email-template-selector.tsx                  # Dropdown de plantillas
    ├── email-send-dialog.tsx                        # Dialog rápido desde tablas
    └── variable-badge.tsx                           # Badges de variables insertables
```

**Uso desde la tabla de presupuestos:**
```tsx
// proposals-table.tsx — columna de acciones
<DropdownMenuItem onClick={() => onSendEmail(proposal)}>
  <IconMail className="size-4" />
  Enviar Email
</DropdownMenuItem>

// Al hacer clic → abre EmailSendDialog
<EmailSendDialog
  open={isDialogOpen}
  onOpenChange={setIsDialogOpen}
  recipient={proposal.client_email}
  subject={`Presupuesto: ${proposal.name}`}
  attachmentType="proposal"
  attachmentId={proposal.id}
/>
```

**Uso desde la tabla de clientes:**
```tsx
// clients-table.tsx — columna de acciones
<DropdownMenuItem onClick={() => onSendEmail(client)}>
  <IconMail className="size-4" />
  Enviar Email
</DropdownMenuItem>

// Al hacer clic → abre EmailSendDialog con selector de PDFs
<EmailSendDialog
  open={isDialogOpen}
  onOpenChange={setIsDialogOpen}
  recipient={client.email}
  attachmentType="select"          // Permite elegir entre proposals del cliente
  availableProposals={clientProposals}
/>
```

---

## Tecnología

**Email:** `aiosmtplib` (async SMTP) o `python-email` (built-in `smtplib` + `email`)

```toml
# pyproject.toml
dependencies = [
    "aiosmtplib>=3.0",    # SMTP async para FastAPI
]
```

---

## Configuración SMTP

Se usa la configuración existente en `backend/.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu@email.com
SMTP_PASSWORD=tu-password
SMTP_FROM_EMAIL=tu@email.com
SMTP_USE_TLS=true
```

Si no está configurado, el servicio registra el email en logs pero no envía (modo desarrollo).

---

## Reglas de Frontend (NO NEGOCIABLE)

### Usar siempre shadcn/ui — nunca crear componentes propios desde cero

Este proyecto usa **shadcn/ui** como sistema de componentes. **No se escriben componentes UI desde cero**. Se busca, instala y compone desde shadcn.

```bash
# Buscar componente disponible
npx shadcn@latest search dialog
npx shadcn@latest search textarea

# Instalar componente
npx shadcn@latest add dialog drawer
```

Si no existe en shadcn, se busca un **bloque de shadcn** (https://ui.shadcn.com/blocks) o una alternativa compatible.

### Reglas de estilo (docs/references/shadcn/rules/)

1. **Colores semánticos** — `bg-background`, `text-foreground`, `text-muted-foreground`, `bg-primary`, `bg-destructive`. **Nunca** colores raw como `bg-blue-500`, `text-emerald-600`, `bg-gray-900`.
2. **className solo para layout** — márgenes, anchos, positioning. **Nunca** para override de colores o tipografía del componente.
3. **gap, no space** — `flex flex-col gap-4`, **nunca** `space-y-4`.
4. **size-*, no w-* h-*** — `size-10` en vez de `w-10 h-10`.
5. **cn() para clases condicionales** — importar de `@/lib/utils`.
6. **No z-index manual** — Dialog, Sheet, Drawer, DropdownMenu manejan su propio stacking.

### Reglas de composición (docs/references/shadcn/rules/composition.md)

1. **Items dentro de su Group** — `SelectItem` dentro de `SelectGroup`, `DropdownMenuItem` dentro de `DropdownMenuGroup`.
2. **Dialog/Sheet/Drawer siempre necesitan Title** — `DialogTitle`, `DrawerTitle` con `className="sr-only"` si no debe ser visible.
3. **Card estructura completa** — `CardHeader` + `CardTitle` + `CardDescription` + `CardContent` + `CardFooter`.
4. **Empty states usan `<Empty>`** — no markup custom.
5. **Callouts usan `<Alert>`** — no divs con colores de alerta.
6. **Toast usa `sonner`** — `toast.success()`, `toast.error()`.
7. **Separadores usan `<Separator>`** — no `<hr>` ni divs con borde.
8. **Loading usa `<Skeleton>`** — no divs con animate-pulse.

### Reglas de formularios (docs/references/shadcn/rules/forms.md)

1. **FieldGroup + Field** — nunca divs con `space-y-*`.
2. **InputGroupInput dentro de InputGroup** — nunca `Input` raw dentro de `InputGroup`.
3. **Textarea dentro de InputGroupTextarea** si está en un InputGroup.
4. **Botón disabled + Spinner** para loading — no existe `isPending`.
5. **ToggleGroup para 2-7 opciones** — no buttons manuales con estado activo.

### Reglas de íconos (docs/references/shadcn/rules/icons.md)

1. **Usar `@tabler/icons-react`** — icon library configurada del proyecto.
2. **data-icon en buttons** — `data-icon="inline-start"` o `data-icon="inline-end"`.
3. **Sin clases de tamaño en íconos** dentro de componentes shadcn — el componente maneja el tamaño.
4. **Iconos como objetos** — `icon={CheckIcon}`, no strings.

### Para esta feature en particular

- **EmailSendDialog**: usar `Dialog` con `DialogTitle`, `DialogDescription`, `DialogHeader`, `DialogContent`, `DialogFooter`.
- **Textarea del cuerpo**: usar `Textarea` de shadcn dentro de `FieldGroup` + `Field`.
- **Selector de plantillas**: usar `Select` con `SelectGroup`.
- **Badges de variables**: usar `Badge` con `variant="secondary"`.
- **Vista previa del email**: usar `Drawer` o `Sheet` con composición completa.
- **Ningún componente nuevo** se crea en `components/core/ui/` sin pasar por `npx shadcn@latest add`.

---

## Notas de Diseño

1. **Independencia total**: `app/shared/email/` no importa ninguna feature específica. Las features usan el servicio pasando datos y un builder específico.

2. **EmailSendDialog reutilizable**: Un solo componente de diálogo que se adapta según el contexto:
   - Desde proposals → precarga destinatario y adjunta PDF automáticamente
   - Desde clients → muestra selector de proposals del cliente para adjuntar
   - Desde la pantalla de email → modo libre sin adjuntos

3. **Pantalla de email**: Es un composer completo accesible desde el sidebar. Sirve para:
   - Enviar emails manuales a cualquier contacto
   - Adjuntar PDFs de cualquier feature
   - Gestionar plantillas
   - Ver historial de envíos (fase 2)

4. **Variables**: Se renderizan en el backend al momento de enviar. En el frontend se muestran como badges clickeables que insertan el texto de la variable en el textarea.

5. **Attachments**: El PDF se genera en memoria (bytes) y se pasa como `Attachment` al `EmailService`. No se guarda en disco.
