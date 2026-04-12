Análisis Integral y Documentación Técnica de la Interfaz de Programación de Aplicaciones (API) de Tiendanube y Nuvemshop: Arquitectura de Versión 2025-03
La infraestructura tecnológica que sustenta a Tiendanube, conocida en el mercado brasileño como Nuvemshop, se fundamenta en una interfaz de programación de aplicaciones (API) robusta, diseñada bajo los principios de la arquitectura REST (Representational State Transfer).1 Esta plataforma permite una integración profunda para desarrolladores de aplicaciones, proveedores de pagos y sistemas de logística, garantizando que el flujo de datos entre la tienda y los servicios externos sea fluido, seguro y escalable. La versión actual, identificada bajo el marcador temporal 2025-03, establece un marco de trabajo estandarizado que utiliza JSON (JavaScript Object Notation) como el formato principal para la serialización de datos y el protocolo OAuth 2.0 para la gestión de autorizaciones.1
La comunicación con la API se realiza exclusivamente a través de conexiones seguras mediante SSL (Secure Sockets Layer), lo que subraya el compromiso de la plataforma con la integridad de los datos transaccionales y la información personal de los consumidores.1 Las direcciones base de la API se segmentan geográficamente para optimizar el rendimiento y cumplir con las regulaciones locales de cada mercado donde opera la compañía.
Fundamentos de Arquitectura y Comunicación de Red
El acceso a los recursos de la tienda se organiza mediante identificadores únicos de establecimiento y versiones específicas de la API, lo que facilita el mantenimiento de la retrocompatibilidad cuando se introducen cambios disruptivos en la estructura de los datos.1 La arquitectura está diseñada para no presentar elementos raíz en las respuestas JSON, utilizando la convención de nombres snake_case para las claves de los atributos.1
Estructura de Endpoints y Direccionamiento Regional
Las solicitudes deben dirigirse a las URLs base correspondientes al país de operación de la tienda, integrando siempre el identificador de la tienda y la versión del protocolo.
Región
	Dirección Base (Endpoint)
	Argentina y Resto de Latinoamérica
	https://api.tiendanube.com/2025-03/{store_id}
	Brasil (Nuvemshop)
	https://api.nuvemshop.com.br/2025-03/{store_id}
	Cualquier interacción con el sistema requiere el envío obligatorio de ciertos encabezados HTTP para validar la identidad de la aplicación y el tipo de contenido que se está procesando. El encabezado Content-Type debe establecerse como application/json; charset=utf-8 para todas las operaciones que involucren el envío de datos (POST y PUT).1 Asimismo, el encabezado User-Agent es un requisito sine qua non para el procesamiento de solicitudes; este debe contener el nombre de la aplicación y un enlace de contacto o dirección de correo electrónico, permitiendo al equipo de ingeniería de la plataforma identificar y contactar a los desarrolladores en caso de irregularidades en el tráfico.1
Gestión de Errores y Códigos de Respuesta
La API emplea códigos de estado HTTP convencionales para comunicar el resultado de las operaciones. El análisis detallado de estos códigos permite a los desarrolladores implementar lógicas de resiliencia y manejo de excepciones de manera eficiente.


Código HTTP
	Significado Técnico y Causa Común
	200 OK
	La solicitud fue procesada exitosamente y el cuerpo de la respuesta contiene los datos solicitados.3
	201 Created
	Se ha creado un nuevo recurso de manera exitosa.3
	400 Bad Request
	La solicitud contiene JSON inválido o carece del encabezado User-Agent.1
	401 Unauthorized
	El access_token proporcionado es inválido o ha expirado.4
	404 Not Found
	El recurso solicitado (tienda, producto, orden) no existe en el sistema.3
	415 Unsupported Media Type
	No se incluyó el encabezado Content-Type: application/json.1
	422 Unprocessable Entity
	Los campos enviados son sintácticamente correctos pero lógicamente inválidos (ej. falta un campo obligatorio).1
	429 Too Many Requests
	Se ha superado el límite de frecuencia permitido por el algoritmo Leaky Bucket.1
	5xx Server Error
	Problemas internos en la infraestructura de la plataforma; se recomienda implementar reintentos con retroceso exponencial.1
	Protocolos de Autenticación y Autorización mediante OAuth 2.0
