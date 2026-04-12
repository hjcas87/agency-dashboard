# US-01 Conectar Tienda con Tiendanube

## Descripción
Como administrador de un comercio, quiero conectar mi tienda de Tiendanube con Mendri Loyalty para poder activar el programa de fidelización y recuperación de carritos.

## Precondiciones
- El comercio tiene una tienda activa en Tiendanube
- El comercio tiene credenciales de administrador en Tiendanube

## Camino Feliz
1. El admin hace clic en "Conectar con Tiendanube"
2. Es redirigido al flujo OAuth de Tiendanube
3. Autoriza la aplicación Mendri Loyalty
4. Es redirigido de vuelta al dashboard de Mendri
5. Se muestra confirmación: "Tienda conectada exitosamente"
6. Se inicia la sincronización inicial del catálogo en segundo plano

## Caminos Alternativos
- **3a. El usuario cancela la autorización**: Se muestra mensaje "Conexión cancelada. Intente nuevamente cuando esté listo"
- **5a. La tienda ya estaba conectada**: Se muestra "Esta tienda ya está conectada" con opción de reconectar

## Caminos de Error
- **2a. Error de red al redirigir a Tiendanube**: Mostrar "Error de conexión. Verifique su conexión a internet e intente nuevamente"
- **3a. Token OAuth inválido**: Mostrar "Error de autenticación con Tiendanube. Intente nuevamente"

## Criterios de Aceptación
- ✅ El admin puede iniciar el flujo OAuth desde el dashboard
- ✅ Tras autorizar, la tienda queda registrada en el sistema
- ✅ Se almacenan: store_id, access_token, tienda nombre, moneda
- ✅ Se registra un webhook listener para la tienda conectada
- ✅ Se inicia sync del catálogo automáticamente
