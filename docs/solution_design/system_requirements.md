# Requisitos del Sistema — Mendri Loyalty

## Propósito
Documentar los requisitos no negociables del sistema y entorno para que la solución funcione correctamente. Este documento define restricciones, no implementación.

---

## Entorno de Ejecución

- **Sistema operativo**: Linux (producción), macOS (desarrollo)
- **Runtime**: Docker Compose (desarrollo y producción)
- **Requisitos de red**:
  - Acceso a internet para conectar con APIs externas (Tiendanube, WhatsApp)
  - Puerto 8000 expuesto (backend API)
  - Puerto 3000 expuesto (frontend)
  - Puerto 5678 expuesto (N8N)
- **Navegadores**: Chrome 120+, Firefox 115+, Safari 17+

---

## Requisitos de la Aplicación

- **Base de datos**: PostgreSQL 15+
- **Message Broker**: RabbitMQ 3+
- **Background Tasks**: Celery 5+ con workers activos
- **Automatización**: N8N self-hosted (última versión estable)
- **Servicios externos requeridos**:
  - Tiendanube API v2025-03 (OAuth 2.0)
  - WhatsApp Business API (vía proveedor o Meta Cloud API)
  - Servicio de email (SMTP o API: SendGrid, Resend, etc.)
- **Permisos requeridos**:
  - API key de Tiendanube con permisos de: productos, clientes, órdenes, carritos, webhooks, metafields
  - Credenciales de WhatsApp Business API
  - Credenciales de servicio de email

---

## Requisitos de Datos

- **Entrada**: Webhooks de Tiendanube (JSON) con eventos: `order/paid`, `checkouts/created`, `product/updated`
- **Formato**: Los payloads deben seguir el esquema oficial de Tiendanube API v2025-03
- **Calidad**: Se asume que los datos de Tiendanube son consistentes y válidos
- **Esquema**: Base de datos PostgreSQL con tablas para tiendas (tenants), clientes, puntos, transacciones de puntos, carritos abandonados

---

## Rendimiento

- **Procesamiento de webhooks**: < 5 segundos desde recepción hasta respuesta
- **Envío de emails de recuperación**: entre 1 y 24 horas después del abandono (configurable por el comercio)
- **Envío de WhatsApp de recuperación**: entre 2 y 48 horas después del abandono (configurable)
- **Tolerancia a fallos**: reintentos automáticos con backoff exponencial para webhooks fallidos
- **Rate limiting**: respetar límites de Tiendanube (40 requests burst, 2 req/seg)

---

## Disponibilidad y Estabilidad

- **Disponibilidad esperada**: 99.9% (el sistema procesa eventos asíncronos, tolera breves caídas)
- **Estabilidad de APIs**: Tiendanube garantiza estabilidad de su API v2025-03
- **Backups**: diarios de la base de datos PostgreSQL
- **Ventanas de mantenimiento**: fuera de horario comercial (22:00 - 06:00 UTC-3)

---

## Seguridad y Cumplimiento

- **Clasificación de datos**: datos de clientes (email, teléfono, historial de compras) — sensibles
- **Manejo de credenciales**:
  - Tokens OAuth de Tiendanube almacenados cifrados
  - API keys de WhatsApp y email nunca en código ni logs
  - Variables de entorno para todas las credenciales
- **Logging**: estructurado, sin datos personales ni credenciales
- **Autenticación**: JWT para acceso al dashboard del comercio

---

## No-Requisitos

- **No se requiere**: storefront widget en el MVP
- **No se soporta**: tiendas fuera de Tiendanube (Mercado Shops, WooCommerce, etc.)
- **No es objetivo**: reemplazar el checkout de Tiendanube
- **Fuera de alcance en MVP**: gamificación, referidos, VIP tiers, dashboard avanzado

---

## Validación

La solución se considera conforme si:
- Todos los requisitos anteriores se cumplen
- No hay asunciones no documentadas
- Las desviaciones están documentadas y aprobadas
