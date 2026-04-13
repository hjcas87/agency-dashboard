# User Story — Generación de PDF y Envío por Email

## Descripción
Como usuario de la plataforma, necesito poder generar presupuestos en formato PDF profesional y enviarlos por email a los clientes con texto personalizado, para profesionalizar el proceso comercial y facilitar la comunicación.

---

## Historias de Usuario

### HU-1: Generar PDF de un presupuesto
**Como** usuario autenticado  
**Quiero** generar un PDF profesional desde un presupuesto existente  
**Para** compartirlo con el cliente de manera profesional

**Criterios de aceptación:**
- En la tabla de presupuestos, cada fila tiene un botón adicional "Generar PDF" (icono de documento) junto a Editar/Eliminar
- Al hacer clic, se abre el PDF en una nueva pestaña del navegador
- El PDF se descarga directamente desde esa pestaña si se desea
- El PDF incluye:
  - **Header**: Logo de la empresa, título del presupuesto, fecha de emisión, número de presupuesto
  - **Datos del cliente**: Nombre, empresa, email, teléfono
  - **Resumen del presupuesto**: Valor por hora, tasa de cambio, ajuste
  - **Tabla de tareas**: Nombre, descripción, horas, precio por tarea
  - **Totales**: Total horas, subtotal, ajuste, total ARS, total USD
  - **Footer**: Texto configurable al pie de página

### HU-2: Configurar plantillas de PDF
**Como** usuario autenticado  
**Quiero** personalizar los textos fijos del PDF  
**Para** adaptar el documento a la imagen de la empresa

**Criterios de aceptación:**
- Existe una pantalla "Plantillas PDF" en el sidebar (debajo de Configuración o dentro de ella)
- Se pueden configurar:
  - **Logo**: subir imagen o usar el default
  - **Texto de cabecera**: texto introductorio que aparece antes de la tabla (ej: "Nos complace presentar la siguiente propuesta...")
  - **Texto de pie de página**: texto al final del documento (ej: "Validez de la oferta: 30 días")
  - **Colores del PDF**: color primario para headers, bordes
- Los valores por defecto vienen preconfigurados
- Se puede previsualizar el PDF con los cambios antes de guardar
- Hay una plantilla por defecto que se puede restaurar

### HU-3: Enviar presupuesto por email con PDF adjunto
**Como** usuario autenticado  
**Quiero** enviar un presupuesto por email con el PDF adjunto y texto personalizado  
**Para** comunicarme con el cliente de manera profesional

**Criterios de aceptación:**
- En la tabla de presupuestos, cada fila tiene un botón "Enviar por email" (icono de sobre)
- Se abre un modal/drawer con:
  - **Destinatario**: precargado con el email del cliente asociado (editable)
  - **Asunto**: precargado con plantilla (ej: "Presupuesto: [nombre] - [empresa]")
  - **Cuerpo del email**: textarea con plantilla editable que puede incluir variables como `{nombre_cliente}`, `{nombre_presupuesto}`, `{total}`
  - **Vista previa del PDF adjunto**: miniatura del PDF
- Al enviar, se genera el PDF automáticamente y se adjunta
- Se muestra toast de éxito o error
- Se registra el envío en un historial (opcional, para fase 2)

### HU-4: Configurar plantillas de email
**Como** usuario autenticado  
**Quiero** gestionar plantillas de email para envío de presupuestos  
**Para** mantener consistencia en las comunicaciones

**Criterios de aceptación:**
- Existe una sección "Plantillas de Email" dentro de la misma pantalla de configuración de plantillas PDF
- Se pueden crear/editar plantillas con:
  - **Nombre** de la plantilla
  - **Asunto** del email
  - **Cuerpo** del email (con variables: `{nombre_cliente}`, `{nombre_presupuesto}`, `{total_ars}`, `{total_usd}`, `{fecha}`, `{nombre_empresa}`)
  - **Indicador de plantilla predeterminada**
- Se puede previsualizar cómo quedaría el email
- La plantilla predeterminada se usa por defecto al enviar presupuestos

