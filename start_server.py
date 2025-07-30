#!/usr/bin/env python3
"""
Script para iniciar el servidor del Chatbot Inteligente
"""
import os
import sys
import subprocess
import time

def activate_venv():
    """Activar el entorno virtual"""
    print("🔧 Activando entorno virtual...")
    if os.name == 'nt':  # Windows
        activate_script = ".venv\\Scripts\\Activate.ps1"
        if os.path.exists(activate_script):
            print("✅ Entorno virtual encontrado")
            return True
        else:
            print("❌ No se encontró el entorno virtual")
            return False
    else:  # Linux/Mac
        activate_script = ".venv/bin/activate"
        if os.path.exists(activate_script):
            print("✅ Entorno virtual encontrado")
            return True
        else:
            print("❌ No se encontró el entorno virtual")
            return False

def check_dependencies():
    """Verificar dependencias"""
    print("📦 Verificando dependencias...")
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencias instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependencias faltantes: {e}")
        return False

def start_server():
    """Iniciar el servidor"""
    print("🚀 Iniciando servidor del Chatbot...")
    
    # Cambiar a la carpeta backend
    os.chdir("backend")
    
    # Comando para iniciar el servidor simple
    cmd = [sys.executable, "test_simple_server.py"]
    
    try:
        print("📡 Servidor iniciado en http://localhost:8000")
        print("🛑 Presiona Ctrl+C para detener el servidor")
        print("=" * 50)
        
        # Ejecutar el servidor
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

def main():
    """Función principal"""
    print("🤖 CHATBOT INTELIGENTE - INICIADOR DE SERVIDOR")
    print("=" * 50)
    
    # Verificar entorno virtual
    if not activate_venv():
        print("💡 Ejecuta: py -m venv .venv")
        return
    
    # Verificar dependencias
    if not check_dependencies():
        print("💡 Ejecuta: py -m pip install -r backend/requirements_optimized.txt")
        return
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main() 