La seguridad en la API de Tiendanube se gestiona a través del marco de trabajo OAuth 2.0, que permite a los propietarios de las tiendas conceder permisos específicos a aplicaciones de terceros sin compartir sus credenciales de acceso maestras.1 El proceso comienza con el registro del desarrollador en el Portal de Partners, donde se obtienen las credenciales de la aplicación (Client ID y Client Secret) necesarias para iniciar el flujo de autorización.1
El Ciclo de Vida del Access Token
Una vez que el comerciante instala la aplicación y autoriza los permisos solicitados, el sistema genera un código de autorización temporal. Este código debe ser intercambiado por un access_token persistente, el cual actúa como la llave maestra para todas las solicitudes subsiguientes en nombre de esa tienda específica.1 La plataforma exige que este token se incluya en el encabezado de autorización de cada petición: Authentication: bearer {ACCESS_TOKEN}.1
El modelo de permisos se organiza en "ámbitos" o scopes, los cuales determinan el nivel de acceso que la aplicación tiene sobre los recursos. Un diseño de aplicación robusto debe solicitar únicamente los permisos mínimos necesarios para su funcionamiento, siguiendo el principio de menor privilegio.2
Tipo de Scope
	Permiso de Lectura (read_)
	Permiso de Escritura (write_)
	Productos y Categorías
	Ver catálogo y existencias
	Crear, editar y eliminar ítems
	Órdenes y Pedidos
	Consultar transacciones y estados
	Modificar estados, notas y reembolsos
	Clientes
	Acceder a datos de contacto
	Gestionar cuentas de usuario
	Ubicaciones
	Listar depósitos y sucursales
	Modificar prioridades y niveles de stock
	Gobernanza de Tráfico y Control de Frecuencia (Rate Limiting)
Para preservar la estabilidad del ecosistema y evitar la degradación del servicio ante picos de tráfico imprevistos, la plataforma implementa un algoritmo de control de frecuencia conocido como Leaky Bucket (Cubo con Fugas).1 Este mecanismo permite manejar ráfagas de solicitudes de corta duración mientras mantiene un ritmo de procesamiento constante a largo plazo.
Mecánica del Algoritmo Leaky Bucket
El sistema define un "cubo" virtual con una capacidad máxima de 40 solicitudes (burst capacity). Las solicitudes se procesan y "gotean" fuera del cubo a una tasa constante de 2 solicitudes por segundo.1 Si una aplicación envía solicitudes más rápido de lo que el sistema puede procesarlas, el cubo comienza a llenarse. Una vez alcanzado el límite de 40 solicitudes en cola, cualquier petición adicional será rechazada con un error HTTP 429 hasta que haya espacio disponible nuevamente en el cubo.1
La API proporciona transparencia absoluta sobre el estado de consumo de la cuota mediante encabezados de respuesta específicos:
* x-rate-limit-limit: Indica la capacidad total del bucket (40 en la configuración estándar).1
* x-rate-limit-remaining: Informa cuántas solicitudes quedan disponibles antes de llenar el bucket.1
* x-rate-limit-reset: Indica el tiempo restante en milisegundos para que el bucket se vacíe por completo.1
Este diseño obliga a los desarrolladores a implementar colas de mensajes y lógicas de espera en sus integraciones, especialmente para procesos intensivos en datos como la sincronización masiva de inventarios o la importación histórica de pedidos.
Navegación de Datos y Estándares de Paginación
Dada la posibilidad de que una tienda gestione catálogos de hasta 100,000 productos, la recuperación eficiente de grandes conjuntos de datos es una prioridad arquitectónica.7 Por defecto, las solicitudes de lista (GET) retornan un máximo de 30 resultados por página.9 Los desarrolladores pueden ajustar este comportamiento utilizando los parámetros de consulta page y per_page.8
Para facilitar la iteración sobre grandes volúmenes de información, la API emplea el encabezado Link, siguiendo los estándares de navegación web modernos. Este encabezado contiene las URLs necesarias para acceder a las páginas relativas de los resultados.


