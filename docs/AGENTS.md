# Instrucciones para Agentes de IA

Este archivo proporciona instrucciones específicas para agentes de IA que trabajan en este proyecto.

> **Nota**: Cursor también lee `.cursorrules` en la raíz del proyecto. Este archivo complementa esas reglas con contexto adicional.

## Estructura del Proyecto

- **Código fuente Backend**: `backend/app/`
- **Código fuente Frontend**: `frontend/app/`
- **Tests**: `backend/tests/`
- **Documentación**: `docs/`

## Comandos de Prueba

```bash
# Ejecutar tests
cd backend && uv run pytest

# Solo unit tests
uv run pytest -m unit

# Solo integration tests
uv run pytest -m integration

# Con coverage
uv run pytest --cov=app --cov-report=html
```

## Prácticas Recomendadas

- Escribir documentación para cada función pública
- Seguir convenciones de código (ver `.cursorrules`)
- Mantener cobertura de tests > 80%
- Usar type hints siempre
- Documentar decisiones arquitectónicas

## Reglas Críticas

### Modelos SQLAlchemy y Base de Datos

**REGLA CRÍTICA**: Los modelos SQLAlchemy DEBEN estar siempre sincronizados con las tablas de la base de datos. NO debe haber diferencias entre los campos definidos en los modelos y las columnas en las tablas.

#### Al Modificar Modelos:

1. **SIEMPRE crear una migración de Alembic**:
   ```bash
   cd backend
   uv run alembic revision --autogenerate -m "Descripción del cambio"
   uv run alembic upgrade head
   ```

2. **NUNCA modificar modelos sin actualizar la base de datos** mediante migraciones

3. **SIEMPRE verificar** que los campos del modelo coinciden con las columnas de la tabla después de cualquier cambio

4. **SIEMPRE ejecutar migraciones** después de modificarlas:
   ```bash
   uv run alembic upgrade head
   ```

5. **Si hay discrepancias**, corregirlas inmediatamente mediante:
   - Crear una migración para agregar/eliminar/modificar columnas faltantes
   - O ajustar el modelo si la estructura de la tabla es la correcta

6. **Verificar sincronización** antes de commitear cambios

#### Errores Comunes a Evitar:

- ❌ Modificar un modelo agregando un campo sin crear migración
- ❌ Tener campos en el modelo que no existen en la tabla
- ❌ Tener columnas en la tabla que no están en el modelo
- ❌ Modificar la base de datos manualmente sin crear migraciones
- ❌ Ignorar errores de SQLAlchemy sobre columnas faltantes o inexistentes

#### Ejemplo Correcto:

```python
# 1. Modificar modelo
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)  # ← Nuevo campo

# 2. Crear migración
# uv run alembic revision --autogenerate -m "Add phone to users"

# 3. Ejecutar migración
# uv run alembic upgrade head

# 4. Verificar que funciona
# Probar que el modelo puede hacer queries correctamente
```

#### Verificación:

Después de cualquier cambio en modelos, verificar:
1. Que las migraciones se ejecutan sin errores
2. Que las queries al modelo funcionan correctamente
3. Que no hay errores de SQLAlchemy sobre columnas faltantes
4. Que el modelo puede crear/leer/actualizar/eliminar registros correctamente

### Flujo de Trabajo con Git: Core vs Custom

**IMPORTANTE**: Los cambios en código `core/` deben seguir un flujo específico de git.

#### Principio Fundamental

- **Cambios en `core/`** → Deben commitearse en `main` (o `dev` si existe)
- **Cambios en `custom/`** → Se commitean directamente en la rama de trabajo (ej: `crm-prego`)
- **Después de commitear cambios en `core/` a `main`** → Actualizar la rama de trabajo desde `main`

#### Proceso cuando Modificas Core

Si necesitas hacer cambios en código `core/` (por ejemplo: `backend/app/core/`, `frontend/components/core/`, `frontend/app/actions/core/`):

1. **Identificar los cambios de core**:
   ```bash
   git status
   # Identificar archivos en core/ que están modificados
   ```

2. **Separar cambios de core de cambios de custom**:
   ```bash
   # Stash cambios de custom/frontend si hay mezclados
   git stash push -m "Cambios custom - restaurar después"
   
   # Agregar solo cambios de core
   git add backend/app/core/ frontend/components/core/ frontend/app/actions/core/
   ```

3. **Commitear cambios de core en la rama actual** (temporal):
   ```bash
   git commit -m "refactor(core): descripción de cambios en core"
   ```

4. **Cambiar a `main` y traer los cambios**:
   ```bash
   git checkout main
   git cherry-pick <commit-hash>
   # O usar: git merge <rama-de-trabajo> (solo cambios de core)
   ```

5. **Volver a la rama de trabajo y actualizar desde `main`**:
   ```bash
   git checkout <rama-de-trabajo>  # ej: crm-prego
   git merge main
   ```

6. **Restaurar cambios de custom si había stash**:
   ```bash
   git stash pop
   ```

#### Ejemplo Completo

```bash
# Estás en rama crm-prego con cambios mezclados
git status  # Muestra cambios en core/ y custom/

# 1. Separar cambios
git stash push -m "Cambios custom"
git add backend/app/core/ frontend/components/core/
git commit -m "refactor(core): reorganizar tasks de Celery"

# 2. Mover a main
git checkout main
git cherry-pick HEAD@{1}  # o usar el hash del commit

# 3. Actualizar rama de trabajo
git checkout crm-prego
git merge main

# 4. Restaurar cambios custom
git stash pop
```

#### ⚠️ Reglas Críticas

- **NUNCA** commitees cambios de `core/` directamente en una rama custom sin pasarlos primero a `main`
- **SIEMPRE** actualiza la rama de trabajo desde `main` después de commitear cambios de core
- **SEPARA** cuidadosamente los cambios de core de los cambios de custom antes de commitear
- Los cambios en `custom/` pueden commitearse directamente en la rama de trabajo sin pasar por `main`

#### ¿Cómo Saber si un Cambio es Core?

- **Core**: Funcionalidad genérica, reutilizable, parte de la infraestructura base
- **Custom**: Lógica específica del cliente, nombres de clientes, reglas de negocio específicas

Ver `docs/CORE_VS_CUSTOM_BRANCH_STRATEGY.md` para más detalles.

## Referencias Importantes

- `.cursorrules` - Reglas detalladas del proyecto (Cursor)
- `docs/ARCHITECTURE.md` - Arquitectura completa
- `docs/CORE_VS_CUSTOM_BRANCH_STRATEGY.md` - Estrategia de branches y flujo de git para core vs custom
- `docs/BACKEND_ARCHITECTURE.md` - Arquitectura del backend

