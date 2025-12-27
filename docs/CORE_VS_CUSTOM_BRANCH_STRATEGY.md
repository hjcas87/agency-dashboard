# Estrategia de Branches: Core vs Custom

## Principio Fundamental

**Todo código genérico debe estar en `core/` y commitearse en la rama `main`.**

## ¿Qué va en Core?

El código debe ir en `core/` si:

1. ✅ Es funcionalidad genérica reutilizable
2. ✅ No tiene lógica de negocio específica del cliente
3. ✅ Puede ser usado por cualquier fork del proyecto
4. ✅ Es parte de la infraestructura base (auth, users, health, n8n, etc.)

### Ejemplos de Features Core

- **Auth** (`core/features/auth/`) - Autenticación genérica (JWT, login, password reset)
- **Users** (`core/features/users/`) - Gestión genérica de usuarios
- **Health** (`core/features/health/`) - Health checks
- **N8N** (`core/features/n8n/`) - Integración genérica con N8N

### Ejemplos de Features Custom

- **Campaigns** (`custom/features/campaigns/`) - Lógica específica de campañas
- **Journeys** (`custom/features/journeys/`) - Journey Builder específico
- **Contacts** (`custom/features/contacts/`) - Gestión de contactos específica
- **Pipelines** (`custom/features/pipelines/`) - Pipeline de leads específico

## Flujo de Trabajo

### Cuando trabajas en una rama custom (ej: `crm-prego`)

1. **Identifica si el cambio es genérico o específico**
   - ¿Es funcionalidad que cualquier fork podría usar? → **Core**
   - ¿Es lógica específica del cliente? → **Custom**

2. **Si es Core - Proceso Completo:**

   Cuando modificas código de `core/`, **SIEMPRE** debes seguir este proceso:

   ```bash
   # PASO 1: Estás en tu rama de trabajo (ej: crm-prego)
   # Separar cambios de core de cambios de custom
   git stash push -m "Cambios custom - restaurar después"
   
   # PASO 2: Agregar solo cambios de core
   git add backend/app/core/ frontend/components/core/ frontend/app/actions/core/
   git commit -m "refactor(core): descripción de cambios"
   
   # PASO 3: Cambiar a main y traer los cambios
   git checkout main
   git cherry-pick <commit-hash>
   # O alternativamente, si prefieres merge selectivo:
   # git merge crm-prego --no-ff -m "Merge core changes"
   
   # PASO 4: Volver a tu rama de trabajo
   git checkout crm-prego
   
   # PASO 5: Actualizar tu rama desde main (CRÍTICO)
   git merge main
   
   # PASO 6: Restaurar cambios de custom si había stash
   git stash pop
   ```

   **⚠️ IMPORTANTE**: El paso 5 (actualizar desde main) es **obligatorio** después de commitear cambios de core en main.

3. **Si es Custom:**
   ```bash
   # Commitear directamente en tu rama custom
   git checkout crm-prego
   git add backend/app/custom/features/...
   git commit -m "feat(custom): agregar funcionalidad Y específica"
   git push origin crm-prego
   ```

## Verificación: ¿Es Core o Custom?

### Preguntas para decidir:

1. **¿Esta funcionalidad es específica de un cliente?**
   - Sí → Custom
   - No → Core

2. **¿Otros forks del proyecto necesitarían esto?**
   - Sí → Core
   - No → Custom

3. **¿Es parte de la infraestructura base?**
   - Sí → Core
   - No → Custom

4. **¿Tiene lógica de negocio específica del dominio del cliente?**
   - Sí → Custom
   - No → Core

## Ejemplo: Módulo de Auth

El módulo de auth (`backend/app/core/features/auth/`) es **genérico** porque:

- ✅ Maneja autenticación JWT (estándar)
- ✅ Login/logout genérico
- ✅ Password reset genérico
- ✅ No tiene lógica de negocio específica
- ✅ Cualquier fork lo necesita

**Por lo tanto, está correctamente ubicado en `core/` y todos los cambios deben commitearse en `main`.**

## Checklist antes de commitear en Core

Antes de commitear cambios en `core/`:

- [ ] El código es genérico y reutilizable
- [ ] No tiene referencias a "custom", nombres de clientes, o lógica específica
- [ ] Está bien documentado
- [ ] Tiene tests (si aplica)
- [ ] Se commitea en `main` primero
- [ ] Luego se actualiza la rama custom desde `main`

## Comandos Útiles

### Ver qué archivos están en core vs custom

```bash
# Ver archivos modificados en core
git diff main --name-only | grep "backend/app/core/"

# Ver archivos modificados en custom
git diff main --name-only | grep "backend/app/custom/"
```

### Mover cambios de core a main (Proceso Detallado)

```bash
# PASO 1: Estás en tu rama de trabajo (ej: crm-prego)
# Ver qué cambios hay y separar core de custom
git status
git diff backend/app/core/

# PASO 2: Si hay cambios mezclados, usar stash para separarlos
git stash push -m "Cambios custom/frontend - restaurar después"
# O si solo quieres agregar específicos:
# git add backend/app/core/ frontend/components/core/

# PASO 3: Crear un commit solo con cambios de core
git add backend/app/core/ frontend/components/core/ frontend/app/actions/core/
git commit -m "feat(core): descripción del cambio"

# PASO 4: Cambiar a main y traer los cambios
git checkout main
git cherry-pick <commit-hash>
# O si prefieres merge selectivo:
# git merge crm-prego --no-ff -m "Merge core changes from crm-prego"

# PASO 5: Volver a tu rama y actualizar desde main (OBLIGATORIO)
git checkout crm-prego
git merge main

# PASO 6: Si usaste stash, restaurar cambios de custom
git stash pop
```

**⚠️ El paso 5 es crítico**: Siempre debes actualizar tu rama de trabajo desde `main` después de commitear cambios de core.

## Notas Importantes

⚠️ **NUNCA modifiques código en `core/` directamente en una rama custom sin commitear primero en `main`.**

⚠️ **Si encuentras código específico en `core/`, debe moverse a `custom/`.**

⚠️ **Si encuentras código genérico en `custom/`, debe moverse a `core/` y commitearse en `main`.**

## Referencias

- Ver `.cursorrules` para más detalles sobre la arquitectura
- Ver `docs/ARCHITECTURE.md` para la estructura del proyecto
- Ver `docs/EXTENDING.md` para cómo extender el proyecto

