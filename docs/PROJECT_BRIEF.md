# Project Brief — Mendri

## Propósito
Este documento captura el acuerdo inicial sobre las necesidades y el desarrollo planificado del proyecto Mendri — una plataforma SaaS multi-tenant de fidelización de clientes para tiendas de Tiendanube.

**Creado por**: Core Team
**Fecha**: 2025-04-11
**Cliente**: Producto interno (no cliente externo)
**Proyecto**: Mendri

---

## Contexto

### Resumen del Negocio
Mendri es un producto SaaS interno dirigido a comercios de Tiendanube que buscan aumentar la retención de clientes y el lifetime value (LTV) a través de un programa de fidelización integrado.

### Situación Actual
- Las tiendas de Tiendanube no tienen herramientas nativas de fidelización
- Los carritos abandonados representan 60-70% de los checkouts iniciados sin recuperación activa
- Los comercios pierden clientes recurrentes por falta de incentivos estructurados

---

## Objetivos del Proyecto

### Objetivos Principales
- Recuperar carritos abandonados mediante email y WhatsApp automatizados
- Implementar un programa de puntos simple para incentivar compras repetidas
- Proveer dashboard al comercio con métricas de retención y recuperación

### Criterios de Éxito
- El sistema detecta carritos abandonados y envía mensajes de recuperación en < 1 hora
- Los clientes pueden ver y redimir sus puntos
- El comercio puede configurar reglas de earning (puntos por $ gastado)

---

## Alcance Inicial (Alto Nivel)

### En Alcance (MVP)
- Integración con Tiendanube vía API + Webhooks
- Detección de carritos abandonados (`checkouts/created` webhook)
- Secuencia de recuperación por email (N8N workflow)
- Secuencia de recuperación por WhatsApp (N8N workflow)
- Motor de puntos: earning simple ($1 = 1 punto configurable)
- Almacenamiento de balance en base de datos propia
- Redención de puntos (descuento en próxima compra)

### Fuera de Alcance (por ahora)
- Gamificación (badges, logros)
- Sistema de referidos
- VIP tiers (Bronce, Plata, Oro)
- Widget en storefront del comercio
- Multi-tenancy completo (se prepara la base, se implementa después)
- Dashboard avanzado (solo métricas básicas en MVP)

---

## Requisitos Clave

### Requisitos Funcionales
- La tienda conecta su cuenta de Tiendanube vía OAuth
- El sistema recibe webhooks de Tiendanube en tiempo real
- Se envía email de recuperación a los X minutos/horas del carrito abandonado
- Se envía mensaje de WhatsApp de recuperación a las Y horas
- El cliente gana puntos al completar una compra (`order/paid`)
- El comercio puede configurar la ratio de puntos ($1 = N puntos)
- El cliente puede redimir puntos como descuento

### Requisitos No Funcionales
- Resiliencia: si un webhook falla, se reintenta
- Latencia: procesamiento de webhook < 5 segundos
- Escalabilidad: soportar 100+ tiendas conectadas

---

## Integraciones y Automatizaciones

### Servicios/APIs Externas
- **Tiendanube API**: OAuth, productos, clientes, órdenes, carritos abandonados
- **Tiendanube Webhooks**: `order/paid`, `checkouts/created`, `product/updated`
- **Tiendanube Metafields**: almacenar puntos del cliente (cache rápido)
- **WhatsApp Business API**: vía N8N para mensajes de recuperación

### Automatizaciones N8N
- **Cart Recovery Email**: Webhook `checkouts/created` → wait X hours → check if converted → if not, send email sequence
- **Cart Recovery WhatsApp**: Webhook `checkouts/created` → wait Y hours → send WhatsApp message
- **Loyalty Points Award**: Webhook `order/paid` → calculate points → store in DB + Metafield

### Tareas en Background
- Sync periódico de catálogo de productos (pull on demand)
- Reintento de webhooks fallidos
- Limpieza de carritos expirados (> 30 días)

---

## Arquitectura Técnica

### Multi-Tenant Strategy
- Base de datos single-schema con `tenant_id` en todas las tablas de negocio
- Tenant resolution por `store_id` de Tiendanube (no subdomain en MVP)
- Se diseña para multi-tenant desde el inicio pero se valida con 1-2 tiendas

### Sync Strategy
- **Pull on Demand**: sync completo de productos al conectar tienda
- **Push on Webhook**: actualizaciones incrementales vía `product/updated`
- Rate limiting: respetar 40 burst / 2 req/sec de Tiendanube

### N8N Integration
- Todos los flujos de comunicación (email, WhatsApp) van por N8N
- El backend solo emite eventos, N8N maneja el canal y el template

---

## Restricciones Conocidas

### Restricciones Técnicas
- Tiendanube API: rate limit estricto (40 burst, 2 req/sec)
- Business Rules API: 800ms timeout para callbacks
- N8N self-hosted: debe escalar con la cantidad de tiendas

### Restricciones de Negocio
- Producto interno: no hay deadlines de cliente externo
- MVP debe ser usable con 1 tienda para validar el concepto

---

## Supuestos

- Tiendanube mantiene la API v2025-03 stable
- Los webhooks son confiables (con retry en caso de fallo)
- Los comercios tienen WhatsApp Business configurado o usan email como canal principal
- No se necesita storefront widget en el MVP

---

## Próximos Pasos

1. Este brief es aprobado como definición del proyecto
2. Generar `docs/solution_design/` basado en este brief (en español)
3. Crear rama `mendri-loyalty` desde `dev`
4. Implementar features en orden de prioridad:
   - `tiendanube-connection` (auth + webhook receiver + store registration)
   - `abandoned-cart` (detection + N8N email/WhatsApp flows)
   - `loyalty` (points engine + redemption)
5. Validar con 1 tienda de prueba

---

## Notas

- WhatsApp se maneja exclusivamente vía N8N, no como feature backend custom
- Multi-tenancy se diseña desde el inicio (tenant_id en modelos) pero se valida con pocas tiendas
- Los docs de referencia de Tiendanube están en `docs/references/tiendanube/`
