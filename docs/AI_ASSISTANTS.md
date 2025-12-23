# Guía de Asistentes de IA (Cursor y Codex)

Esta guía explica cómo configurar y optimizar el uso de asistentes de IA (Cursor y Codex) en este proyecto.

## 📋 Archivos de Configuración

### Cursor

- **`.cursorrules`** - Reglas del proyecto (raíz) - **Principal**
- **`.cursorignore`** - Archivos a ignorar
- **`AGENTS.md`** - Contexto adicional (complementa .cursorrules)

### Codex

- **`AGENTS.md`** - Instrucciones principales (raíz)
- **`.cursorrules`** - También leído por Codex

## 🎯 Cursor

### Configuración

Cursor lee automáticamente `.cursorrules` en la raíz del proyecto.

### Características Principales

1. **Tab**: Autocompletado inteligente
2. **Agent**: Modifica código en múltiples archivos
3. **Ctrl+K**: Edición inline con lenguaje natural
4. **Chat (Ctrl+L)**: Conversación con IA sobre el código
5. **Composer (Ctrl+Shift+L)**: Editar múltiples archivos

### Mejores Prácticas

#### 1. Reglas Claras en `.cursorrules`

El archivo `.cursorrules` debe incluir:

- Contexto del proyecto
- Arquitectura y estructura
- Convenciones de código
- Patrones de diseño
- Reglas específicas (qué hacer/nunca hacer)

#### 2. Instrucciones Específicas

**❌ Malo:**

```
Agregar endpoint para usuarios
```

**✅ Bueno:**

```
Crear feature 'users' en custom/features/users/ con:
- routes.py: GET /api/v1/users y POST /api/v1/users
- schemas.py: UserCreate, UserResponse con validación
- service.py: UserService con lógica de negocio
- repository.py: UserRepository extendiendo BaseRepository
- Agregar tests en tests/integration/api/test_users_routes.py
- Seguir estructura de features/users como referencia
```

#### 3. Usar Contexto

- Mencionar archivos relevantes
- Referenciar código existente similar
- Especificar patrones a seguir

### Comandos Útiles

- `Ctrl+K`: Editar código seleccionado
- `Ctrl+L`: Abrir chat con IA
- `Tab`: Aceptar sugerencia de autocompletado
- `Ctrl+Shift+L`: Composer (editar múltiples archivos)
- `Ctrl+I`: Inline edit

## 🔧 Codex (OpenAI)

### Configuración

Codex está disponible en ChatGPT Plus/Pro y se integra con:

- Terminal (CLI)
- VS Code
- Cursor
- Windsurf

### Instalación CLI

```bash
npm i -g @openai/codex
```

### Mejores Prácticas

#### 1. Instrucciones Claras y Específicas

**❌ Malo:**

```
Agregar función para usuarios
```

**✅ Bueno:**

```
Crear función create_user en app/core/features/users/service.py
que:
- Reciba UserCreate como parámetro
- Valide email único usando UserRepository.get_by_email()
- Cree usuario en DB usando UserRepository.create()
- Retorne User
- Incluir manejo de errores HTTPException si email existe
- Seguir patrón de N8NFeatureService como referencia
```

#### 2. Proporcionar Contexto

- Estructura del proyecto
- Patrones usados
- Convenciones de código
- Ejemplos similares

#### 3. Verificación

Codex ejecuta en entorno aislado. Siempre:

- Revisar cambios propuestos
- Verificar tests
- Validar que sigue convenciones
- Ejecutar linters

## 📁 Archivos de Contexto

### Para Cursor

1. **`.cursorrules`** - Reglas principales del proyecto (raíz)
2. **`AGENTS.md`** - Contexto adicional y ejemplos
3. **`.cursorignore`** - Archivos a ignorar
4. **`README.md`** - Documentación principal
5. **`docs/ARCHITECTURE.md`** - Arquitectura detallada
6. **`docs/business/`** - **Documentación de negocio (diagramas, diseños, requisitos)**

### Para Codex

1. **`AGENTS.md`** - Instrucciones principales (raíz)
2. **`.cursorrules`** - También leído por Codex
3. **Documentación del proyecto** - README y docs/
4. **Estructura de archivos** - Organización clara
5. **Ejemplos de código** - Patrones a seguir
6. **`docs/business/`** - **Documentación de negocio**

## 🎨 Estrategias de Uso

### 1. Desarrollo Incremental

```
1. Describir feature completo en lenguaje natural
2. IA genera estructura base
3. Revisar y ajustar
4. Agregar tests
5. Refinar implementación
6. Iterar hasta completar
```

### 2. Refactoring

```
1. Explicar qué se quiere cambiar y por qué
2. Mencionar archivos afectados
3. Especificar patrones a seguir
4. Revisar cambios propuestos
5. Verificar tests siguen pasando
```

### 3. Debugging

```
1. Describir el problema específico
2. Mencionar archivos relevantes
3. Incluir logs/errores completos
4. Pedir solución siguiendo patrones del proyecto
5. Verificar solución propuesta
```

### 4. Agregar Tests

