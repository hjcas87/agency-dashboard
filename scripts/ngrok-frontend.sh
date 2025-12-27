#!/bin/bash

# Script para exponer el frontend local con ngrok
# Uso: ./scripts/ngrok-frontend.sh

set -e

FRONTEND_PORT=${FRONTEND_PORT:-3000}
NGROK_AUTH_TOKEN=${NGROK_AUTH_TOKEN:-}

echo "============================================================"
echo "Exponiendo Frontend con ngrok"
echo "============================================================"
echo ""
echo "Puerto del frontend: $FRONTEND_PORT"
echo ""

# Verificar si ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok no está instalado."
    echo ""
    echo "Para instalar ngrok:"
    echo "  macOS: brew install ngrok/ngrok/ngrok"
    echo "  Linux: https://ngrok.com/download"
    echo "  O descarga desde: https://ngrok.com/download"
    echo ""
    exit 1
fi

# Verificar si hay un token de autenticación configurado
if [ -z "$NGROK_AUTH_TOKEN" ]; then
    echo "⚠️  NGROK_AUTH_TOKEN no está configurado."
    echo ""
    echo "Para obtener un token gratuito:"
    echo "  1. Visita: https://dashboard.ngrok.com/signup"
    echo "  2. Crea una cuenta (gratis)"
    echo "  3. Copia tu authtoken de: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "  4. Ejecuta: ngrok config add-authtoken TU_TOKEN"
    echo "  5. O exporta la variable: export NGROK_AUTH_TOKEN=TU_TOKEN"
    echo ""
    echo "Continuando sin token (funcionalidad limitada)..."
    echo ""
fi

# Verificar que el frontend esté corriendo
if ! lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  El frontend no está corriendo en el puerto $FRONTEND_PORT"
    echo ""
    echo "Para iniciar el frontend:"
    echo "  cd frontend && npm run dev"
    echo ""
    echo "Esperando a que el frontend esté disponible..."
    
    # Esperar hasta que el puerto esté disponible
    MAX_WAIT=30
    WAITED=0
    while ! lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; do
        if [ $WAITED -ge $MAX_WAIT ]; then
            echo "❌ Timeout: El frontend no está disponible después de $MAX_WAIT segundos"
            exit 1
        fi
        sleep 1
        WAITED=$((WAITED + 1))
        echo -n "."
    done
    echo ""
    echo "✅ Frontend detectado"
    echo ""
fi

echo "🚀 Iniciando ngrok..."
echo ""
echo "El frontend estará disponible en una URL pública cuando ngrok se inicie."
echo "Presiona Ctrl+C para detener ngrok."
echo ""

# Configurar authtoken si está disponible
if [ -n "$NGROK_AUTH_TOKEN" ]; then
    ngrok config add-authtoken "$NGROK_AUTH_TOKEN" 2>/dev/null || true
fi

# Iniciar ngrok
ngrok http $FRONTEND_PORT


