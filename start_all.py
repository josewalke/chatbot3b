#!/usr/bin/env python3
"""
Script para iniciar todo el sistema del Chatbot Inteligente
"""
import os
import sys
import subprocess
import time
import threading
import requests

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
        import requests
        print("✅ Dependencias instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependencias faltantes: {e}")
        return False

def start_server():
    """Iniciar el servidor en segundo plano"""
    print("🚀 Iniciando servidor...")
    
    # Cambiar a la carpeta backend
    os.chdir("backend")
    
    # Comando para iniciar el servidor
    cmd = [sys.executable, "optimized_server.py"]
    
    try:
        # Ejecutar el servidor en segundo plano
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un poco para que el servidor se inicie
        time.sleep(5)
        
        # Verificar si el servidor está funcionando
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ Servidor iniciado correctamente en http://localhost:8000")
                return process
            else:
                print("❌ Servidor no responde correctamente")
                return None
        except requests.exceptions.RequestException:
            print("❌ No se puede conectar al servidor")
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return None

def start_learning():
    """Iniciar aprendizaje automático"""
    print("🧠 Iniciando aprendizaje automático...")
    
    # Volver a la carpeta raíz
    os.chdir("..")
    
    try:
        # Ejecutar el script de aprendizaje continuo
        cmd = [sys.executable, "demo_continuous_learning.py"]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Aprendizaje detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando aprendizaje: {e}")

def main():
    """Función principal"""
    print("🤖 CHATBOT INTELIGENTE - SISTEMA COMPLETO")
    print("=" * 50)
    
    # Verificar entorno virtual
    if not activate_venv():
        print("💡 Ejecuta: py -m venv .venv")
        return
    
    # Verificar dependencias
    if not check_dependencies():
        print("💡 Ejecuta: py -m pip install -r backend/requirements_optimized.txt")
        return
    
    print("\n🎯 ¿Qué quieres hacer?")
    print("1. 🚀 Solo iniciar servidor")
    print("2. 🧠 Solo iniciar aprendizaje")
    print("3. 🔄 Iniciar servidor + aprendizaje")
    print("4. ❌ Salir")
    
    while True:
        try:
            choice = input("\n📝 Selecciona una opción (1-4): ").strip()
            
            if choice == "1":
                print("\n🚀 Iniciando solo el servidor...")
                start_server()
                input("\n🛑 Presiona Enter para detener el servidor...")
                break
                
            elif choice == "2":
                print("\n🧠 Iniciando solo el aprendizaje...")
                start_learning()
                break
                
            elif choice == "3":
                print("\n🔄 Iniciando servidor y aprendizaje...")
                server_process = start_server()
                
                if server_process:
                    print("⏰ Esperando 10 segundos para que el servidor se estabilice...")
                    time.sleep(10)
                    
                    print("🧠 Iniciando aprendizaje automático...")
                    start_learning()
                else:
                    print("❌ No se pudo iniciar el servidor")
                break
                
            elif choice == "4":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida. Selecciona 1, 2, 3 o 4.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

if __name__ == "__main__":
    main() 