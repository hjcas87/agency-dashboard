#!/bin/bash
set -e

echo "🚀 Configurando Core Boilerplate..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Copiar .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Archivo .env creado. Por favor revisa y ajusta las variables según necesites."
    else
        echo "⚠️  .env.example no encontrado. Creando .env básico..."
        cat > .env << EOF
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=core_db

# Backend
SECRET_KEY=dev-secret-key-change-in-production

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# N8N
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin
EOF
    fi
fi

echo "✅ Configuración completada!"
echo ""
echo "Para levantar el proyecto, ejecuta:"
echo "  docker-compose up -d"
echo ""
echo "O usa el Makefile:"
echo "  make dev"

