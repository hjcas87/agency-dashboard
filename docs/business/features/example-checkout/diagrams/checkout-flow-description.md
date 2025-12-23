# Descripción: Checkout Flow Diagram

## Archivo
`checkout-flow.png` (o `checkout-flow.svg`)

## Descripción del Diagrama

Este diagrama muestra el flujo completo del proceso de checkout:

### Pasos del Flujo

1. **Inicio**: Usuario accede a checkout desde carrito
2. **Validación de Carrito**: 
   - Verificar que carrito no esté vacío
   - Validar stock de cada item
3. **Información de Envío**:
   - Usuario ingresa dirección
   - Sistema calcula costo de envío
4. **Método de Pago**:
   - Usuario selecciona tarjeta/transferencia/etc
   - Sistema valida método
5. **Revisión**:
   - Mostrar resumen completo
   - Usuario puede editar o continuar
6. **Procesamiento**:
   - Procesar pago
   - Crear orden
   - Actualizar stock
7. **Confirmación**:
   - Mostrar confirmación
   - Enviar email

### Puntos de Decisión

- **Stock insuficiente**: Redirigir a carrito con mensaje
- **Pago fallido**: Mostrar error, permitir reintentar
- **Timeout**: Guardar progreso, permitir continuar después

### Flujos Alternativos

- **Usuario no autenticado**: Redirigir a login
- **Carrito vacío**: Redirigir a productos
- **Error de conexión**: Mostrar mensaje, permitir reintentar

## Uso para Implementación

Al implementar el feature checkout:
1. Seguir este flujo exactamente
2. Implementar todas las validaciones mencionadas
3. Manejar todos los flujos alternativos
4. Incluir puntos de decisión

## Referencias

- Requisitos: `../requirements/checkout-requirements.md`
- Diseño: `../designs/checkout-figma.md`

