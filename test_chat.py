#!/usr/bin/env python3
"""
Script para probar el chat del Chatbot Inteligente
"""
import requests
import json
import time

def test_server_health():
    """Probar si el servidor está funcionando"""
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

def test_chat(message: str):
    """Probar el chat con un mensaje"""
    try:
        data = {
            "message": message,
            "user_id": "test_user"
        }
        
        response = requests.post(
            "http://localhost:8000/chat",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 Respuesta: {result['response']}")
            print(f"🎯 Intención: {result['intent']}")
            print(f"⏰ Timestamp: {result['timestamp']}")
            return True
        else:
            print(f"❌ Error en chat: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando chat: {e}")
        return False

def test_stats():
    """Probar estadísticas"""
    try:
        response = requests.get("http://localhost:8000/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("📊 Estadísticas del servidor:")
            print(f"   • Conversaciones totales: {stats.get('total_conversations', 0)}")
            print(f"   • Estadísticas por intención: {stats.get('intent_stats', {})}")
            return True
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error probando estadísticas: {e}")
        return False

def interactive_chat():
    """Chat interactivo"""
    print("\n💬 CHAT INTERACTIVO")
    print("=" * 30)
    print("Escribe 'salir' para terminar")
    print("Escribe 'stats' para ver estadísticas")
    print("-" * 30)
    
    while True:
        try:
            message = input("\n👤 Tú: ").strip()
            
            if message.lower() == 'salir':
                print("👋 ¡Hasta luego!")
                break
            elif message.lower() == 'stats':
                test_stats()
                continue
            elif not message:
                continue
            
            print("🔄 Procesando...")
            test_chat(message)
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🤖 CHATBOT INTELIGENTE - PRUEBA DE CHAT")
    print("=" * 50)
    
    # Verificar servidor
    if not test_server_health():
        return
    
    print("\n🎯 ¿Qué quieres hacer?")
    print("1. 💬 Chat interactivo")
    print("2. 🧪 Pruebas automáticas")
    print("3. 📊 Solo ver estadísticas")
    print("4. ❌ Salir")
    
    while True:
        try:
            choice = input("\n📝 Selecciona una opción (1-4): ").strip()
            
            if choice == "1":
                interactive_chat()
                break
            elif choice == "2":
                print("\n🧪 Ejecutando pruebas automáticas...")
                test_messages = [
                    "Hola",
                    "¿Cómo estás?",
                    "Necesito ayuda",
                    "Quiero hacer una cita",
                    "¿Tienen productos?",
                    "Adiós"
                ]
                
                for message in test_messages:
                    print(f"\n📝 Probando: '{message}'")
                    test_chat(message)
                    time.sleep(1)
                
                print("\n📊 Estadísticas finales:")
                test_stats()
                break
            elif choice == "3":
                test_stats()
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