# Mejores Prácticas: Documentación de Negocio para IA

## ¿Es Buena Práctica Incluir Documentación Visual?

**✅ SÍ, es una excelente práctica** cuando se hace correctamente.

### Ventajas

1. **Contexto Completo**: Los agentes de IA entienden mejor el propósito
2. **Consistencia**: Asegura que la implementación sigue los diseños
3. **Trazabilidad**: Conecta código con requisitos de negocio
4. **Onboarding**: Facilita que nuevos desarrolladores entiendan el proyecto
5. **Validación**: Permite verificar que el código cumple con especificaciones

### Consideraciones

1. **Tamaño**: Archivos grandes pueden ralentizar el contexto
2. **Formato**: Algunos formatos son mejor que otros
3. **Organización**: Debe estar bien estructurada
4. **Actualización**: Debe mantenerse sincronizada con el código

## Formatos Recomendados

### ✅ Mejores Formatos

1. **Markdown (.md)**
   - ✅ Excelente para texto
   - ✅ Fácil de leer por IA
   - ✅ Versionable en Git
   - ✅ Ligero

2. **Imágenes PNG/JPG**
   - ✅ Diagramas y mockups
   - ✅ IA puede "ver" el contenido
   - ⚠️ No indexable (usar nombres descriptivos)

3. **SVG**
   - ✅ Diagramas vectoriales
   - ✅ Texto indexable
   - ✅ Ligero

4. **PDFs**
   - ✅ Documentos completos
   - ⚠️ Puede ser pesado
   - ⚠️ Mejor extraer texto a Markdown

### ⚠️ Formatos con Limitaciones

1. **Figma Files (.figma)**
   - ⚠️ No directamente legible
   - ✅ Usar exports en PNG/PDF
   - ✅ O links con descripción

2. **Archivos Binarios Grandes**
   - ⚠️ Pueden ralentizar el contexto
   - ✅ Usar `.cursorignore` para excluir si es necesario
   - ✅ Preferir versiones comprimidas

## Estructura Recomendada

```
docs/business/
├── requirements/          # Texto (Markdown)
│   ├── feature-name.md
│   └── user-stories.md
├── diagrams/             # Imágenes (PNG, SVG)
│   ├── architecture/
│   ├── flowcharts/
│   └── sequence/
├── designs/             # Diseños (PNG, PDF, links)
│   ├── figma/           # Links o exports
│   ├── mockups/         # Imágenes
│   └── wireframes/      # Imágenes
├── specs/               # Texto (Markdown)
│   ├── api-specs/
│   └── business-rules/
└── assets/              # Recursos pesados
    ├── pdfs/           # PDFs completos
    └── exports/        # Exports de Figma
```

## Estrategias para Diferentes Tipos de Documentación

### Diagramas

**Mejor Práctica:**
1. Exportar como PNG/SVG
2. Nombre descriptivo: `checkout-flow-diagram.png`
3. Crear archivo `.md` que describe el diagrama
4. Referenciar en código

**Ejemplo:**
```markdown
# Checkout Flow Diagram

Ver: `diagrams/flowcharts/checkout-flow.png`

## Descripción
Este diagrama muestra el flujo completo del proceso de checkout:
1. Usuario agrega items al carrito
2. Valida stock
3. Calcula total
4. Procesa pago
5. Confirma orden
```

### Diseños Figma

**Mejor Práctica:**
1. Exportar componentes clave como PNG
2. Crear archivo `.md` con link a Figma
3. Describir componentes y estilos
4. Incluir especificaciones de diseño

**Ejemplo:**
```markdown
# Checkout Page Design

**Figma Link**: [Ver diseño completo](https://figma.com/file/...)

## Componentes Principales
- Header con logo
- Cart summary (derecha)
- Checkout form (izquierda)
- Payment section

## Colores
- Primary: #3B82F6
- Background: #F9FAFB
- Text: #111827

## Espaciado
- Padding: 24px
- Gap entre elementos: 16px
```

### PDFs

**Mejor Práctica:**
1. Extraer contenido importante a Markdown
2. Guardar PDF en `assets/pdfs/`
3. Referenciar desde Markdown
4. Incluir resumen de contenido

**Ejemplo:**
```markdown
# Functional Specification: Checkout

**PDF Completo**: `assets/pdfs/checkout-spec-v1.2.pdf`

## Resumen
Este documento especifica los requisitos funcionales del proceso de checkout.

### Puntos Clave
- Validación de stock en tiempo real
- Múltiples métodos de pago
- Confirmación por email
```

