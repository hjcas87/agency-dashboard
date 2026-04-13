# User Story — Gestión de Clientes

## Descripción
Como usuario de la plataforma, necesito poder gestionar mis clientes (crear, ver, editar y eliminar) para mantener un registro organizado de las empresas y personas con las que trabajo.

## Historias de Usuario

### HU-1: Ver lista de clientes
**Como** usuario autenticado  
**Quiero** ver una tabla con todos mis clientes  
**Para** tener una vista general de quiénes son

**Criterios de aceptación:**
- La tabla muestra: Nombre, Empresa (opcional), Email, Teléfono
- La tabla soporta ordenamiento por columna
- La tabla soporta paginación
- La tabla soporta filtrado/búsqueda
- Si no hay clientes, se muestra un estado vacío con mensaje apropiado
- La página se accede desde el sidebar → "Clientes"

### HU-2: Crear un nuevo cliente
**Como** usuario autenticado  
**Quiero** crear un nuevo cliente con nombre, empresa, email y teléfono  
**Para** registrar un nuevo contacto en el sistema

**Criterios de aceptación:**
- El botón "Crear Cliente" está visible arriba a la derecha de la tabla
- El formulario de creación tiene campos: Nombre (requerido), Empresa (opcional), Email (requerido), Teléfono (opcional)
- Se valida que el email sea válido
- Se muestra un toast de éxito al crear
- Se redirige a la lista de clientes tras crear

### HU-3: Editar un cliente existente
**Como** usuario autenticado  
**Quiero** editar los datos de un cliente  
**Para** corregir o actualizar su información

**Criterios de aceptación:**
- Cada fila de la tabla tiene un botón de edición
- El formulario de edición se abre en la misma pantalla de creación (ruta `/clientes/nuevo` y `/clientes/{id}/editar`)
- Los campos se precargan con los datos existentes
- Se valida que el email sea válido
- Se muestra un toast de éxito al editar
- Se redirige a la lista de clientes tras editar

### HU-4: Eliminar un cliente
**Como** usuario autenticado  
**Quiero** eliminar un cliente  
**Para** quitar registros que ya no necesito

**Criterios de aceptación:**
- Cada fila de la tabla tiene un botón de eliminar
- Se pide confirmación antes de eliminar (AlertDialog)
- Se muestra un toast de éxito al eliminar
- La fila se elimina de la tabla sin recargar

## Estructura de Datos

### Cliente
| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| id | UUID | Auto | Identificador único |
| name | string | Sí | Nombre del cliente |
| company | string \| null | No | Empresa del cliente |
| email | string | Sí | Email del cliente |
| phone | string \| null | No | Teléfono del cliente |
| created_at | datetime | Auto | Fecha de creación |
| updated_at | datetime | Auto | Fecha de última modificación |

## URLs

| Ruta | Descripción |
|---|---|
| `/clientes` | Lista de clientes (tabla) |
| `/clientes/nuevo` | Formulario de creación |
| `/clientes/{id}/editar` | Formulario de edición |

> Nota: Las URLs del sidebar se manejan en inglés internamente (`/clients`) pero los labels visibles están en español.

## API Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/clients` | Listar todos los clientes |
| POST | `/api/v1/clients` | Crear un nuevo cliente |
| GET | `/api/v1/clients/{id}` | Obtener un cliente por ID |
| PUT | `/api/v1/clients/{id}` | Actualizar un cliente |
| DELETE | `/api/v1/clients/{id}` | Eliminar un cliente |

## Mensajes de Usuario (español)

- Creación exitosa: "Cliente creado correctamente"
- Edición exitosa: "Cliente actualizado correctamente"
- Eliminación exitosa: "Cliente eliminado correctamente"
- Error al crear: "No se pudo crear el cliente. Intentalo de nuevo."
- Error al editar: "No se pudo actualizar el cliente. Intentalo de nuevo."
- Error al eliminar: "No se pudo eliminar el cliente. Intentalo de nuevo."
- Confirmación de eliminación: "¿Estás seguro de que deseas eliminar este cliente?"
