# Diseño: Checkout Page

## Figma

**Link**: [Ver diseño en Figma](https://figma.com/file/example-checkout)

**Versión**: v1.2  
**Última actualización**: 2024-01-XX

## Componentes Principales

### Layout

- **Header**: Logo y navegación
- **Main Content**: Formulario de checkout (2 columnas)
  - **Columna Izquierda**: Formulario
  - **Columna Derecha**: Resumen del pedido
- **Footer**: Información de contacto

### Componentes UI

1. **Shipping Form**
   - Input: Nombre completo
   - Input: Dirección
   - Input: Ciudad
   - Input: Código postal
   - Select: País

2. **Payment Method**
   - Radio buttons: Tarjeta, Transferencia, PayPal
   - Si Tarjeta: Formulario de tarjeta
   - Si Transferencia: Mostrar datos bancarios

3. **Order Summary**
   - Lista de items
   - Subtotal
   - Impuestos
   - Envío
   - Total

4. **Action Buttons**
   - "Volver al carrito" (secundario)
   - "Confirmar pedido" (primario)

## Especificaciones de Diseño

### Colores

- **Primary**: #3B82F6 (Blue 500)
- **Primary Hover**: #2563EB (Blue 600)
- **Background**: #F9FAFB (Gray 50)
- **Text Primary**: #111827 (Gray 900)
- **Text Secondary**: #6B7280 (Gray 500)
- **Border**: #E5E7EB (Gray 200)
- **Error**: #EF4444 (Red 500)

### Tipografía

- **Heading**: Inter, 24px, Bold
- **Body**: Inter, 16px, Regular
- **Label**: Inter, 14px, Medium
- **Small**: Inter, 12px, Regular

### Espaciado

- **Container Padding**: 24px
- **Section Gap**: 32px
- **Field Gap**: 16px
- **Button Padding**: 12px 24px

### Componentes shadcn/ui a Usar

- `Card` - Para resumen del pedido
- `Input` - Para campos de formulario
- `Select` - Para dropdowns
- `RadioGroup` - Para método de pago
- `Button` - Para acciones
- `Label` - Para labels de formulario

## Estados

### Estados del Formulario

- **Default**: Campos vacíos, botón deshabilitado
- **Validating**: Mostrar spinners en campos
- **Error**: Mostrar mensajes de error debajo de campos
- **Success**: Mostrar confirmación

### Responsive

- **Desktop**: 2 columnas (formulario | resumen)
- **Tablet**: 2 columnas apiladas
- **Mobile**: 1 columna, resumen al final

## Implementación

### Archivos a Crear

- `frontend/app/checkout/page.tsx` - Página principal
- `frontend/components/custom/checkout/ShippingForm.tsx`
- `frontend/components/custom/checkout/PaymentMethod.tsx`
- `frontend/components/custom/checkout/OrderSummary.tsx`

### Referencias

- Requisitos: `../requirements/checkout-requirements.md`
- Flujo: `../diagrams/checkout-flow-description.md`
- API: `../specs/checkout-api-spec.md`

