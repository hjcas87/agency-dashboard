# Logging con Rich

El backend usa [Rich](https://rich.readthedocs.io/) para mejorar la salida de terminal con colores, formato y mejor legibilidad.

## Configuración

El logging se configura automáticamente al iniciar la aplicación en `app/main.py`. La configuración está en `app/core/logging_config.py`.

### Niveles de Log por Ambiente

- **DEVELOPMENT**: `DEBUG` - Muestra todos los logs
- **PRODUCTION**: `INFO` - Solo logs importantes
- **Otros**: `WARNING` - Solo warnings y errores

## Uso Básico

```python
from app.core.logging_config import get_logger

logger = get_logger(__name__)

logger.debug("Mensaje de debug")
logger.info("Mensaje informativo")
logger.warning("Advertencia")
logger.error("Error")
```

## Usando Markup de Rich

Rich soporta markup para colores y estilos. Ejemplos:

```python
# Colores básicos
logger.info("[red]Error[/red] en la operación")
logger.info("[green]✓[/green] Operación exitosa")
logger.info("[yellow]⚠[/yellow] Advertencia")
logger.info("[cyan]Información[/cyan] importante")

# Estilos
logger.info("[bold]Texto en negrita[/bold]")
logger.info("[dim]Texto atenuado[/dim]")
logger.info("[italic]Texto en cursiva[/italic]")

# Combinaciones
logger.info("[bold green]✓[/bold green] Email enviado a [cyan]user@example.com[/cyan]")
logger.error("[bold red]✗[/bold red] Error: [yellow]Connection timeout[/yellow]")
```

## Ejemplos Comunes

### Mensajes de Éxito

```python
logger.info(f"[green]✓[/green] Email enviado exitosamente a [cyan]{email}[/cyan]")
logger.info(f"[bold green]✓[/bold green] Usuario creado: [bold]{username}[/bold]")
```

### Mensajes de Error

```python
logger.error(f"[red]✗[/red] Error al enviar email: [yellow]{str(e)}[/yellow]")
logger.error(f"[bold red]✗[/bold red] Fallo crítico: [yellow]{error_message}[/yellow]")
```

### Mensajes de Advertencia

```python
logger.warning(f"[yellow]⚠[/yellow] SMTP no configurado, usando servicio de logging")
logger.warning(f"[yellow]⚠[/yellow] Intento {retry_count}/{max_retries} fallido")
```

### Mensajes Informativos

```python
logger.info(f"[cyan]Procesando[/cyan] workflow [bold]{workflow_name}[/bold]")
logger.info(f"[dim]Email (logged, not sent):[/dim]\n[cyan]To:[/cyan] {to}")
```

## Colores Disponibles

- `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
- `bright_black`, `bright_red`, `bright_green`, etc.

## Estilos Disponibles

- `bold` - Negrita
- `dim` - Atenuado
- `italic` - Cursiva
- `underline` - Subrayado
- `strike` - Tachado
- `reverse` - Invertido

## Tracebacks Mejorados

Rich automáticamente mejora los tracebacks cuando se usa `exc_info=True`:

```python
try:
    # código que puede fallar
    pass
except Exception as e:
    logger.error("Error en operación", exc_info=True)
    # Rich mostrará un traceback bonito con colores y formato
```

## Referencias

- [Rich Documentation](https://rich.readthedocs.io/)
- [Rich Markup Guide](https://rich.readthedocs.io/en/latest/markup.html)
- [Rich Logging](https://rich.readthedocs.io/en/latest/logging.html)
