# Alcance — Mendri Loyalty

## Propósito
Definir explícitamente qué está dentro y fuera del alcance del MVP de Mendri Loyalty.

---

## Dentro del Alcance (MVP)

### 1. Conexión con Tiendanube
- Registro de tienda vía OAuth
- Recepción y almacenamiento de webhooks (`order/paid`, `checkouts/created`, `product/updated`)
- Sync inicial de catálogo de productos (pull on demand)
- Actualización incremental vía webhooks

### 2. Recuperación de Carritos Abandonados
- Detección automática de carritos no convertidos
- Secuencia de emails de recuperación (configurable: cantidad, timing, contenido)
- Secuencia de mensajes de WhatsApp de recuperación (configurable)
- Registro de carritos recuperados vs no recuperados

### 3. Programa de Puntos (Simple)
- El cliente gana puntos al completar una compra (`order/paid`)
- Ratio de puntos configurable por el comercio (ej: $1 = 1 punto)
- Balance de puntos almacenado en base de datos propia
- Redención de puntos como descuento en la próxima compra
- Historial de transacciones de puntos (ganados y gastados)

### 4. Dashboard Básico del Comercio
- Ver métricas de carritos abandonados y recuperados
- Ver métricas de puntos otorgados y redimidos
- Configurar ratio de puntos
- Configurar timing de emails/WhatsApp de recuperación

---

## Fuera de Alcance (MVP)

- **Gamificación**: badges, logros, niveles, streaks
- **Sistema de referidos**: códigos de invitación, bonificaciones
- **VIP Tiers**: Bronze, Silver, Gold basados en puntos acumulados
- **Storefront Widget**: componente visual en la tienda del comercio
- **Dashboard avanzado**: cohortes, RFM, LTV predictivo, segmentación
- **Multi-tenancy completo**: se diseña la base (`tenant_id`) pero se valida con 1-2 tiendas
- **App móvil**: solo dashboard web

---

## Escenarios Soportados

| Escenario | Soportado en MVP |
|-----------|-----------------|
| Tienda conecta su cuenta de Tiendanube | ✅ |
| Tienda recibe webhooks automáticamente | ✅ |
| Cliente abandona carrito → recibe email | ✅ |
| Cliente abandona carrito → recibe WhatsApp | ✅ |
| Cliente completa compra → gana puntos | ✅ |
| Cliente redime puntos como descuento | ✅ |
| Comercio configura ratio de puntos | ✅ |
| Comercio ve métricas básicas | ✅ |

---

## Escenarios NO Soportados (MVP)

| Escenario | Disponible en |
|-----------|--------------|
| Cliente ve sus puntos en storefront | Fase 2 |
| Cliente gana badge por 5 compras seguidas | Fase 2 |
| Cliente comparte código de referido | Fase 2 |
| Comercio ve análisis de cohortes | Fase 3 |
| Tienda con múltiples sucursales | Fase 3 |
| Programa de puntos con niveles VIP | Fase 2 |

---

## Criterios de Aceptación

1. **Conexión Tiendanube**: Una tienda puede conectar su cuenta y recibir webhooks en < 1 minuto
2. **Carrito abandonado**: El sistema detecta un carrito abandonado y envía el primer email en el tiempo configurado
3. **Puntos ganados**: Al completar una orden, los puntos se acreditan en < 10 segundos
4. **Redención**: El cliente puede aplicar un descuento por puntos en su próxima compra
5. **Métricas**: El comercio puede ver al menos: carritos abandonados (total, tasa de recuperación), puntos otorgados (total, redimidos)

---

## Política de Cambio de Alcance

Cualquier cambio en el alcance debe:
1. Ser documentado como actualización de este archivo
2. Ser aprobado por el equipo de producto
3. Reflejarse en los user stories afectados
4. Actualizar la estimación de esfuerzo si corresponde