Relación (rel)
	Descripción de la URL Proporcionada
	next
	Enlace directo a la página inmediata de resultados.1
	prev
	Enlace a la página anterior.1
	first
	Enlace a la primera página de la colección.1
	last
	Enlace a la última página disponible.1
	El uso de estos enlaces es preferible sobre la construcción manual de URLs de paginación, ya que garantiza que los parámetros de filtrado y búsqueda se mantengan consistentes durante toda la navegación del conjunto de datos.
Gestión del Catálogo: Productos, Variantes e Imágenes
El recurso de Producto (Product) es la piedra angular de cualquier integración de comercio electrónico. En la API de Tiendanube, un producto no es simplemente un ítem estático, sino una entidad compleja que agrupa descripciones multilingües, configuraciones logísticas y una estructura de variantes que permite representar múltiples opciones de un mismo artículo.7
Atributos y Propiedades del Recurso Producto
Cada producto posee un conjunto de metadatos diseñados tanto para la gestión administrativa como para la optimización en motores de búsqueda (SEO).


Atributo Técnico
	Tipo
	Descripción y Restricciones
	id
	Integer
	Identificador numérico único inmutable.9
	name
	Object
	Diccionario con los nombres en todos los idiomas de la tienda.9
	description
	Object
	Contenido HTML localizado para la descripción detallada.9
	handle
	Object
	Slugs de URL generados automáticamente para cada idioma.9
	variants
	Array
	Colección de objetos Product Variant (máximo 1,000 por producto).7
	categories
	Array
	Lista de IDs de categorías asociadas.9
	published
	Boolean
	Indica si el producto es visible para los consumidores finales.9
	requires_shipping
	Boolean
	Define si el producto es físico (true) o digital/servicio (false).9
	seo_title
	String
	Título optimizado para buscadores (límite de 70 caracteres).9
	seo_description
	String
	Meta descripción para SEO (límite de 320 caracteres).9
	La plataforma impone límites específicos para garantizar la calidad del contenido: un producto puede tener un máximo de 3 atributos (ej. Talla, Color, Material) que sirven como ejes para la generación de variantes.7
Dinámica de las Variantes de Producto y el Nuevo Modelo de Multi-Inventario
El recurso Product Variant ha experimentado una evolución significativa con la introducción del soporte para múltiples ubicaciones físicas (Multi-Inventory). En el modelo heredado, el stock era un atributo directo de la variante (variant.stock). Sin embargo, en la arquitectura actual, el stock se descentraliza mediante el objeto inventory_levels.11
Cada nivel de inventario vincula una cantidad disponible con un location_id específico. Este cambio permite a las tiendas gestionar existencias en depósitos independientes, tiendas físicas y centros de distribución de manera simultánea. Para mantener la compatibilidad con integraciones antiguas, si una aplicación envía el campo stock de manera tradicional, el sistema asume que la actualización corresponde a la ubicación definida como predeterminada en la configuración de la tienda.11
Las variantes también capturan dimensiones críticas para el cálculo de costos de envío:
* weight: Peso del ítem en kilogramos (kg).7
* width, height, depth: Dimensiones físicas en centímetros (cm).7
* price: Precio base de la variante; si se establece en null, el sistema deshabilita el carrito y lo reemplaza por un botón de contacto.7
* promotional_price: Precio de oferta que se muestra tachado junto al precio original en el escaparate.7
Multimedia y Gestión Avanzada de Imágenes
Las imágenes de producto (Product Image) son fundamentales para la conversión en el comercio electrónico. La API permite gestionar hasta 250 imágenes por producto, con un peso máximo por archivo de 10MB.7 Los formatos soportados incluyen.gif,.jpg,.png y.webp.7
Una característica potente de la infraestructura de entrega de contenido (CDN) de la plataforma es la generación dinámica de tamaños de imagen. Al manipular la URL base devuelta por el atributo src, los desarrolladores pueden solicitar dimensiones optimizadas para diferentes interfaces.


