# Conventional Commits

Este proyecto utiliza el estándar [Conventional Commits](https://www.conventionalcommits.org/) para los mensajes de commit. Esto ayuda a mantener un historial de commits claro y permite generar changelogs automáticamente.

## Formato

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Tipos de Commit

### `feat`
Nueva funcionalidad para el usuario (no para un script de build).

```bash
git commit -m "feat: agregar autenticación con JWT"
git commit -m "feat(auth): implementar login con Google"
```

### `fix`
Corrección de un bug.

```bash
git commit -m "fix: corregir validación de email"
git commit -m "fix(api): resolver error 500 en endpoint de usuarios"
```

### `docs`
Cambios en la documentación.

```bash
git commit -m "docs: actualizar guía de instalación"
git commit -m "docs(api): agregar ejemplos de uso"
```

### `style`
Cambios de formato, punto y coma faltante, etc.; sin afectar el código de producción.

```bash
git commit -m "style: formatear código con black"
git commit -m "style(frontend): corregir indentación"
```

### `refactor`
Refactorización del código de producción, por ejemplo, renombrar una variable.

```bash
git commit -m "refactor: extraer lógica de validación a servicio"
git commit -m "refactor(users): simplificar método de creación"
```

### `perf`
Mejora de rendimiento.

```bash
git commit -m "perf: optimizar consulta de base de datos"
git commit -m "perf(api): cachear respuestas frecuentes"
```

### `test`
Agregar o corregir tests.

```bash
git commit -m "test: agregar tests para servicio de usuarios"
git commit -m "test(integration): corregir test de API"
```

### `build`
Cambios en el sistema de build o dependencias externas (ej: npm, pip, docker).

```bash
git commit -m "build: actualizar dependencias de Python"
git commit -m "build(docker): optimizar imagen de producción"
```

### `ci`
Cambios en archivos de configuración de CI/CD.

```bash
git commit -m "ci: agregar workflow de tests"
git commit -m "ci(github): configurar CodeQL"
```

### `chore`
Otros cambios que no modifican el código fuente ni los tests (ej: actualizar .gitignore).

```bash
git commit -m "chore: actualizar .gitignore"
git commit -m "chore(deps): actualizar dependencias"
```

### `revert`
Revertir un commit anterior.

```bash
git commit -m "revert: revertir cambio en autenticación"
git commit -m "revert(feat): revertir implementación de cache"
```

## Scope (Opcional)

El scope es opcional y especifica el área del código afectada. Ejemplos:

- `feat(auth)`: Nueva funcionalidad en autenticación
- `fix(api)`: Corrección en la API
- `docs(readme)`: Cambios en el README
- `refactor(users)`: Refactorización en el módulo de usuarios
- `test(integration)`: Tests de integración

## Descripción

- **Obligatoria**: Debe estar en minúsculas
- **No termina en punto**: No debe terminar con punto final
- **Imperativo**: Usa el modo imperativo ("agregar" no "agrega" o "agregué")
- **Máximo 72 caracteres**: Para mantener el mensaje legible

### ✅ Buenos Ejemplos

```bash
feat: agregar autenticación con JWT
fix(api): corregir error 500 en endpoint de usuarios
docs: actualizar guía de instalación
refactor(users): simplificar lógica de creación
test: agregar tests para servicio de autenticación
```

### ❌ Malos Ejemplos

```bash
# Sin tipo
agregar autenticación

# Tipo incorrecto
feature: agregar autenticación

# Descripción con punto
feat: agregar autenticación.

# Descripción en pasado
feat: agregué autenticación

# Descripción muy larga
feat: agregar sistema completo de autenticación con JWT, refresh tokens, y validación de roles de usuario
```

## Body (Opcional)

El cuerpo proporciona información adicional sobre el cambio. Debe estar separado del título por una línea en blanco.

```bash
git commit -m "feat: agregar autenticación con JWT

Implementa autenticación usando JWT tokens con refresh tokens.
Incluye validación de roles y permisos.

Closes #123"
```

## Footer (Opcional)

El footer se usa para referencias a issues, breaking changes, etc.

### Referencias a Issues

```bash
feat: agregar autenticación con JWT

Closes #123
Fixes #456
Refs #789
```

### Breaking Changes

```bash
feat(api): cambiar formato de respuesta

BREAKING CHANGE: El formato de respuesta ahora incluye metadata adicional.
Los clientes deben actualizar su código para manejar el nuevo formato.
```

## Ejemplos Completos

### Commit Simple

```bash
feat: agregar endpoint de usuarios
```

### Commit con Scope

```bash
feat(users): agregar endpoint de creación de usuarios
```

### Commit con Body

```bash
feat(users): agregar endpoint de creación de usuarios

Implementa POST /api/v1/users con validación de email único
y generación automática de ID.

Closes #42
```

### Commit con Breaking Change

```bash
refactor(api): cambiar estructura de respuesta

BREAKING CHANGE: La respuesta ahora incluye un campo 'data' que envuelve
el contenido anterior. Los clientes deben actualizar su código.

Antes:
{
  "id": 1,
  "name": "John"
}

Después:
{
  "data": {
    "id": 1,
    "name": "John"
  }
}
```

## Validación Automática

El proyecto incluye un hook de pre-commit que valida automáticamente el formato de los mensajes de commit. Si el mensaje no sigue el formato, el commit será rechazado.

### Ejecutar Validación Manualmente

```bash
# Validar el último mensaje de commit
pre-commit run commit-msg --hook-stage commit-msg

# Validar un mensaje específico
echo "feat: mi nuevo feature" | pre-commit run commit-msg --hook-stage commit-msg
```

### Saltar Validación (No Recomendado)

```bash
# Solo en casos excepcionales
git commit --no-verify -m "mensaje sin formato"
```

⚠️ **Advertencia**: Saltar la validación puede comprometer la consistencia del historial.

## Beneficios

1. **Historial Claro**: Fácil de entender qué cambió y por qué
2. **Changelog Automático**: Herramientas pueden generar changelogs automáticamente
3. **Versionado Semántico**: Facilita el versionado semántico basado en tipos de commits
4. **Búsqueda Fácil**: Fácil buscar commits por tipo o scope
5. **Automatización**: CI/CD puede usar los tipos para tomar decisiones

## Herramientas Relacionadas

- [Conventional Commits](https://www.conventionalcommits.org/) - Especificación oficial
- [Commitlint](https://commitlint.js.org/) - Linter para mensajes de commit
- [Semantic Release](https://semantic-release.gitbook.io/) - Automatización de releases
- [Standard Version](https://github.com/conventional-changelog/standard-version) - Generación de changelogs

## Recursos

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [Git Commit Best Practices](https://chris.beams.io/posts/git-commit/)

