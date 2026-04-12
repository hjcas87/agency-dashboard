# US-06 Redimir Puntos como Descuento

## Descripción
Como cliente de un comercio, quiero poder usar mis puntos acumulados como descuento en mi próxima compra.

## Precondiciones
- El cliente tiene puntos acumulados en su balance
- El comercio tiene habilitada la redención de puntos

## Camino Feliz
1. El cliente inicia una compra en la tienda
2. Al momento de pagar, el sistema detecta que tiene puntos disponibles
3. Se aplica un descuento equivalente a los puntos redimidos
4. Los puntos redimidos se descuentan del balance
5. Se registra la transacción de redención en el historial

## Caminos Alternativos
- **3a. El cliente redime solo algunos puntos**: Elige cuántos puntos usar (hasta su balance total)
- **3b. El cliente no quiere redimir**: Continúa la compra sin descuento

## Criterios de Aceptación
- ✅ 1 punto = $1 de descuento (o ratio configurable)
- ✅ El cliente no puede redimir más puntos de los que tiene
- ✅ La redención se registra: cliente, puntos usados, descuento aplicado, fecha
- ✅ Si la orden se cancela, los puntos se devuelven al balance
