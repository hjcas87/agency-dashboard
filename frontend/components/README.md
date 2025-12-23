# Frontend Components

Este directorio contiene los componentes del frontend organizados en dos categorías:

## Estructura

```
components/
├── core/          # Componentes base (NO modificar en forks)
└── custom/         # Componentes personalizados (modificar aquí)
```

## Core Components

Componentes base del sistema. Estos componentes **NO deben modificarse** en forks de clientes.

Incluye componentes de shadcn/ui y componentes base reutilizables.

## Custom Components

Este directorio está destinado a componentes personalizados específicos del cliente.

### Estructura Recomendada

```
custom/
├── ui/          # Componentes UI personalizados
├── features/    # Componentes de funcionalidades específicas
└── layouts/     # Layouts personalizados
```

## Notas Importantes

- Los componentes en `core/` NO deben modificarse en forks de clientes
- Todos los cambios personalizados deben ir en `custom/`
- Al actualizar desde el repo original, los cambios en `custom/` se preservan
- Usar shadcn/ui como base para componentes personalizados

