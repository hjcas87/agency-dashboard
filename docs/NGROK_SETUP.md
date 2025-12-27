# Configuración de ngrok para Exponer el Frontend

Esta guía explica cómo usar ngrok para exponer tu frontend local a través de una URL pública, permitiendo compartir tu aplicación con otros sin necesidad de deploy.

## 📋 Prerrequisitos

1. **ngrok instalado** en tu sistema
2. **Frontend corriendo** en el puerto 3000 (por defecto)
3. **Cuenta de ngrok** (gratuita) para obtener un authtoken

## 🚀 Instalación de ngrok

### macOS
```bash
brew install ngrok/ngrok/ngrok
```

### Linux
```bash
# Descargar desde: https://ngrok.com/download
# O usar el instalador:
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok
```

### Windows
Descarga el ejecutable desde: https://ngrok.com/download

## 🔑 Configuración del Authtoken

1. **Crear cuenta gratuita**:
   - Visita: https://dashboard.ngrok.com/signup
   - Crea una cuenta (es gratis)

2. **Obtener tu authtoken**:
   - Ve a: https://dashboard.ngrok.com/get-started/your-authtoken
   - Copia tu authtoken

3. **Configurar ngrok**:
   ```bash
   ngrok config add-authtoken TU_TOKEN_AQUI
   ```

   O exporta la variable de entorno:
   ```bash
   export NGROK_AUTH_TOKEN=TU_TOKEN_AQUI
   ```

## 🎯 Uso

### Opción 1: Usar el script del proyecto (Recomendado)

```bash
# Desde la raíz del proyecto
make ngrok

# O directamente:
./scripts/ngrok-frontend.sh
```

El script:
- ✅ Verifica que ngrok esté instalado
- ✅ Verifica que el frontend esté corriendo
- ✅ Espera automáticamente si el frontend no está disponible
- ✅ Inicia ngrok en el puerto 3000

### Opción 2: Usar ngrok directamente

```bash
# Si el frontend está en el puerto 3000 (por defecto)
ngrok http 3000

# Si el frontend está en otro puerto
ngrok http 8080
```

### Opción 3: Usar con puerto personalizado

```bash
# Configurar el puerto del frontend
export FRONTEND_PORT=3000
./scripts/ngrok-frontend.sh
```

## 📱 Acceder a tu Frontend

Una vez que ngrok esté corriendo, verás algo como:

```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:3000
```

**Comparte esta URL** (`https://abc123.ngrok-free.app`) con quien quieras que acceda a tu frontend.

## ⚙️ Configuración del Frontend para URLs Públicas

Si necesitas que el frontend funcione correctamente con la URL de ngrok, asegúrate de:

1. **Configurar CORS en el backend** (si es necesario):
   ```python
   # En backend/app/main.py
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # En desarrollo, ajustar para producción
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Variables de entorno del frontend**:
   - El frontend usa `NEXT_PUBLIC_API_URL` para conectarse al backend
   - Si el backend también necesita ser accesible públicamente, considera usar ngrok también para el backend

## 🔒 Seguridad

⚠️ **Importante**: 
- Las URLs de ngrok son **públicas** y cualquiera con el link puede acceder
- No uses ngrok en producción
- Considera usar autenticación si compartes URLs de desarrollo
- Las URLs gratuitas de ngrok cambian cada vez que reinicias ngrok (a menos que uses un plan de pago)

## 🛠️ Solución de Problemas

### Error: "ngrok not found"
```bash
# Verificar instalación
which ngrok

# Si no está instalado, instalar según tu sistema (ver arriba)
```

### Error: "Frontend no está corriendo"
```bash
# Asegúrate de que el frontend esté corriendo
cd frontend && npm run dev

# Verificar que esté en el puerto correcto
lsof -i :3000
```

### Error: "authtoken required"
```bash
# Configurar el authtoken
ngrok config add-authtoken TU_TOKEN

# O verificar la configuración
ngrok config check
```

### El frontend no carga correctamente con la URL de ngrok
- Verifica que el backend también sea accesible (puede necesitar su propio túnel ngrok)
- Revisa la consola del navegador para errores de CORS
- Asegúrate de que `NEXT_PUBLIC_API_URL` esté configurado correctamente

## 📚 Recursos Adicionales

- [Documentación oficial de ngrok](https://ngrok.com/docs)
- [Dashboard de ngrok](https://dashboard.ngrok.com/)
- [Guía de inicio rápido de ngrok](https://ngrok.com/docs/getting-started/)