```
1. Describir qué se quiere testear
2. Mencionar feature/archivo
3. Especificar casos de prueba
4. Referenciar tests similares existentes
5. Verificar coverage
```

## ✅ Ejemplos de Instrucciones Efectivas

### Crear Feature Completo

```
Crear feature 'checkout' en custom/features/checkout/ según:

DOCUMENTACIÓN DE NEGOCIO:
- Requisitos: docs/business/features/checkout/requirements/checkout-requirements.md
- Flujo: docs/business/features/checkout/diagrams/checkout-flow.png
- Diseño: docs/business/features/checkout/designs/checkout-figma.md
- Especificación API: docs/business/features/checkout/specs/checkout-api-spec.md

IMPLEMENTACIÓN:
1. Modelo Order (models.py) - Según especificación API
2. Schemas (schemas.py) - CheckoutCreate, OrderResponse
3. Repository (repository.py) - OrderRepository extendiendo BaseRepository
4. Service (service.py) - CheckoutService con métodos según requisitos
5. Routes (routes.py) - POST /api/v1/checkout según especificación
6. Tests - Validar que cumple todos los requisitos

Seguir estructura de features/users como referencia técnica.
Implementar según diagrama de flujo.
Seguir diseño UI especificado.
```

## ❌ Errores Comunes

### 1. Instrucciones Vagas

**❌ Malo:**

```
Hacer lo de usuarios
Agregar algo para orders
```

**✅ Bueno:**

```
Crear feature users con CRUD completo siguiendo estructura de features/n8n
```

### 2. Falta de Contexto

**❌ Malo:**

```
Crear función para procesar datos
```

**✅ Bueno:**

```
Crear función process_user_data en UserService que:
- Reciba UserData
- Valide formato
- Transforme según reglas de negocio
- Retorne UserProcessed
- Seguir patrón de process_order_data como referencia
```

### 3. No Especificar Ubicación

**❌ Malo:**

```
Agregar endpoint para login
```

**✅ Bueno:**

```
Agregar endpoint POST /api/v1/auth/login en custom/features/auth/routes.py
```

## 🔍 Troubleshooting

### Cursor no sigue las reglas

1. Verificar que `.cursorrules` está en la raíz
2. Reiniciar Cursor
3. Verificar sintaxis del archivo (Markdown válido)
4. Ser más específico en las reglas
5. Usar ejemplos concretos

### Codex no entiende el proyecto

1. Mejorar documentación del proyecto
2. Proporcionar ejemplos de código existente
3. Ser más específico en instrucciones
4. Dividir tareas en pasos más pequeños
5. Incluir estructura de archivos en prompt

### Sugerencias de baja calidad

1. Mejorar contexto en `.cursorrules`
2. Agregar más ejemplos de código
3. Ser más específico en comentarios
4. Verificar que el código existente sigue buenas prácticas
5. Actualizar documentación

## 📋 Documentación de Negocio

### ¿Es Buena Práctica Incluir Documentación Visual?

**✅ SÍ, es excelente práctica** cuando se organiza correctamente.

### Ventajas

1. **Contexto Completo**: Los agentes entienden mejor el propósito
2. **Consistencia**: Asegura implementación según diseños
3. **Trazabilidad**: Conecta código con requisitos
4. **Validación**: Permite verificar cumplimiento de especificaciones

### Estructura Recomendada

```
docs/business/
├── requirements/      # Requisitos funcionales (Markdown)
├── diagrams/          # Diagramas (PNG, SVG)
├── designs/           # Diseños (Figma, mockups, wireframes)
├── specs/             # Especificaciones técnicas (Markdown)
└── assets/            # Recursos (PDFs, exports)
```

### Mejores Prácticas

1. **Organizar por feature**: Agrupar documentación relacionada
2. **Nombres descriptivos**: Usar nombres claros
3. **Descripciones en texto**: Siempre incluir descripción de imágenes
4. **Referenciar en código**: Incluir referencias a documentación
5. **Mantener actualizado**: Sincronizar con código

Ver `docs/business/BEST_PRACTICES.md` para guía completa.

## 📚 Recursos

- [Cursor Documentation](https://docs.cursor.com)
- [OpenAI Codex](https://openai.com/codex)

## 🎓 Tips Avanzados

### 1. Usar Comentarios Estratégicos

```python
# TODO: Implementar validación de email único
# FIXME: Manejar caso cuando user no existe
# NOTE: Este método se usa en background tasks
```

### 2. Documentar Decisiones

```python
def process_order(order: Order):
    # Usamos transaction aquí para asegurar atomicidad
    # de la operación de actualización de inventario
    with db.begin():
        # ...
```

### 3. Referenciar Código Existente

```python
# Similar a UserService.create_user pero con validaciones adicionales
def create_premium_user(user_data: PremiumUserCreate) -> User:
    # ...
```

### 4. Usar Type Hints Complejos

```python
from typing import List, Dict, Optional, Union

def process_orders(
    orders: List[Order],
    filters: Optional[Dict[str, Union[str, int]]] = None
) -> List[OrderResponse]:
    # ...
```
