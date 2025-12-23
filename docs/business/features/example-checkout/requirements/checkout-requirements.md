# Requisitos Funcionales: Checkout

## Feature: Checkout

### Descripción
Sistema de checkout que permite a los usuarios completar una compra de productos.

## User Stories

### US-001: Completar Compra
**Como** cliente  
**Quiero** completar una compra  
**Para** recibir los productos que deseo

**Criterios de Aceptación:**
- [ ] Puedo ingresar información de envío
- [ ] Puedo seleccionar método de pago
- [ ] Puedo revisar el resumen antes de confirmar
- [ ] Recibo confirmación de la orden

## Casos de Uso

### UC-001: Proceso de Checkout Completo

**Actor Principal**: Cliente

**Precondiciones:**
- Cliente tiene items en el carrito
- Cliente está autenticado

**Flujo Principal:**
1. Cliente accede a checkout
2. Sistema muestra resumen del carrito
3. Cliente ingresa información de envío
4. Cliente selecciona método de pago
5. Cliente confirma orden
6. Sistema procesa pago
7. Sistema crea orden
8. Sistema envía confirmación

**Postcondiciones:**
- Orden creada en sistema
- Pago procesado
- Cliente recibe confirmación

## Requisitos Funcionales

### RF-001: Validación de Stock
**Descripción**: El sistema debe validar stock antes de confirmar orden

**Reglas de Negocio:**
- Si no hay stock suficiente, mostrar error
- Permitir actualizar cantidad o eliminar item

### RF-002: Cálculo de Totales
**Descripción**: Calcular total incluyendo impuestos y envío

**Reglas de Negocio:**
- Subtotal = suma de items
- Impuestos = 21% del subtotal
- Envío según zona
- Total = subtotal + impuestos + envío

## Referencias

- Diagrama de flujo: `../diagrams/checkout-flow.png`
- Diseño UI: `../designs/checkout-figma.md`
- Especificación API: `../specs/checkout-api-spec.md`

