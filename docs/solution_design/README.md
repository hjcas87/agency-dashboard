# Solution Design — Mendri Loyalty

**Versión**: v1.0
**Fecha**: 2025-04-11
**Proyecto**: Mendri Loyalty

## Documentos

| Documento | Descripción |
|-----------|-------------|
| [Requisitos del Sistema](./system_requirements.md) | Requisitos técnicos y de entorno |
| [Alcance](./scope.md) | Qué está dentro y fuera del MVP |
| [Supuestos y Restricciones](./assumptions_and_constraints.md) | Expectativas y riesgos conocidos |

## User Stories

| ID | Story | Feature |
|----|-------|---------|
| US-01 | [Conectar Tienda con Tiendanube](./user_stories/US-01-conectar-tienda-tiendanube.md) | tiendanube-connection |
| US-02 | [Detectar Carrito Abandonado](./user_stories/US-02-detectar-carrito-abandonado.md) | abandoned-cart |
| US-03 | [Recuperar Carrito por Email](./user_stories/US-03-recuperar-carrito-email.md) | abandoned-cart |
| US-04 | [Recuperar Carrito por WhatsApp](./user_stories/US-04-recuperar-carrito-whatsapp.md) | abandoned-cart (N8N) |
| US-05 | [Ganar Puntos por Compra](./user_stories/US-05-ganar-puntos-compra.md) | loyalty |
| US-06 | [Redimir Puntos como Descuento](./user_stories/US-06-redimir-puntos-descuento.md) | loyalty |
| US-07 | [Configurar Programa de Puntos](./user_stories/US-07-configurar-programa-puntos.md) | loyalty |
| US-08 | [Ver Métricas del Programa](./user_stories/US-08-ver-metricas-programa.md) | dashboard |

## Diagramas

> Los diagramas se crearán en formato Excalidraw (`.excalidraw`) a medida que se definan los flujos.

## Reglas

- Estos documentos están **acordados con el cliente** (o aprobados internamente)
- Son la **única fuente de verdad** funcional del proyecto
- **No contienen detalles de implementación** técnica
- Están escritos en **español** para revisión y discusión
- Cada user story mapea a **exactamente un feature** (backend + frontend si aplica)
