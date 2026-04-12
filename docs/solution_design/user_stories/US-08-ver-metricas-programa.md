# US-08 Ver Métricas del Programa

## Descripción
Como administrador de un comercio, quiero ver métricas básicas del programa de fidelización y recuperación para evaluar su efectividad.

## Precondiciones
- El admin tiene una tienda conectada (US-01)
- El programa de puntos y/o recuperación de carritos está activo

## Camino Feliz
1. El admin accede al dashboard
2. Ve las siguientes métricas:
   - **Carritos abandonados**: total en los últimos 30 días
   - **Tasa de recuperación**: % de carritos abandonados que se convirtieron tras recibir email/WhatsApp
   - **Puntos otorgados**: total en los últimos 30 días
   - **Puntos redimidos**: total en los últimos 30 días
   - **Clientes activos**: cantidad de clientes con puntos > 0

## Criterios de Aceptación
- ✅ Las métricas se actualizan al menos cada hora
- ✅ Se puede filtrar por rango de fechas (7, 30, 90 días)
- ✅ Los datos son consistentes con las transacciones reales en la base de datos
