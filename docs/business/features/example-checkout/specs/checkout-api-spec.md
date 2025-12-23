# Especificación API: Checkout

## Endpoints

### POST /api/v1/checkout

Crea una nueva orden de compra.

**Request Body:**
```json
{
  "shipping_address": {
    "name": "John Doe",
    "address": "123 Main St",
    "city": "Buenos Aires",
    "postal_code": "C1000",
    "country": "AR"
  },
  "payment_method": "card",
  "card_details": {
    "number": "4111111111111111",
    "expiry": "12/25",
    "cvv": "123"
  }
}
```

**Response 201:**
```json
{
  "order_id": "12345",
  "status": "confirmed",
  "total": 1250.50,
  "estimated_delivery": "2024-01-15"
}
```

**Errors:**
- `400`: Stock insuficiente
- `400`: Datos de pago inválidos
- `422`: Validación fallida

### GET /api/v1/checkout/shipping-cost

Calcula costo de envío.

**Query Parameters:**
- `postal_code` (required)
- `country` (required)

**Response 200:**
```json
{
  "shipping_cost": 500.00,
  "estimated_days": 5
}
```

## Modelo de Datos

### Order

```python
class Order(Base):
    id: int
    user_id: int
    shipping_address: JSON
    payment_method: str
    total: Decimal
    status: str  # pending, confirmed, shipped, delivered
    created_at: datetime
    updated_at: datetime
```

## Reglas de Negocio

1. **Validación de Stock**: Verificar antes de crear orden
2. **Cálculo de Totales**: Subtotal + Impuestos (21%) + Envío
3. **Procesamiento de Pago**: Asíncrono con Celery
4. **Confirmación**: Enviar email después de confirmar

## Referencias

- Requisitos: `../requirements/checkout-requirements.md`
- Flujo: `../diagrams/checkout-flow-description.md`
- Diseño: `../designs/checkout-figma.md`

