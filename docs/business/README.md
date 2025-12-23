# Documentación de Negocio

Este directorio contiene toda la documentación de negocio, requisitos funcionales, diagramas y diseños que guían el desarrollo del proyecto.

## Estructura

```
business/
├── requirements/      # Requisitos funcionales
│   ├── user-stories/
│   ├── use-cases/
│   └── functional-specs/
├── diagrams/          # Diagramas
│   ├── architecture/
│   ├── flowcharts/
│   ├── sequence/
│   └── er-diagrams/
├── designs/           # Diseños UI/UX
│   ├── figma/
│   ├── mockups/
│   └── wireframes/
├── specs/            # Especificaciones técnicas de negocio
│   ├── api-specs/
│   ├── data-models/
│   └── business-rules/
└── assets/           # Recursos (imágenes, PDFs, etc.)
    ├── images/
    ├── pdfs/
    └── exports/
```

## Cómo Usar Esta Documentación

### Para Desarrolladores

1. **Antes de implementar una feature**:

   - Revisar requisitos en `requirements/`
   - Consultar diagramas relevantes en `diagrams/`
   - Verificar diseños en `designs/`
   - Leer especificaciones en `specs/`

2. **Durante el desarrollo**:

   - Referenciar diagramas de flujo
   - Seguir diseños de UI
   - Implementar según especificaciones
   - Documentar desviaciones

3. **Al completar**:
   - Verificar que cumple requisitos
   - Comparar con diseños
   - Actualizar documentación si hay cambios

### Para Agentes de IA

Los agentes de IA (Cursor, Codex) deben:

1. **Consultar esta documentación** antes de implementar features
2. **Referenciar diagramas** al crear flujos
3. **Seguir diseños** al crear componentes UI
4. **Cumplir especificaciones** de negocio

**Ejemplo de instrucción para agente:**

```
Implementar feature 'checkout' según:
- Requisitos: docs/business/requirements/checkout.md
- Diagrama de flujo: docs/business/diagrams/flowcharts/checkout-flow.png
- Diseño UI: docs/business/designs/figma/checkout.figma
- Especificaciones: docs/business/specs/api-specs/checkout-api.md
```

## Tipos de Documentación

### Requirements (Requisitos)

- **User Stories**: Historias de usuario
- **Use Cases**: Casos de uso detallados
- **Functional Specs**: Especificaciones funcionales

### Diagrams (Diagramas)

- **Architecture**: Diagramas de arquitectura
- **Flowcharts**: Flujos de proceso
- **Sequence**: Diagramas de secuencia
- **ER Diagrams**: Modelos de datos

### Designs (Diseños)

- **Figma**: Archivos de Figma (exportados o links)
- **Mockups**: Mockups de UI
- **Wireframes**: Wireframes de baja fidelidad

### Specs (Especificaciones)

- **API Specs**: Especificaciones de APIs
- **Data Models**: Modelos de datos de negocio
- **Business Rules**: Reglas de negocio

## Mejores Prácticas

### Para Analistas de Negocio

1. **Organizar por feature**: Agrupar documentación relacionada
2. **Nombres descriptivos**: Usar nombres claros para archivos
3. **Versionar**: Mantener versiones de documentos importantes
4. **Actualizar**: Mantener documentación actualizada
5. **Referenciar**: Referenciar entre documentos relacionados

### Para Desarrolladores

1. **Consultar primero**: Revisar documentación antes de codificar
2. **Seguir diseños**: Implementar según diseños proporcionados
3. **Cumplir requisitos**: Verificar que se cumplen todos los requisitos
4. **Documentar cambios**: Si hay desviaciones, documentarlas
5. **Actualizar docs**: Si el código cambia, actualizar documentación

### Para Agentes de IA

1. **Leer documentación**: Siempre consultar docs relevantes
2. **Referenciar**: Mencionar qué documentos se usaron
3. **Seguir especificaciones**: Implementar según especificaciones
4. **Validar**: Verificar que la implementación cumple requisitos

## Formato de Archivos

### Markdown para Texto

- `.md` para requisitos, especificaciones
- Incluir ejemplos y casos de uso

### Imágenes

- `.png`, `.jpg` para diagramas y mockups
- `.svg` para diagramas vectoriales
- Incluir descripción en nombre del archivo

### PDFs

- `.pdf` para documentos completos
- Incluir índice y versionado

### Figma

- Links a archivos de Figma
- O exports en formato imagen/PDF
- Documentar componentes y estilos

## Ejemplo de Estructura por Feature

```
business/
└── features/
    └── checkout/
        ├── requirements/
        │   └── checkout-requirements.md
        ├── diagrams/
        │   ├── checkout-flow.png
        │   └── checkout-sequence.png
        ├── designs/
        │   ├── checkout-figma-link.md
        │   └── checkout-mockups/
        └── specs/
            └── checkout-api-spec.md
```

## Integración con Desarrollo

Esta documentación se integra con:

- **`.cursorrules`**: Referencia esta documentación
- **`AGENTS.md`**: Instrucciones para agentes de IA
- **Features**: Cada feature puede tener su documentación aquí
- **Tests**: Tests deben validar requisitos de esta documentación

## Versionado

- Usar nombres descriptivos con fechas o versiones
- Ejemplo: `checkout-requirements-v1.2.md`
- Mantener changelog de cambios importantes