Sufijo de Tamaño
	Aplicación Sugerida
	50px
	Miniaturas de carrito y notificaciones.7
	100px
	Vistas de lista pequeñas.7
	240px
	Grillas de productos en dispositivos móviles.7
	480px
	Vistas de producto en tabletas.7
	1024px
	Tamaño estándar para zoom y detalles (formato JPEG garantizado).7
	Es fundamental destacar que si un archivo se carga originalmente en formato WEBP, al solicitar la versión de 1024px, la CDN realizará una conversión automática a JPEG para asegurar que la imagen sea visible en navegadores que no soportan formatos modernos, priorizando la accesibilidad sobre el ahorro de ancho de banda en resoluciones altas.7
Organización del Catálogo mediante Categorías
Las categorías (Category) actúan como la estructura taxonómica de la tienda. Los dueños de las tiendas utilizan estas entidades para agrupar productos similares y mejorar la navegabilidad del sitio.7
Jerarquía y Propiedades de las Categorías
A diferencia de otros sistemas donde la relación es bidireccional, en Tiendanube la asignación de categorías es una propiedad del producto. No obstante, el recurso de categoría permite definir jerarquías complejas de padre e hijo.


Atributo
	Descripción Técnica
	id
	Identificador único de la categoría.7
	name
	Nombre localizado en los idiomas de la tienda.7
	parent
	ID de la categoría de nivel superior; null si es una categoría raíz.7
	subcategories
	Arreglo de solo lectura con los IDs de las categorías descendientes inmediatas.7
	description
	Texto HTML explicativo (límite de 65,535 caracteres).7
	google_shopping_category
	Mapeo con la taxonomía oficial de Google para campañas de anuncios.7
	Una limitación técnica importante es que una tienda puede tener un máximo de 1,000 categorías. Superar este límite resultará en un error 422 Unprocessable Entity al intentar crear nuevos recursos.7 Además, para convertir una categoría en subcategoría, el desarrollador debe actualizar el atributo parent de la categoría hija, ya que el arreglo subcategories de la categoría padre no es modificable directamente a través de la API.7
Extensibilidad mediante Campos Personalizados (Custom Fields)
Para escenarios donde los atributos estándar de la plataforma no son suficientes para cubrir las necesidades de un negocio específico, la API ofrece el sistema de Campos Personalizados. Estos permiten expandir el modelo de datos de productos, variantes de productos y órdenes con campos únicos y estructurados.12
Tipología y Control de los Custom Fields
Los campos personalizados están diseñados para ser creados por aplicaciones y gestionados programáticamente. Poseen tipos de datos definidos que aseguran la integridad de la información almacenada.
* text: Campo de texto libre.
* text_list: Selección de valores predefinidos (ideal para atributos fijos como "Tipo de Tela" o "Certificación").
* numeric: Valores numéricos.
* date: Fechas estandarizadas.


Propiedad del Campo
	Descripción
	id
	UUID v4 asignado globalmente.12
	owner_resource
	Define a qué entidad pertenece: product, product_variant o order.12
	read_only
	Si es true, el comerciante solo puede ver el valor en el panel de control, pero no editarlo.12
	values
	Para tipos text_list, contiene las opciones permitidas (máximo 250 caracteres por opción).12
	Una distinción técnica crítica es que únicamente los campos asociados a las variantes de productos (Product Variant Custom Fields) pueden ser habilitados por el comerciante como filtros en el escaparate de la tienda.12 Esto permite a las aplicaciones de nicho (ej. repuestos de autos o moda técnica) implementar buscadores avanzados basados en datos personalizados.