---

## Arquitectura Propuesta

### Backend — Módulo de PDF (`app/shared/pdf/`)

```
app/shared/pdf/
├── __init__.py
├── base.py            # Clase base PdfGenerator (interfaz común)
├── proposal_pdf.py    # ProposalPdfGenerator extiende la base
├── templates.py       # PdfTemplate model + repository (para plantillas configurables)
└── config.py          # Configuración global de PDFs
```

**Clase base `PdfGenerator`:**
```python
class PdfGenerator(ABC):
    """Interfaz base para todos los generadores de PDF."""
    
    @abstractmethod
    def generate(self, data: dict, template: PdfTemplate) -> bytes:
        """Genera el PDF y retorna bytes."""
    
    def generate_and_save(self, data: dict, template: PdfTemplate, path: str) -> str:
        """Genera, guarda en disco y retorna la ruta."""
```

**Implementación `ProposalPdfGenerator`:**
```python
class ProposalPdfGenerator(PdfGenerator):
    """Genera PDF para propuestas."""
    
    def generate(self, proposal: dict, template: PdfTemplate) -> bytes:
        # 1. Obtener template config (logo, header text, footer text, colors)
        # 2. Crear PDF con reportlab/fpdf
        # 3. Dibujar header con logo
        # 4. Dibujar texto de introducción
        # 5. Dibujar datos del cliente
        # 6. Dibujar tabla de tareas
        # 7. Dibujar totales
        # 8. Dibujar footer
        # 9. Retornar bytes
```

### Backend — Módulo de Email (`app/shared/email/`)

```
app/shared/email/
├── __init__.py
├── service.py           # EmailService (ya existe parcialmente en shared/services/email_service.py)
├── templates.py         # EmailTemplate model + repository
└── proposal_email.py    # ProposalEmailBuilder
```

### Backend — Endpoints API

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/proposals/{id}/pdf` | Genera y retorna PDF (stream) |
| GET | `/api/v1/proposals/{id}/pdf/preview` | Retorna URL temporal para preview |
| POST | `/api/v1/proposals/{id}/email` | Envía presupuesto por email con PDF adjunto |
| GET | `/api/v1/pdf-templates` | Listar plantillas PDF |
| GET | `/api/v1/pdf-templates/default` | Obtener plantilla por defecto |
| PUT | `/api/v1/pdf-templates/default` | Actualizar plantilla por defecto |
| GET | `/api/v1/email-templates` | Listar plantillas de email |
| PUT | `/api/v1/email-templates/{id}` | Actualizar plantilla de email |

### Frontend

```
frontend/
├── app/(private)/(custom)/pdf-templates/page.tsx     # Configuración de plantillas
├── app/api/(custom)/pdf/route.ts                      # API route para stream de PDF
├── components/custom/features/pdf/
│   ├── pdf-template-form.tsx                          # Form de configuración de plantilla PDF
│   └── email-template-form.tsx                        # Form de configuración de plantilla email
└── lib/custom/features/pdf/
    └── types.ts                                       # Tipos compartidos
