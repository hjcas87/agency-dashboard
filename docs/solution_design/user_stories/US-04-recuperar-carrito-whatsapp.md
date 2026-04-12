# US-04 Recuperar Carrito por WhatsApp

## Descripción
Como comercio, quiero que se envíen mensajes de WhatsApp a los clientes que abandonaron su carrito para incentivarlos a completar la compra.

## Precondiciones
- El carrito abandonado fue detectado (US-02)
- El cliente tiene un número de teléfono válido registrado
- El comercio tiene WhatsApp Business API configurado
- Los templates de WhatsApp están aprobados por Meta

## Camino Feliz
1. Se cumple el tiempo de espera configurado (ej: 4 horas, después del email)
2. El sistema verifica que el carrito NO fue convertido
3. N8N envía mensaje de WhatsApp con resumen del carrito y link de checkout
4. Si no convierte en X horas, se envía segundo mensaje con incentivo
5. El comercio puede ver en el dashboard cuántos WhatsApp se enviaron y cuántos resultaron en conversión

## Criterios de Aceptación
- ✅ El mensaje incluye: saludo personalizado, items del carrito, link al checkout
- ✅ Se envía solo si el cliente tiene teléfono registrado
- ✅ Se respeta la plantilla aprobada por Meta
- ✅ Se registra: mensaje enviado, fecha, estado de entrega, conversión
