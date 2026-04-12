Referencia Técnica Completa de Recursos API Tiendanube (Versión 2025-03)
Esta guía detalla las estructuras de datos, campos y métodos para los 33 recursos de la API de Tiendanube.
________________
1. Abandoned Checkout (Checkout Abandonado)
Se genera cuando un cliente inicia el proceso pero no lo finaliza.
* Métodos: GET (lista/detalle), POST (interacciones de flujo).
* Estructura de Datos:
   * id (Integer): ID único.
   * token (String): Token de ubicación del pedido.
   * abandoned_checkout_url (String): URL para recuperar la compra.
   * contact_email, contact_name, contact_phone (String): Datos del comprador.
   * shipping_address, billing_address (String/Object): Direcciones completas.
   * subtotal, total, discount (String/Numeric): Montos financieros.
   * products (Array): Lista de productos incluidos.
2. Billing (Facturación)
Gestión de cobros de aplicaciones.
* Métodos: POST (planes/cargos), PATCH (actualizar), DELETE (eliminar).
* Estructura (Plan): id, code (moneda), external_reference, description, default (Boolean).
* Estructura (Suscripción): amount_value, amount_currency, recurring_frequency, next_execution (Date).
* Estructura (Cargo/Charge): amount_value, description, from_date, to_date.
3. Blog
Gestión de contenido informativo de la tienda.1
* Métodos: GET, POST, PUT, DELETE (orientados a artículos y categorías de blog).
* Estructura: Se basa en objetos de contenido con title (Object localizado), content (HTML localizado), author y status (published/draft).
4. Business Rules (Reglas de Negocio)
Define comportamientos dinámicos para pagos y envíos.
* Métodos: PUT (para registrar integraciones), POST (webhook de consulta).
* Estructura (Callback): url (HTTPS), event (ej. payments/before-filter), domain.
* Payload de Consulta: Contiene cart_id, products, customer y totals para que la app decida qué filtrar.
5. Cart (Carrito)
Manipulación de carritos activos en el storefront.
* Métodos: GET (detalle), DELETE (eliminar ítems o cupones).
* Estructura:
   * id (Numeric): ID del carrito.
   * items (Array): Objetos con variant_id, quantity, unit_price.
   * subtotal (Numeric): Monto antes de descuentos y envío.
6. Category (Categoría)
Organización jerárquica de productos.3
* Métodos: GET, POST, PUT, DELETE.
* Estructura:
   * id (Numeric): ID único.
   * name, description, handle (Object): Localizados por idioma.
   * parent (Numeric/Null): ID de categoría padre.
   * subcategories (List - ReadOnly): IDs de hijos directos.3
7. Category Custom Fields
Campos personalizados para categorías.1
* Métodos: GET, POST, PUT, DELETE.
* Estructura: id (UUID), name, value_type (Enum: text, numeric, date, text_list), values (Array para listas).3
8. Checkout
Interfaz de JavaScript para pagos.6
* Métodos: Funciones JS (getData, processPayment, setInstallments).
* Datos Disponibles: order.cart, totalPrice, order.billingAddress, form (datos capturados de tarjeta).7
9. Checkout SDK
Librería para personalización profunda del checkout.6
* Métodos: subscribeEvent('LINE_ITEMS_UPDATED'), hidePaymentOptions(ids), changePaymentBenefit(data).
* Eventos: Captura cambios en el carrito y permite inyectar lógica de visualización.6
10. Coupon (Cupón)
Herramientas de descuento promocional.8
* Métodos: GET, POST, PUT, DELETE.
* Estructura:
   * code (String): Código único.
   * type (Enum: percentage, absolute, shipping).
   * value (Numeric): Valor del descuento.
   * min_price (Numeric): Mínimo de compra.
   * max_uses (Integer): Límite de uso.8
11. Customer (Cliente)
Perfiles de compradores.
* Métodos: GET, POST, PUT, DELETE.
* Estructura:
   * id (Numeric): ID único.
   * name, email, phone, identification (String).
   * addresses (Array): Lista de direcciones.
   * total_spent (String/Numeric): Gasto histórico acumulado.9
