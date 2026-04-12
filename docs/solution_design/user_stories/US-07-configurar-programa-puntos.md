# US-07 Configurar Programa de Puntos

## Descripción
Como administrador de un comercio, quiero configurar la ratio de puntos y las reglas del programa de fidelización para adaptarlo a mi negocio.

## Precondiciones
- El admin tiene una tienda conectada (US-01)
- El admin está autenticado en el dashboard

## Camino Feliz
1. El admin accede a la sección "Programa de Puntos"
2. Configura la ratio: "$X = 1 punto"
3. Opcionalmente configura: puntos mínimo para redimir, vigencia de puntos
4. Guarda la configuración
5. El sistema confirma: "Programa de puntos activado"

## Criterios de Aceptación
- ✅ La ratio se puede cambiar en cualquier momento (afecta solo compras futuras)
- ✅ Se registra la configuración: ratio, fecha de creación, último cambio
- ✅ Las compras anteriores mantienen los puntos calculados con la ratio vigente al momento