La asociación de estos campos con un recurso específico se realiza mediante el método PUT en el endpoint de valores correspondiente (ej. /orders/{id}/custom-fields/values). Para eliminar una asociación existente, se debe enviar el ID del campo con un valor null.12

El Ecosistema de Ventas: Carritos, Órdenes y Reembolsos
El flujo transaccional en Tiendanube es una secuencia de estados que transforman la intención de compra de un usuario en un registro financiero y logístico firme. La API proporciona visibilidad y control sobre cada etapa de este ciclo de vida.
Manipulación de Carritos de Compra
El recurso de Carrito (Cart) representa la etapa inicial donde el usuario selecciona productos. Las aplicaciones pueden interactuar con carritos activos para realizar tareas de recuperación de ventas o personalización de precios.7 Sin embargo, existen restricciones de accesibilidad: una vez que el carrito inicia el proceso de checkout o se convierte en una orden, deja de ser accesible a través de los endpoints de /carts.7
Las operaciones permitidas incluyen la recuperación del estado del carrito mediante GET /carts/{id}, la eliminación de ítems específicos (DELETE /carts/{id}/line-items/{id}) y la desvinculación de cupones de descuento (DELETE /carts/{id}/coupons/{id}).7
Ciclo de Vida de la Orden (Order)
Una Orden se crea cuando el consumidor completa exitosamente el proceso de pago o cuando una aplicación externa la genera programáticamente. El objeto Order es uno de los más densos de la API, consolidando información de clientes, productos, finanzas y logística.7
Atributos financieros clave del pedido:
* subtotal: Valor de los productos antes de envío y descuentos.7
* total: Valor final cobrado al cliente.7
* total_usd: Equivalente en dólares estadounidenses para fines de reporte global.7
* currency: Código ISO 4217 de la moneda de la transacción.7
El estado de un pedido se rastrea mediante tres ejes independientes:
1. status: El estado general del documento (open, closed, cancelled).7
2. payment_status: La situación financiera (authorized, pending, paid, refunded, voided).7
3. shipping_status: El progreso logístico (unpacked, shipped, delivered, partially_fulfilled).7
Pedidos Borrador (Draft Orders)
Los Pedidos Borrador permiten a los comerciantes actuar como agentes de venta, creando órdenes para sus clientes desde canales externos como WhatsApp o venta telefónica.7 A diferencia de una orden estándar, un Draft Order permite capturar la intención de compra y enviarla al cliente para que este complete el pago, o bien confirmarla manualmente desde el panel administrativo si el pago se recibió por medios informales.7
Órdenes de Cumplimiento (Fulfillment Orders)
Como parte de la modernización de la arquitectura logística, la plataforma ha introducido la entidad Fulfillment Order. Este recurso resuelve la problemática de los pedidos que requieren múltiples envíos (ej. productos que salen de diferentes depósitos o artículos con tiempos de preparación distintos).7
Una orden puede estar asociada a múltiples Fulfillment Orders, cada uno con su propio código de seguimiento y estado de entrega. Esto mejora drásticamente la transparencia para el consumidor final, quien puede rastrear cada paquete de su compra de forma independiente.7


Estado de Fulfillment
	Significado para el Consumidor
	dispatched
	El paquete ha sido entregado al correo o logística propia.7
	received_by_post_office
	El transportista ha procesado el ingreso del paquete.7
	in_transit
	El paquete se encuentra viajando hacia el destino.7
	ready_for_pickup
	Disponible para retiro en sucursal o punto de entrega.7
	delivered
	Entrega confirmada exitosamente.7
	Gestión de Ubicaciones y Control de Stock Geográfico
