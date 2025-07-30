#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicio Optimizado para Chatbot Inteligente
Versión eficiente en recursos
"""

import os
import sys
import logging
import subprocess
import time
from pathlib import Path

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        logger.error("❌ Se requiere Python 3.8 o superior")
        return False
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def check_dependencies():
    """Verificar dependencias básicas"""
    required_packages = ['fastapi', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} instalado")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"⚠️ {package} no encontrado")
    
    if missing_packages:
        logger.error(f"❌ Paquetes faltantes: {', '.join(missing_packages)}")
        logger.info("💡 Ejecuta: pip install -r requirements_optimized.txt")
        return False
    
    return True

def create_env_file():
    """Crear archivo .env optimizado si no existe"""
    env_file = Path(".env")
    if not env_file.exists():
        logger.info("📝 Creando archivo .env optimizado...")
        
        env_content = """# Configuración Optimizada del Chatbot
# Modo optimizado (ahorra recursos)
DEBUG=False
WORKERS=1
CACHE_MAX_SIZE=1000
LOG_LEVEL=INFO

# Base de datos SQLite (ligera)
DATABASE_URL=sqlite:///chatbot_optimized.db

# Configuraciones opcionales (descomentar solo si se necesita)
# USE_OPENAI=False
# OPENAI_API_KEY=tu-api-key-aqui

# USE_STRIPE=False
# STRIPE_SECRET_KEY=tu-stripe-key-aqui

# USE_TELEGRAM=False
# TELEGRAM_BOT_TOKEN=tu-telegram-token-aqui

# USE_FACEBOOK=False
# FACEBOOK_PAGE_ACCESS_TOKEN=tu-facebook-token-aqui

# Configuración de seguridad
SECRET_KEY=chatbot-optimized-secret-key-2024
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        logger.info("✅ Archivo .env creado")
    else:
        logger.info("✅ Archivo .env encontrado")

def optimize_system():
    """Optimizar configuración del sistema"""
    logger.info("🔧 Aplicando optimizaciones...")
    
    # Configurar variables de entorno para optimización
    os.environ.setdefault('PYTHONOPTIMIZE', '1')  # Optimizaciones de Python
    os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')  # No generar .pyc
    os.environ.setdefault('PYTHONUNBUFFERED', '1')  # Salida sin buffer
    
    # Configuraciones específicas del chatbot
    os.environ.setdefault('WORKERS', '1')
    os.environ.setdefault('CACHE_MAX_SIZE', '1000')
    os.environ.setdefault('LOG_LEVEL', 'INFO')
    
    logger.info("✅ Optimizaciones aplicadas")

def start_server():
    """Iniciar servidor optimizado con aprendizaje continuo"""
    logger.info("🚀 Iniciando servidor optimizado...")
    
    try:
        # Configurar servidor uvicorn optimizado
        cmd = [
            sys.executable, "-m", "uvicorn",
            "optimized_server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "1",
            "--loop", "asyncio",
            "--log-level", "info",
            "--access-log",
            "--no-use-colors"
        ]
        
        logger.info("✅ Servidor iniciado en http://localhost:8000")
        logger.info("📊 Panel de estado: http://localhost:8000/health")
        logger.info("🤖 Chat: http://localhost:8000/chat/send")
        logger.info("📈 Estadísticas: http://localhost:8000/stats")
        logger.info("🔄 Aprendizaje continuo: http://localhost:8000/continuous-learning/stats")
        
        # Ejecutar servidor
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        return False
    
    return True

def show_optimization_info():
    """Mostrar información de optimización"""
    logger.info("""
🔧 CHATBOT INTELIGENTE OPTIMIZADO
================================

💾 Optimizaciones de Memoria:
   • Cache limitado a 1000 elementos
   • Un solo worker para ahorrar RAM
   • Base de datos SQLite ligera
   • Logging optimizado

⚡ Optimizaciones de CPU:
   • LRU cache para funciones frecuentes
   • Búsqueda directa de patrones
   • Procesamiento asíncrono
   • Índices en base de datos

🌐 Optimizaciones de Red:
   • Respuestas JSON compactas
   • Timeouts configurados
   • CORS optimizado
   • Headers mínimos

📊 Uso de Recursos Estimado:
   • Memoria: ~50-100 MB
   • CPU: ~5-15%
   • Disco: ~10-50 MB
   • Red: Mínimo

🚀 Endpoints Disponibles:
   • GET  / - Página principal
   • GET  /health - Estado del servidor
   • POST /chat/send - Enviar mensaje
   • GET  /appointments/available-slots - Horarios
   • POST /appointments/create - Crear cita
   • GET  /sales/products - Productos
   • POST /support/query - Soporte
   • GET  /stats - Estadísticas

💡 Para habilitar características adicionales:
   • Edita el archivo .env
   • Descomenta las configuraciones que necesites
   • Instala las dependencias correspondientes
""")

def main():
    """Función principal"""
    logger.info("🤖 Iniciando Chatbot Inteligente Optimizado...")
    
    # Verificaciones previas
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        logger.error("❌ No se pueden verificar las dependencias")
        logger.info("💡 Instala las dependencias: pip install -r requirements_optimized.txt")
        sys.exit(1)
    
    # Configurar entorno
    create_env_file()
    optimize_system()
    
    # Mostrar información
    show_optimization_info()
    
    # Iniciar servidor
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main() 