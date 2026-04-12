# US-05 Ganar Puntos por Compra

## Descripción
Como cliente de un comercio, quiero ganar puntos cada vez que realizo una compra para poder redimirlos en futuras compras.

## Precondiciones
- El comercio tiene un programa de puntos activo con una ratio configurada
- La tienda está conectada con Tiendanube
- El webhook `order/paid` está registrado y activo

## Camino Feliz
1. El cliente completa una compra en Tiendanube
2. Tiendanube envía webhook `order/paid` al sistema
3. El sistema calcula los puntos: `monto_total × ratio_de_puntos`
4. Los puntos se acreditan al balance del cliente
5. Se registra la transacción en el historial

## Caminos Alternativos
- **3a. El cliente no existe en el sistema**: Se crea un perfil con email de Tiendanube y se acreditan los puntos

## Caminos de Error
- **2a. Webhook no recibido**: El sistema hace sync periódico de órdenes de respaldo cada 24 horas
- **4a. Error al acreditar**: Se reintenta 3 veces con backoff exponencial

## Criterios de Aceptación
- ✅ Los puntos se acreditan en < 10 segundos tras recibir el webhook
- ✅ Se registra: cliente, orden, puntos ganados, fecha
- ✅ El cálculo es correcto según la ratio configurada
- ✅ El historial es inmutable (solo se agregan transacciones, no se modifican)
