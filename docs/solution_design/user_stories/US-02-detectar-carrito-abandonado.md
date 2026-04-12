# US-02 Detectar Carrito Abandonado

## Descripción
Como sistema, quiero detectar automáticamente cuando un cliente abandona un carrito de compras para poder iniciar la secuencia de recuperación.

## Precondiciones
- La tienda está conectada con Tiendanube
- El webhook `checkouts/created` está registrado y activo

## Camino Feliz
1. Tiendanube envía webhook `checkouts/created` al sistema
2. El sistema valida y almacena el carrito abandonado
3. El sistema programa los mensajes de recuperación según la configuración del comercio
4. El sistema verifica periódicamente si el carrito fue convertido
5. Si no fue convertido en el tiempo configurado, se disparan los mensajes de recuperación

## Caminos Alternativos
- **4a. El carrito se convierte antes del primer mensaje**: Se cancelan todos los mensajes programados

## Caminos de Error
- **1a. Webhook no recibido**: El sistema hace sync periódico de respaldo cada 6 horas
- **2a. Error al almacenar**: Se reintentan 3 veces con backoff exponencial

## Criterios de Aceptación
- ✅ El sistema recibe y procesa webhooks `checkouts/created`
- ✅ Se almacena: cliente (email), items del carrito, total, fecha de creación
- ✅ Se verifica si el carrito fue convertido antes de enviar mensajes
- ✅ Los mensajes se envían solo si el carrito NO fue convertido
