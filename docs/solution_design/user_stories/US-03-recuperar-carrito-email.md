# US-03 Recuperar Carrito por Email

## Descripción
Como comercio, quiero que se envíen emails automáticos a los clientes que abandonaron su carrito para incentivarlos a completar la compra.

## Precondiciones
- El carrito abandonado fue detectado (US-02)
- El cliente tiene un email válido registrado
- El comercio configuró la secuencia de emails

## Camino Feliz
1. Se cumple el tiempo de espera configurado (ej: 2 horas)
2. El sistema verifica que el carrito NO fue convertido
3. N8N envía el primer email de recuperación con el resumen del carrito
4. Si no convierte en X horas, se envía segundo email con incentivo (ej: descuento)
5. El comercio puede ver en el dashboard cuántos emails se enviaron y cuántos resultaron en conversión

## Caminos Alternativos
- **2a. El carrito fue convertido**: Se cancela toda la secuencia de emails

## Criterios de Aceptación
- ✅ El email incluye: nombre del cliente, items del carrito, link al checkout
- ✅ El segundo email incluye incentivo si el comercio lo configuró
- ✅ Se registra: email enviado, fecha, si fue abierto, si resultó en conversión
- ✅ Máximo 2 emails por carrito abandonado
