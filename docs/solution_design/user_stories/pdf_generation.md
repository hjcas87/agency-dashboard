# User Story — Generación de PDF

## Descripción
Módulo reutilizable de generación de PDF que puede ser consumido por cualquier feature del sistema (presupuestos, facturas, reportes, etc.). Genera documentos profesionales con configuración visual (colores, logo, textos fijos) y permite previsualización antes de descarga.

---

## Historias de Usuario

### HU-PDF-1: Generar PDF desde un presupuesto
**Como** usuario autenticado  
**Quiero** generar un PDF profesional de un presupuesto con un clic  
**Para** compartirlo con el cliente o archivarlo

**Criterios de aceptación:**
- En la tabla de presupuestos, cada fila tiene un botón "PDF" (icono de documento)
- Al hacer clic, se abre el PDF en una nueva pestaña del navegador
- El PDF incluye:
  - Logo de la empresa en el header
  - Nombre del presupuesto y fecha de emisión
  - Datos del cliente asociado (nombre, empresa, email, teléfono)
  - Tabla de tareas con nombre, descripción y horas
  - Resumen de totales: horas, subtotal ARS, ajuste, total ARS, total USD
  - Texto de pie de página configurable
- Colores del PDF según la plantilla configurada
- El PDF se muestra inline en el navegador (Content-Disposition: inline)
- El usuario puede descargarlo desde el navegador si lo desea

### HU-PDF-2: Configurar apariencia del PDF
**Como** usuario autenticado  
**Quiero** personalizar los colores y apariencia del PDF  
**Para** que refleje la identidad visual de mi empresa

**Criterios de aceptación:**
- Existe una pantalla "Plantillas PDF" accesible desde el sidebar
- Se pueden configurar:
  - **Color de fondo** del PDF (color picker)
  - **Color de texto** del PDF (color picker)
  - **Color de acento** para headers y bordes (color picker)
  - **Logo**: subir imagen o usar el default del proyecto
  - **Texto de cabecera**: texto introductorio antes de la tabla
  - **Texto de pie de página**: texto al final del documento
- Se puede **previsualizar** el PDF en tiempo real con un presupuesto de ejemplo
- Los valores por defecto vienen preconfigurados y funcionales
- La plantilla se puede restaurar a los valores por defecto

### HU-PDF-3: Generar PDF desde una factura (futuro)
**Como** usuario autenticado  
**Quiero** generar un PDF desde una factura usando el mismo módulo de PDF  
**Para** mantener consistencia visual en todos los documentos

**Criterios de aceptación:**
- El módulo de PDF es independiente de la feature de presupuestos
- Las facturas usan el mismo generador de PDF con su propio template
- La configuración de colores y plantilla es compartida entre todos los documentos
- El botón "PDF" aparece en la tabla de facturas con el mismo comportamiento

---

## Arquitectura Técnica

### Backend — Módulo Reutilizable (`app/shared/pdf/`)

```
app/shared/pdf/
├── __init__.py
├── generator.py         # PdfGenerator — clase principal (NO depende de features)
├── template.py          # PdfTemplate model + CRUD
└── renderers/
    ├── __init__.py
    ├── base.py          # PdfRenderer — interfaz abstracta
    └── proposal.py      # ProposalPdfRenderer — render específico
```

**Clase base `PdfGenerator`:**
```python
class PdfGenerator:
    """Generador de PDF reutilizable. No depende de features específicas."""

    def __init__(self, template: PdfTemplate):
        self.template = template
        self.renderer: PdfRenderer | None = None

    def set_renderer(self, renderer: PdfRenderer) -> None:
        self.renderer = renderer

    def generate(self, data: dict) -> bytes:
        """Genera PDF usando el renderer configurado."""
        if not self.renderer:
            raise ValueError("Renderer not set")
        html = self.renderer.render(data, self.template)
        return weasyprint.HTML(string=html).write_pdf()
```

**Interfaz `PdfRenderer`:**
```python
class PdfRenderer(ABC):
    """Interfaz para renderizadores específicos de cada tipo de documento."""

    @abstractmethod
    def render(self, data: dict, template: PdfTemplate) -> str:
        """Retorna HTML string listo para convertir a PDF."""
```

**Implementación `ProposalPdfRenderer`:**
```python
class ProposalPdfRenderer(PdfRenderer):
    def render(self, data: dict, template: PdfTemplate) -> str:
        # data = { proposal, client, tasks, totals }
        # template = { logo, bg_color, text_color, accent_color, header_text, footer_text }
        # Retorna HTML con Jinja2 o f-strings
```

### Modelo de Datos

### PdfTemplate
| Campo | Tipo | Descripción |
|---|---|---|
| id | int | PK |
| logo_url | string \| null | URL o path del logo |
| header_text | text | Texto introductorio |
| footer_text | text | Texto de pie de página |
| bg_color | string | Color de fondo (hex: "#ffffff") |
| text_color | string | Color de texto (hex: "#1a1a1a") |
| accent_color | string | Color de acento (hex: "#2563eb") |
| is_default | bool | Plantilla activa por defecto |
| created_at | datetime | Auto |
| updated_at | datetime | Auto |

### Endpoints API

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/pdf/proposals/{id}` | Genera y stream PDF de presupuesto |
| GET | `/api/v1/pdf-templates` | Obtener plantilla PDF activa |
| PUT | `/api/v1/pdf-templates` | Actualizar plantilla PDF |
| POST | `/api/v1/pdf-templates/reset` | Restaurar valores por defecto |

### Frontend

```
frontend/
├── app/(private)/(custom)/pdf-templates/page.tsx    # Configuración de plantilla
├── app/api/(custom)/pdf/proposals/[id]/route.ts     # API route para stream
├── lib/shared/pdf/
│   └── types.ts                                     # Tipos compartidos
└── components/custom/features/pdf/
    ├── pdf-template-form.tsx                        # Form con color pickers
    └── pdf-preview-dialog.tsx                       # Preview en modal
```

---

## Tecnología

**WeasyPrint** — genera PDF desde HTML/CSS

```toml
# pyproject.toml
dependencies = [
    "weasyprint>=60.0",
]
```

Razones:
- HTML/CSS → fácil diseñar layouts profesionales con color pickers
- Templates reutilizables con variables (Jinja2 o f-strings)
- Soporte para logos, tablas, colores, fuentes custom
- Alternativa: `reportlab` (más control pero más código, menos flexible para templates visuales)

---

## Dependencias del Sistema

```bash
# macOS (para weasyprint)
brew install pango glib gobject-introspection
```

---

## Notas de Diseño

1. **Independencia**: El módulo `app/shared/pdf/` no importa ninguna feature específica. Las features (proposals, invoices) usan el módulo pasando datos y un renderer específico.

2. **Color pickers**: Se usa `<input type="color">` nativo del navegador o un componente shadcn si existe. Los colores se guardan como hex strings en la DB.

3. **Preview**: El preview se genera llamando al mismo endpoint de generación de PDF pero con datos de ejemplo. El PDF se muestra en un iframe o se abre en nueva pestaña.

4. **Stream vs descarga**: El endpoint retorna `Content-Type: application/pdf` con `Content-Disposition: inline` para mostrar en el navegador. El usuario descarga desde ahí.
