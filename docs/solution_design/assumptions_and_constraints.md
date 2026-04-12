# Supuestos y Restricciones — Mendri

## Propósito
Documentar las expectativas sobre datos, rendimiento, condiciones de ejecución y riesgos conocidos.

---

## Supuestos del Entorno

| # | Supuesto | Impacto si es falso |
|---|----------|---------------------|
| A1 | Tiendanube mantiene la API v2025-03 estable durante el desarrollo | Requerir adaptación de payloads y endpoints |
| A2 | Los webhooks de Tiendanube son entregados al menos una vez | Si se pierden, se necesitaría sync periódico de respaldo |
| A3 | Las tiendas tienen al menos un canal de comunicación (email o WhatsApp) configurado | Sin canal, no hay recuperación posible |
| A4 | N8N self-hosted tiene disponibilidad 24/7 | Si cae, se acumulan eventos sin procesar |
| A5 | PostgreSQL y RabbitMQ están disponibles en el entorno de producción | Sin infraestructura, el sistema no funciona |

---

## Supuestos de Datos

| # | Supuesto | Impacto si es falso |
|---|----------|---------------------|
| D1 | Los emails de clientes en Tiendanube son válidos | Emails de recuperación rebotan |
| D2 | Los números de teléfono (si existen) están en formato internacional | WhatsApp no puede entregar mensajes |
| D3 | Los precios de productos están en una sola moneda por tienda | El cálculo de puntos podría ser incorrecto |
| D4 | Cada `checkouts/created` corresponde a un cliente identificable | Sin cliente, no se puede enviar recuperación |
| D5 | El campo `order/paid` se dispara solo cuando el pago se confirma | Puntos otorgados por pagos no confirmados |

---

## Supuestos Operacionales

| # | Supuesto | Impacto si es falso |
|---|----------|---------------------|
| O1 | El comercio configura la ratio de puntos antes de activar el programa | Sin ratio, no se calculan puntos |
| O2 | El comercio define el contenido de los emails de recuperación | Sin contenido, no se envían emails |
| O3 | Hay al menos un admin del comercio que accede al dashboard | Sin admin, nadie configura ni ve métricas |

---

## Restricciones Técnicas

| # | Restricción | Detalle |
|---|-------------|---------|
| T1 | Rate limit de Tiendanube | 40 requests burst, 2 req/seg drain |
| T2 | Timeout de Business Rules API | 800ms para callbacks |
| T3 | Metafields de Tiendanube | Almacenamiento limitado por recurso (key-value namespaced) |
| T4 | N8N self-hosted | Debe escalar horizontalmente si crece la carga de workflows |
| T5 | WhatsApp Business API | Requiere aprobación de templates por Meta antes de enviar |

---

## Restricciones Funcionales

| # | Restricción | Detalle |
|---|-------------|---------|
| F1 | Solo se soporta Tiendanube como plataforma de ecommerce | No Mercado Shops, WooCommerce, Shopify |
| F2 | El MVP no incluye storefront widget | Los clientes no ven sus puntos en la tienda |
| F3 | Un cliente solo puede pertenecer a una tienda | No hay clientes cross-tienda |
| F4 | La redención de puntos es solo como descuento (no como producto gratis) | Se aplica al total de la orden |

---

## Restricciones Operacionales

| # | Restricción | Detalle |
|---|-------------|---------|
| OP1 | El sistema se despliega con Docker Compose | No Kubernetes, no serverless en esta fase |
| OP2 | Una sola instancia de N8N para MVP | Sin clustering de N8N |
| OP3 | Monitoreo básico (logs + health checks) | Sin APM avanzado en MVP |

---

## Riesgos Conocidos

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|--------|-------------|---------|------------|
| R1 | Tiendanube cambia su API sin aviso previo | Baja | Alto | Suscribirse a changelog de devs, tests de integración periódicos |
| R2 | Webhooks no entregados por caída de red | Media | Medio | Reintento con backoff + sync periódico de respaldo |
| R3 | Templates de WhatsApp rechazados por Meta | Media | Alto | Tener email como canal fallback |
| R4 | Rate limit excedido durante sync de catálogo | Media | Bajo | Implementar backoff exponencial con tenacity |
| R5 | Datos inconsistentes entre Tiendanube y DB local | Baja | Medio | Validación periódica de integridad |

---

## Validación

Este documento se considera aprobado cuando:
- Todos los supuestos son razonables para el equipo de desarrollo
- Los riesgos tienen mitigación definida
- Las restricciones son aceptadas como límites del sistema