```

**Modificación en `proposals-table.tsx`:**
- Agregar columnas de acciones: Editar | Generar PDF | Enviar Email | Eliminar
- "Generar PDF" → abre `/api/proposals/{id}/pdf` en nueva pestaña (`window.open`)
- "Enviar Email" → abre Drawer/Dialog con formulario de email

---

## Tecnología para PDF

**Propuesta: `weasyprint`**

Razones:
- Basado en HTML/CSS → fácil diseñar layouts profesionales
- Soporte para fuentes custom, logos, tablas, colores
- Permite templates HTML que se pueden configurar desde el frontend
- Buen rendimiento para documentos de tamaño presupuesto
- Alternativa más compleja: `reportlab` (más control, pero más código)
- Alternativa más simple pero limitada: `fpdf2`

```python
# pyproject.toml
dependencies = [
    "weasyprint>=60.0",
]
```

```html
<!-- Template HTML para PDF (configurable) -->
<div class="pdf-document">
  <header class="pdf-header">
    <img src="{{ logo_url }}" class="logo" />
    <h1>{{ proposal.name }}</h1>
    <p class="date">{{ date }}</p>
  </header>
  
  <section class="intro">{{ template.header_text }}</section>
  
  <section class="client-info">
    <h2>Datos del Cliente</h2>
    <p><strong>{{ client.name }}</strong></p>
    {% if client.company %}<p>{{ client.company }}</p>{% endif %}
    <p>{{ client.email }}</p>
  </section>
  
  <table class="tasks">
    <thead>
      <tr><th>Tarea</th><th>Descripción</th><th>Horas</th></tr>
    </thead>
    <tbody>
      {% for task in tasks %}
      <tr><td>{{ task.name }}</td><td>{{ task.description }}</td><td>{{ task.hours }}</td></tr>
      {% endfor %}
    </tbody>
  </table>
  
  <section class="totals">
    <p>Total Horas: {{ totals.total_hours }} hs</p>
    <p>Subtotal: {{ totals.subtotal_ars }} ARS</p>
    <p>Ajuste: {{ totals.adjustment }} ARS</p>
    <p class="total"><strong>Total: {{ totals.total_ars }} ARS ({{ totals.total_usd }} USD)</strong></p>
  </section>
  
  <footer class="pdf-footer">{{ template.footer_text }}</footer>
</div>
```

---

## Modelo de Datos — Plantillas

### PdfTemplate
| Campo | Tipo | Descripción |
|---|---|---|
| id | int | PK |
| name | string | Nombre de la plantilla (ej: "default") |
| logo_url | string \| null | URL o path del logo |
| header_text | text | Texto introductorio |
| footer_text | text | Texto de pie de página |
| primary_color | string | Color hexadecimal (ej: "#2563eb") |
| is_default | bool | Plantilla activa por defecto |
| created_at | datetime | Auto |
| updated_at | datetime | Auto |

### EmailTemplate
| Campo | Tipo | Descripción |
|---|---|---|
| id | int | PK |
| name | string | Nombre de la plantilla |
| subject | string | Asunto del email |
| body | text | Cuerpo del email (con variables) |
| is_default | bool | Plantilla activa por defecto |
| created_at | datetime | Auto |
| updated_at | datetime | Auto |

---

## Variables disponibles en plantillas de email

| Variable | Descripción |
|---|---|
| `{nombre_cliente}` | Nombre del cliente |
| `{nombre_empresa}` | Empresa del cliente (si existe) |
| `{nombre_presupuesto}` | Nombre del presupuesto |
| `{total_ars}` | Total en pesos argentinos |
| `{total_usd}` | Total en dólares |
| `{fecha}` | Fecha de emisión |
| `{validéz}` | Texto de validez (configurable en footer) |

---

## Notas de Diseño

1. **PDF como stream**: El endpoint `GET /api/v1/proposals/{id}/pdf` retorna directamente el PDF con `Content-Type: application/pdf` y `Content-Disposition: inline` (para mostrar en el navegador). El usuario puede descargarlo desde ahí.

2. **Plantillas editables**: Se guarda en DB para que sean persistentes entre sesiones. Por defecto se crea una plantilla "default" con valores razonables.

3. **Módulo reutilizable**: `PdfGenerator` como clase base abstracta permite agregar `InvoicePdfGenerator`, `ReportPdfGenerator`, etc., cada uno con su propio template HTML.

4. **Email con adjunto**: El servicio de email existente se extiende para soportar attachments. El PDF se genera en memoria (bytes) y se adjunta directamente sin guardar en disco.

5. **No se elimina infraestructura existente**: N8N, Celery, RabbitMQ se mantienen pero no se inician por defecto. Se puede controlar con variables de entorno o perfiles de docker-compose.

---

## Dependencias a agregar

```toml
# pyproject.toml
dependencies = [
    "weasyprint>=60.0",     # Generación de PDF desde HTML
]
```

```bash
# System dependency para weasyprint en macOS
brew install pango glib gobject-introspection
```