12. Customer Custom Fields
Campos personalizados para perfiles de cliente.
* Métodos: GET, POST, PUT, DELETE.
* Estructura: Sigue el estándar de Custom Fields con owner_resource: customer y value_type definido.
13. Discount (Descuento)
Reglas de promociones aplicadas automáticamente.
* Métodos: POST (crear promociones), GET (listar), DELETE.
* Concepto: Se divide en Promotion (la regla) y Discount (el valor resultante aplicado al total o ítem).
14. Draft Order (Pedido Borrador)
Pedidos creados por canales externos.1
* Métodos: POST (crear), GET (detalle).
* Estructura: Similar al recurso de Orden, pero permite definir precios manuales y productos sin necesidad de que existan en el catálogo público.2
15. Email Templates
Plantillas de correos automáticos.4
* Métodos: GET, PUT.
* Estructura:
   * id (Integer), type (Enum: orderconfirmation, ordershipped, etc.).
   * subject, template_html, template_text (Object): Localizados por idioma.4
16. Fulfillment Order
Gestión de envíos múltiples por pedido.1
* Métodos: GET, POST (crear envío).
* Estructura: Contiene la lista de ítems (line_items) asignados a un paquete específico, status del envío y datos de rastreo.10
17. Location (Ubicación)
Puntos de stock físico.1
* Métodos: GET, POST, PUT, DELETE.
* Estructura: id, name, address, phone. Es fundamental para la gestión de inventario multi-ubicación.5
18. Metafields
Almacén clave-valor para aplicaciones.
* Métodos: GET, POST, PUT, DELETE.
* Estructura: id, namespace, key, value, owner_resource (Product, Order, etc.), owner_id.
19. Order (Orden/Pedido)
Transacciones completadas.10
* Métodos: GET, POST, PUT.
* Estructura:
   * number (Numeric): Número de orden.
   * status, payment_status, shipping_status (String).
   * products (Array): Ítems comprados con price, quantity, sku.
   * gateway (String): Proveedor de pago usado.
20. Order Custom Fields
Campos personalizados para pedidos.
* Métodos: GET, POST, PUT, DELETE.
* Estructura: UUID id, name, value_type, owner_resource: order. Permite asociar datos como "Número de despacho externo".
21. Page (Página)
Páginas de contenido estático.12
* Métodos: GET, POST, PUT, DELETE (alcance read_content/write_content).
* Estructura: id, title, content (HTML localizado), handle (URL slug).
22. Payment Option
Alternativas de pago en checkout.13
* Estructura: id, name, type (Enum), fields (campos requeridos en UI), checkout_js_url.
23. Payment Provider
Pasarelas de pago integradas.
* Métodos: GET, POST, PUT.
* Estructura: id, name, transparent_checkout (Boolean), rates_url, checkout_payment_options (Array).
24. Product (Producto)
Entidad principal del catálogo.
* Métodos: GET, POST, PUT, DELETE.
* Estructura: id, name, description, variants (Array), images (Array), categories (Array), requires_shipping (Boolean).5
25. Product Image
Imágenes de productos.
* Métodos: GET, POST, PUT, DELETE.
* Estructura: id, src (URL), position, product_id.5
26. Product Variant
Versiones de un producto (talla/color).5
* Métodos: GET, POST, PUT, DELETE.
* Estructura: id, price, promotional_price, stock, sku, weight, inventory_levels (Array por ubicación).5
27. Product Custom Fields / 28. Product Variant Custom Fields
Personalización de productos y variantes.
* Estructura: Sigue el estándar UUID con owner_resource definido como product o product_variant.5
29. Script
Inyección de JS en el storefront.
* Métodos: GET, POST, DELETE.
* Estructura: name, handle, location (store/checkout), event (onload/firstinteraction), script_file.
30. Shipping Carrier
Proveedores de logística.
* Métodos: GET, POST, PUT.
* Estructura: id, name, callback_url, types (ship/pickup).
31. Store (Tienda)
Configuración general.
* Métodos: GET.
* Estructura: id, name, email, logo, languages, main_currency, plan_name, country.
32. Transaction (Transacción)
Movimiento de dinero.
* Métodos: GET, POST.
* Estructura: id, payment_provider_id, status (pending, success, failure), amount (Object), events (Array de estados).
33. Webhook
Notificaciones de eventos.4
* Métodos: GET, POST, PUT, DELETE.
* Estructura: id, url (HTTPS), event (ej. order/paid, product/updated). Incluye obligatoriamente webhooks de privacidad (redact/data_request).4
Obras citadas
1. API Resources | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources
2. Billing | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/billing
3. Product | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/product
4. Category | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/category
5. Scripts | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/script
6. Cart | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/cart
7. Coupons | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/coupon
8. Webhook | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/webhook
9. Abandoned Checkout | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/abandoned-checkout
10. Order | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/order
11. Business Rules | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/business-rules
12. Authentication | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/authentication
13. Checkout | Nuvemshop API - GitHub Pages, fecha de acceso: enero 22, 2026, https://tiendanube.github.io/api-documentation/resources/checkout