El recurso Ubicación (Location) es la representación digital de un punto físico donde reside la mercadería. La API permite gestionar una red de ubicaciones, lo cual es fundamental para estrategias de Ship-from-Store o gestión de múltiples centros de distribución.7
Priorización y Lógica de Asignación de Stock
Cada ubicación tiene una propiedad priority. Durante el proceso de checkout, el sistema evalúa la disponibilidad de los productos en las diferentes ubicaciones siguiendo el orden de prioridad definido por el comerciante (los valores numéricos más bajos tienen mayor prioridad).7
Para las aplicaciones que gestionan inventarios, es vital utilizar los endpoints específicos de niveles de stock por ubicación:
* GET /locations/{id}/inventory-levels: Devuelve las existencias de todos los productos en una ubicación específica, con soporte para filtrado por variant_id.7
* PATCH /locations/priorities: Permite reorganizar la jerarquía de despacho de toda la tienda en una sola operación masiva.7
Es importante notar que una ubicación no puede ser eliminada si tiene niveles de inventario asignados (stock mayor a cero en cualquier variante) o si está marcada como la ubicación predeterminada de la tienda.7
Herramientas Promocionales: Cupones y Descuentos
La API ofrece dos mecanismos para la aplicación de beneficios económicos: los Cupones (Coupons), que requieren una acción explícita del usuario, y la API de Descuentos (Discounts), que permite aplicar reglas automáticas basadas en la lógica de aplicaciones externas.7
Tipología de Cupones de Descuento
Existen tres categorías fundamentales de cupones, cada una con un impacto financiero distinto en el carrito de compras.
1. Porcentual: Reduce el total del carrito en un porcentaje definido (ej. 15% de descuento).7
2. Valor Absoluto: Descuenta un monto fijo de la moneda local (ej. $500 de descuento).7
3. Envío Gratuito: Elimina el costo logístico sin alterar el valor de los productos.7
Los cupones pueden estar restringidos por fecha de inicio y fin, monto mínimo de compra, categorías específicas o productos seleccionados. Además, se puede configurar si un cupón es combinable con otras promociones activas en la tienda.7
La API de Descuentos y el Ciclo de Promociones
La API de Descuentos es una herramienta avanzada para socios que desarrollan motores de promociones complejos (ej. "Lleva 3 y paga 2"). A diferencia de los cupones, los descuentos operan mediante un flujo de callback en tiempo real.7
Cuando ocurre una acción en el carrito (agregar ítem, cambiar cantidad), la plataforma envía el payload completo del carrito a la URL de callback de la aplicación. La aplicación debe procesar la lógica y responder con "comandos" para aplicar o remover descuentos.17 Este sistema divide las promociones en dos niveles o Tiers:
* Line Item: Descuentos aplicados a un producto específico dentro del carrito.17
* Cross Items: Descuentos globales que afectan al total de la compra una vez calculados los precios individuales.17
Debido a que este proceso es crítico para la experiencia de compra, la plataforma impone un tiempo de respuesta estricto de 800 milisegundos. Si la aplicación no responde en ese tiempo o devuelve un formato inválido, el sistema elimina automáticamente todos los descuentos aplicados anteriormente por esa aplicación para proteger al comerciante de errores de cálculo o pérdidas financieras imprevistas.7
Facturación y Modelos de Negocio para Aplicaciones (Billing)
Para los socios que ofrecen servicios bajo un modelo de suscripción o cargos variables, la sección de Facturación (Billing) de la API proporciona la infraestructura necesaria para gestionar cobros a través de la factura de servicio de la plataforma.5
Entidades del Modelo de Facturación


Entidad
	Propósito Técnico
	Plan
	Define niveles de servicio, límites de uso y precios fijos.5
	Subscription
	Vincula al comerciante con un servicio; genera cargos periódicos automáticamente.5
	Charge
	Permite crear cobros extraordinarios por única vez (ej. exceso de uso, servicios premium).7
	Un aspecto sofisticado del sistema de facturación es el alineamiento automático de los ciclos de cobro. La plataforma intenta alinear todos los cargos de aplicaciones al día 16 de cada mes. Esto implica que, dependiendo de la fecha de instalación, el primer cargo puede ser prorrateado para cubrir el periodo hasta el próximo día 16, simplificando la administración financiera para el comerciante al unificar los vencimientos de todas sus herramientas digitales.7
