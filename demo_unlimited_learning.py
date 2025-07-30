#!/usr/bin/env python3
"""
Demo del Sistema de Aprendizaje Ilimitado
Muestra cómo el chatbot puede aprender todas las palabras sin límites
"""

import requests
import time
import json
from typing import Dict, List

# Configuración
BASE_URL = "http://localhost:8000"

def check_server_health():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"❌ Error en servidor: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return False

def get_learning_stats():
    """Obtener estadísticas de aprendizaje"""
    try:
        response = requests.get(f"{BASE_URL}/learning/stats", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_vocabulary_summary():
    """Obtener resumen del vocabulario"""
    try:
        response = requests.get(f"{BASE_URL}/learning/vocabulary", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error obteniendo vocabulario: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def send_message_and_learn(message: str, user_id: str = "demo_user") -> Dict:
    """Enviar mensaje y mostrar aprendizaje"""
    try:
        print(f"💬 Enviando: '{message}'")
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": message,
                "user_id": user_id
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Respuesta: {data['response']}")
            print(f"🎯 Intención: {data['intent']}")
            print(f"📚 Palabras aprendidas: {data['learned_words']}")
            print(f"💬 Expresiones aprendidas: {data['learned_expressions']}")
            print(f"📖 Vocabulario total: {data['total_vocabulary']}")
            return data
        else:
            print(f"❌ Error en respuesta: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return None

def show_learning_progress(initial_stats: Dict, current_stats: Dict):
    """Mostrar progreso del aprendizaje"""
    print("\n📊 PROGRESO DEL APRENDIZAJE")
    print("=" * 50)
    
    if initial_stats and current_stats:
        words_diff = current_stats.get('total_words', 0) - initial_stats.get('total_words', 0)
        expressions_diff = current_stats.get('total_expressions', 0) - initial_stats.get('total_expressions', 0)
        
        print(f"📈 Palabras nuevas aprendidas: +{words_diff}")
        print(f"📈 Expresiones nuevas aprendidas: +{expressions_diff}")
        print(f"📊 Total de palabras: {current_stats.get('total_words', 0)}")
        print(f"📊 Total de expresiones: {current_stats.get('total_expressions', 0)}")
        
        # Mostrar palabras más frecuentes
        top_words = current_stats.get('top_words', [])
        if top_words:
            print("\n🏆 Palabras más frecuentes:")
            for i, word_data in enumerate(top_words[:5], 1):
                print(f"  {i}. '{word_data['word']}' (usada {word_data['frequency']} veces)")

def demonstrate_unlimited_learning():
    """Demostrar aprendizaje ilimitado"""
    print("🚀 DEMOSTRACIÓN: SISTEMA DE APRENDIZAJE ILIMITADO")
    print("=" * 60)
    
    # Verificar servidor
    if not check_server_health():
        return
    
    # Obtener estadísticas iniciales
    print("\n📊 Estadísticas iniciales:")
    initial_stats = get_learning_stats()
    if initial_stats:
        print(f"   Palabras totales: {initial_stats.get('total_words', 0)}")
        print(f"   Expresiones totales: {initial_stats.get('total_expressions', 0)}")
    
    # Obtener resumen del vocabulario
    vocab_summary = get_vocabulary_summary()
    if vocab_summary:
        print(f"   Configuración: {vocab_summary.get('config', {}).get('max_vocabulary_size', 'N/A')}")
    
    # Lista de mensajes con palabras variadas para demostrar aprendizaje ilimitado
    test_messages = [
        # Palabras básicas
        "Hola, ¿cómo estás hoy?",
        "Necesito ayuda con mi pedido",
        "Quisiera agendar una cita para mañana",
        
        # Palabras técnicas
        "El algoritmo de machine learning necesita optimización",
        "La implementación del microservicio requiere refactoring",
        "El deployment en Kubernetes está configurado correctamente",
        
        # Palabras especializadas
        "El neurocirujano realizó la operación con precisión milimétrica",
        "La criptografía asimétrica utiliza claves públicas y privadas",
        "La fotosíntesis es el proceso biológico fundamental",
        
        # Palabras largas y complejas
        "La electroencefalografía muestra actividad cerebral normal",
        "El neumonoultramicroscopiosilicovolcanoconiosis es una enfermedad",
        "La supercalifragilisticexpialidocious es una palabra inventada",
        
        # Expresiones complejas
        "Me gustaría solicitar información sobre los procedimientos administrativos",
        "El sistema de gestión integral requiere actualización inmediata",
        "La implementación de la metodología ágil ha mejorado la productividad",
        
        # Palabras de diferentes idiomas (que el chatbot puede aprender)
        "El software tiene un bug que necesita fixing",
        "El meeting está programado para las 3 PM",
        "El feedback del cliente fue muy positivo",
        
        # Palabras con números y caracteres especiales
        "El producto v2.0 tiene mejoras significativas",
        "La API REST utiliza autenticación OAuth2",
        "El código está en el branch feature/new-version",
        
        # Palabras muy específicas
        "La blockchain utiliza tecnología de consenso distribuido",
        "El machine learning implementa redes neuronales convolucionales",
        "La inteligencia artificial utiliza procesamiento de lenguaje natural"
    ]
    
    print(f"\n📝 Enviando {len(test_messages)} mensajes con palabras variadas...")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i:2d}. ", end="")
        result = send_message_and_learn(message, f"demo_user_{i}")
        time.sleep(0.5)  # Pausa entre mensajes
    
    # Mostrar estadísticas finales
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 60)
    
    final_stats = get_learning_stats()
    if final_stats:
        print(f"📚 Total de palabras aprendidas: {final_stats.get('total_words', 0)}")
        print(f"💬 Total de expresiones aprendidas: {final_stats.get('total_expressions', 0)}")
        print(f"📈 Palabras aprendidas hoy: {final_stats.get('today_words', 0)}")
        print(f"📈 Expresiones aprendidas hoy: {final_stats.get('today_expressions', 0)}")
        
        # Mostrar progreso
        if initial_stats:
            show_learning_progress(initial_stats, final_stats)
    
    # Verificar que no hay límites
    vocab_final = get_vocabulary_summary()
    if vocab_final:
        config = vocab_final.get('config', {})
        max_size = config.get('max_vocabulary_size', 'N/A')
        print(f"\n🎯 Configuración de límite: {max_size}")
        if max_size == 0 or max_size == 'ilimitado':
            print("✅ Sistema configurado para aprendizaje ilimitado")
        else:
            print(f"⚠️ Sistema tiene límite de {max_size} palabras")

def interactive_demo():
    """Demo interactivo donde el usuario puede escribir mensajes"""
    print("\n🎮 DEMO INTERACTIVO")
    print("=" * 40)
    print("Escribe mensajes y ve cómo el chatbot aprende.")
    print("Escribe 'salir' para terminar.")
    print("=" * 40)
    
    if not check_server_health():
        return
    
    # Obtener estadísticas iniciales
    initial_stats = get_learning_stats()
    
    while True:
        try:
            message = input("\n💬 Tu mensaje: ").strip()
            
            if message.lower() in ['salir', 'exit', 'quit']:
                break
            
            if not message:
                continue
            
            # Enviar mensaje
            result = send_message_and_learn(message, "interactive_user")
            
            # Mostrar estadísticas actuales
            current_stats = get_learning_stats()
            if current_stats and initial_stats:
                words_diff = current_stats.get('total_words', 0) - initial_stats.get('total_words', 0)
                print(f"📈 Palabras nuevas desde el inicio: +{words_diff}")
                print(f"📊 Total actual: {current_stats.get('total_words', 0)} palabras")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo terminado por el usuario")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🧠 SISTEMA DE APRENDIZAJE ILIMITADO")
    print("=" * 50)
    print("Este demo muestra cómo el chatbot puede aprender")
    print("TODAS las palabras sin límites.")
    print("=" * 50)
    
    while True:
        print("\n🎯 Selecciona una opción:")
        print("1. Demo automático (mensajes predefinidos)")
        print("2. Demo interactivo (escribe tus propios mensajes)")
        print("3. Salir")
        
        try:
            choice = input("\nTu elección (1-3): ").strip()
            
            if choice == "1":
                demonstrate_unlimited_learning()
            elif choice == "2":
                interactive_demo()
            elif choice == "3":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida. Intenta de nuevo.")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 