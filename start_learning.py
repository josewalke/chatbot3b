#!/usr/bin/env python3
"""
Script para iniciar el aprendizaje automático del Chatbot Inteligente
"""
import os
import sys
import subprocess
import time
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

def check_server():
    """Verificar si el servidor está funcionando"""
    print("🔍 Verificando servidor...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print("❌ Servidor no responde correctamente")
            return False
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return False

def start_continuous_learning():
    """Iniciar aprendizaje continuo"""
    print("🧠 Iniciando aprendizaje automático...")
    
    try:
        print("📚 El chatbot comenzará a aprender automáticamente")
        print("⏰ Intervalo de aprendizaje: 30 minutos")
        print("🛑 Presiona Ctrl+C para detener el aprendizaje")
        print("=" * 50)
        
        # Ejecutar el script de aprendizaje continuo
        cmd = [sys.executable, "demo_continuous_learning.py"]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Aprendizaje detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando aprendizaje: {e}")

def start_auto_learning():
    """Iniciar aprendizaje automático simple"""
    print("🤖 Iniciando aprendizaje automático...")
    
    try:
        print("📚 Descargando vocabulario español...")
        print("🔄 Configurando fuentes de aprendizaje...")
        print("=" * 50)
        
        # Ejecutar el script de aprendizaje automático
        cmd = [sys.executable, "run_auto_learning.py"]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Aprendizaje detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando aprendizaje: {e}")

def show_menu():
    """Mostrar menú de opciones"""
    print("\n🎯 ¿Qué tipo de aprendizaje quieres iniciar?")
    print("1. 🧠 Aprendizaje continuo (recomendado)")
    print("2. 🤖 Aprendizaje automático simple")
    print("3. 📊 Solo monitorear estadísticas")
    print("4. ❌ Salir")
    
    while True:
        try:
            choice = input("\n📝 Selecciona una opción (1-4): ").strip()
            if choice == "1":
                return "continuous"
            elif choice == "2":
                return "auto"
            elif choice == "3":
                return "monitor"
            elif choice == "4":
                return "exit"
            else:
                print("❌ Opción inválida. Selecciona 1, 2, 3 o 4.")
        except KeyboardInterrupt:
            return "exit"

def main():
    """Función principal"""
    print("🤖 CHATBOT INTELIGENTE - INICIADOR DE APRENDIZAJE")
    print("=" * 50)
    
    # Verificar entorno virtual
    if not activate_venv():
        print("💡 Ejecuta: py -m venv .venv")
        return
    
    # Verificar servidor
    if not check_server():
        print("💡 Primero ejecuta: py start_server.py")
        return
    
    # Mostrar menú
    choice = show_menu()
    
    if choice == "exit":
        print("👋 ¡Hasta luego!")
        return
    elif choice == "continuous":
        start_continuous_learning()
    elif choice == "auto":
        start_auto_learning()
    elif choice == "monitor":
        print("📊 Iniciando monitor de estadísticas...")
        cmd = [sys.executable, "monitor_continuous_learning.py"]
        subprocess.run(cmd)

if __name__ == "__main__":
    main() 