Personalización del Escaparate: Scripts y Contexto Global
La API de Scripts permite a las aplicaciones extender la funcionalidad visual de la tienda inyectando archivos JavaScript directamente en las páginas de navegación del cliente.7
El Ciclo de Vida del Script
Los scripts no se inyectan como archivos estáticos simples, sino que forman parte de un sistema de gestión de versiones en el Portal de Partners. Esto permite a los desarrolladores probar nuevas funcionalidades en tiendas de prueba antes de realizar un despliegue masivo a producción.18
Existen dos tipos de carga para los scripts:
1. onfirstinteraction (Predeterminado): El script se carga solo cuando el usuario realiza una acción (scroll, clic, touch). Es ideal para widgets de chat o popups de intención de salida, ya que no penaliza el tiempo de carga inicial de la página.7
2. onload: El script se ejecuta inmediatamente. Este método requiere una revisión de rendimiento y aprobación previa por parte del equipo técnico de la plataforma para asegurar que no afecte negativamente el SEO de la tienda.7
Interacción con el Objeto Contextual LS
Los scripts inyectados tienen acceso a un objeto global de JavaScript llamado LS, que actúa como el puente de datos entre el servidor y el cliente.


Página de Navegación
	Datos Disponibles en el Objeto LS
	Todas las páginas
	store.id, cart.subtotal, cart.items, lang, currency, customer.id.18
	Página de Producto
	product.id, product.name, product.tags, variants (JSON completo).18
	Página de Categoría
	category.id, category.name.18
	Página de Agradecimiento
	order.id, order.total, order.coupon, order.gateway.18
	Este objeto elimina la necesidad de realizar llamadas adicionales a la API desde el cliente para obtener información básica de la sesión, mejorando drásticamente el rendimiento de las extensiones front-end.
Interfaz de Pagos y el Checkout SDK
Para los desarrolladores de pasarelas de pago, la plataforma ofrece dos niveles de integración: la API del Proveedor de Pagos (Back-end) y el Checkout SDK (Front-end).7
Estrategias de Integración de Pagos
1. Checkout Transparente: El consumidor ingresa los datos de su tarjeta sin abandonar el dominio de la tienda. El desarrollador debe alojar un archivo JavaScript en una CDN de alta disponibilidad y configurar su URL en el atributo checkout_js_url del proveedor de pagos.7
2. Redirección (External Payment): El consumidor es enviado a una página externa para completar el pago. La API gestiona la comunicación back-to-back para recuperar la URL de destino.7
3. Modal: La interfaz del proveedor se carga dentro de un iframe o lightbox, manteniendo la percepción de que el usuario permanece en la tienda.7
Capacidades del Checkout SDK
El Checkout SDK proporciona métodos de alto nivel para alterar el flujo de pago en tiempo real desde el navegador.
* window.SDKCheckout.hidePaymentOptions(['id_gateway']): Permite ocultar dinámicamente opciones de pago basadas en condiciones del carrito.7
* window.SDKCheckout.changePaymentBenefit({ id: 'id_gateway', value: '5% OFF' }): Modifica el texto de beneficio mostrado junto a la opción de pago.7
* window.SDKCheckout.hideInstallments({ id: 'id_gateway', value: 12 }): Elimina opciones de cuotas específicas de la lista de selección del usuario.7
Esta granularidad permite implementar lógicas complejas de riesgo o promociones bancarias específicas sin necesidad de modificar el código fuente del motor de checkout.
Integración Logística: Shipping Carriers y Circuit Breaker
La integración de servicios de transporte se gestiona a través del recurso Shipping Carrier. Para activar estos endpoints, los desarrolladores deben completar un proceso de homologación específico con el equipo de alianzas de la plataforma.7
Funcionamiento de los Callbacks de Tarifas
Cuando un consumidor ingresa su código postal en la tienda, la plataforma realiza una solicitud POST a la URL de callback del transportista. La respuesta debe ser un arreglo de opciones de envío, donde cada una incluya nombre, precio, moneda y tiempo estimado de entrega.7
Para proteger la experiencia del usuario ante transportistas inestables, el sistema implementa un Circuit Breaker (Disyuntor). Si un transportista falla en el 50% de sus solicitudes (o tarda más de 10 segundos) durante un periodo de 30 minutos (con al menos 500 solicitudes), la plataforma dejará de consultarlo automáticamente durante 5 minutos, evitando que la lentitud del servicio externo bloquee el proceso de compra de los clientes.7
Automatización y Notificaciones mediante Webhooks
Los Webhooks son el mecanismo principal para que las aplicaciones mantengan sus bases de datos sincronizadas con los eventos de la tienda de manera asincrónica y eficiente.7
Eventos y Seguridad de los Webhooks
La plataforma permite suscribirse a una amplia gama de eventos que cubren casi todos los cambios en el estado de la tienda.


