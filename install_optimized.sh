#!/bin/bash
# Script de instalación automática para Chatbot Inteligente Optimizado

echo "🤖 Instalando Chatbot Inteligente Optimizado..."
echo "================================================"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado"
    exit 1
fi

echo "✅ Python 3 detectado"

# Instalar dependencias
echo "📦 Instalando dependencias optimizadas..."
cd backend
pip3 install -r requirements_optimized.txt

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env optimizado..."
    cat > .env << EOF
# Configuración Optimizada del Chatbot
DEBUG=False
WORKERS=1
CACHE_MAX_SIZE=1000
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///chatbot_optimized.db
SECRET_KEY=chatbot-optimized-secret-key-2024
EOF
fi

echo "✅ Instalación completada"
echo "🚀 Para iniciar: python3 start_optimized.py" 