### Imágenes

**Mejor Práctica:**
1. Nombres descriptivos: `user-dashboard-mockup-v2.png`
2. Incluir descripción en archivo `.md` adjunto
3. Comprimir si son muy grandes
4. Usar formato optimizado (WebP si es posible)

## Cómo Referenciar en Código

### En Comentarios

```python
# Implementación según:
# - Requisitos: docs/business/requirements/checkout.md
# - Flujo: docs/business/diagrams/flowcharts/checkout-flow.png
# - Diseño: docs/business/designs/figma/checkout-design.md
def process_checkout(order_data: OrderCreate) -> Order:
    # ...
```

### En Docstrings

```python
def render_checkout_page():
    """
    Renderiza la página de checkout.
    
    Implementación basada en:
    - Diseño: docs/business/designs/figma/checkout-design.md
    - Componentes: shadcn/ui Card, Button, Input
    - Estilos: Tailwind CSS según especificaciones
    """
    # ...
```

## Optimización para IA

### 1. Texto Descriptivo

Siempre incluir descripción en texto de lo que muestra una imagen:

```markdown
# Checkout Flow

![Checkout Flow Diagram](diagrams/flowcharts/checkout-flow.png)

Este diagrama muestra:
1. Usuario inicia checkout
2. Sistema valida stock
3. Calcula total con impuestos
4. Procesa pago
5. Confirma orden
```

### 2. Nombres Descriptivos

**❌ Malo:**
```
diagram.png
design1.jpg
```

**✅ Bueno:**
```
checkout-flow-diagram.png
user-dashboard-mockup-v2.jpg
order-sequence-diagram.svg
```

### 3. Organización por Feature

Agrupar toda la documentación de un feature:

```
business/
└── features/
    └── checkout/
        ├── requirements.md
        ├── diagrams/
        ├── designs/
        └── specs/
```

### 4. Índices y Referencias

Crear archivos índice que referencien toda la documentación:

```markdown
# Feature: Checkout

## Documentación Completa

- [Requisitos](requirements/checkout-requirements.md)
- [Diagramas](diagrams/checkout/)
- [Diseños](designs/checkout/)
- [Especificaciones](specs/checkout-api-spec.md)
```

## Limitaciones y Soluciones

### Limitación: IA no "ve" imágenes directamente

**Solución:**
- Incluir descripciones detalladas en texto
- Usar nombres descriptivos
- Crear archivos `.md` que describan el contenido

### Limitación: Archivos grandes ralentizan

**Solución:**
- Usar `.cursorignore` para archivos muy grandes
- Comprimir imágenes
- Preferir texto cuando sea posible
- Usar links externos para archivos muy pesados

### Limitación: PDFs no son indexables

**Solución:**
- Extraer contenido importante a Markdown
- Incluir resumen en texto
- Referenciar PDF desde Markdown

## Ejemplo Completo

```
docs/business/
└── features/
    └── checkout/
        ├── README.md                    # Índice del feature
        ├── requirements/
        │   └── checkout-requirements.md  # Texto
        ├── diagrams/
        │   ├── checkout-flow.png         # Imagen
        │   └── checkout-flow.md         # Descripción
        ├── designs/
        │   ├── checkout-figma.md        # Link + descripción
        │   └── mockups/
        │       └── checkout-page.png    # Imagen
        └── specs/
            └── checkout-api-spec.md       # Texto
```

## Checklist para Agregar Documentación

- [ ] Organizar por feature o tema
- [ ] Usar nombres descriptivos
- [ ] Incluir descripciones en texto
- [ ] Crear archivos índice cuando sea necesario
- [ ] Comprimir imágenes grandes
- [ ] Extraer contenido de PDFs a Markdown
- [ ] Referenciar en código cuando se use
- [ ] Mantener actualizado

## Conclusión

**Sí, es excelente práctica** incluir documentación de negocio visual y textual, siempre que:

1. ✅ Esté bien organizada
2. ✅ Incluya descripciones en texto
3. ✅ Use nombres descriptivos
4. ✅ Esté referenciada en código
5. ✅ Se mantenga actualizada

Esto mejora significativamente la capacidad de los agentes de IA para entender y implementar correctamente las funcionalidades.