Categoría
	Eventos Disponibles
	Aplicación
	uninstalled, suspended, resumed.10
	Productos
	created, updated, deleted.10
	Órdenes
	paid, packed, fulfilled, cancelled, edited, pending.10
	Datos
	domain/updated, subscription/updated, fulfillment/updated.10
	Para validar que la notificación proviene realmente de Tiendanube, cada solicitud incluye un encabezado de firma digital x-linkedstore-hmac-sha256. Los desarrolladores deben calcular el hash HMAC-SHA256 del cuerpo de la solicitud utilizando el secreto de su aplicación como clave y comparar el resultado con el encabezado recibido.7
Política de Reintentos e Idempotencia
Dada la naturaleza distribuida de la infraestructura, los webhooks pueden llegar fuera de orden o incluso duplicarse. Es responsabilidad del desarrollador implementar una lógica de idempotencia, tratando múltiples notificaciones con el mismo contenido como un único evento.7 Si el servidor del desarrollador no responde con un éxito (2XX) en 10 segundos, el sistema iniciará una secuencia de hasta 18 reintentos con retroceso exponencial a lo largo de 48 horas.7
Cumplimiento y Protección de Datos (LGPD/GDPR)
En cumplimiento con las leyes de protección de datos personales, como la LGPD en Brasil, la API proporciona webhooks obligatorios para la gestión de la privacidad de los consumidores.7
1. store/redact: Se activa cuando un comerciante desinstala una aplicación; la aplicación debe proceder a eliminar cualquier dato de la tienda de su base de datos.7
2. customers/redact: Se dispara cuando un consumidor solicita el borrado de sus datos (típicamente si no ha realizado compras en los últimos 6 meses).7
3. customers/data_request: Solicitud de acceso a los datos; la aplicación debe recopilar la información del cliente almacenada en sus sistemas y enviarla al comerciante para su entrega al interesado.7
Conclusiones y Mejores Prácticas de Desarrollo
La API de Tiendanube y Nuvemshop representa un sistema de alta madurez técnica que equilibra la flexibilidad para el desarrollador con la seguridad y estabilidad para el comerciante. Para construir integraciones exitosas, se recomienda:
* Respetar los límites de frecuencia: Implementar estrategias de "backoff" ante errores 429 y optimizar el uso del bucket.1
* Optimizar el front-end: Utilizar el objeto LS y el Checkout SDK para evitar llamadas redundantes a la API desde el navegador del cliente.18
* Manejar la asincronía: No depender del orden de llegada de los webhooks y utilizar el campo updated_at para determinar la versión más reciente de un recurso.7
* Diseñar para el Multi-Inventario: Abandonar el uso del campo stock simple y adoptar la estructura de inventory_levels para asegurar la compatibilidad a largo plazo.11
Este reporte constituye una guía técnica exhaustiva para la implementación de soluciones robustas dentro del ecosistema de comercio electrónico líder en América Latina, proporcionando los fundamentos necesarios para el desarrollo de aplicaciones escalables y seguras.
