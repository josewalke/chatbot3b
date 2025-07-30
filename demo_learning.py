#!/usr/bin/env python3
"""
Demostración del Sistema de Aprendizaje Optimizado
Muestra en tiempo real cómo el chatbot aprende nuevas palabras y expresiones
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"

def print_header():
    """Imprimir encabezado de la demostración"""
    print("🧠 DEMOSTRACIÓN DEL SISTEMA DE APRENDIZAJE OPTIMIZADO")
    print("=" * 60)
    print("🎯 Este script demuestra cómo el chatbot aprende continuamente")
    print("📚 Cada mensaje enseña nuevas palabras y expresiones al bot")
    print("📊 Se muestran estadísticas en tiempo real")
    print("=" * 60)
    print()

def check_server():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Servidor funcionando correctamente")
            print(f"📊 Estado: {data.get('status', 'unknown')}")
            print(f"⏰ Última verificación: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose:")
        print("   python backend/start_optimized.py")
        return False

def get_initial_stats():
    """Obtener estadísticas iniciales"""
    try:
        response = requests.get(f"{BASE_URL}/learning/stats", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas iniciales: {e}")
        return {}

def send_message_and_learn(message, user_id="demo_user"):
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
            print(f"🎯 Intención detectada: {data['intent']}")
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

def show_learning_progress(initial_stats, current_stats):
    """Mostrar progreso del aprendizaje"""
    print("\n📈 PROGRESO DEL APRENDIZAJE:")
    print("-" * 40)
    
    # Comparar estadísticas
    initial_words = initial_stats.get('total_words', 0)
    current_words = current_stats.get('total_words', 0)
    words_learned = current_words - initial_words
    
    initial_expressions = initial_stats.get('total_expressions', 0)
    current_expressions = current_stats.get('total_expressions', 0)
    expressions_learned = current_expressions - initial_expressions
    
    print(f"📚 Palabras aprendidas en esta sesión: {words_learned}")
    print(f"💬 Expresiones aprendidas en esta sesión: {expressions_learned}")
    print(f"📊 Total de palabras en vocabulario: {current_words}")
    print(f"📊 Total de expresiones en vocabulario: {current_expressions}")
    
    # Mostrar palabras más frecuentes
    if current_stats.get('top_words'):
        print(f"\n🔤 Palabras más frecuentes:")
        for i, word_data in enumerate(current_stats['top_words'][:5], 1):
            print(f"   {i}. '{word_data['word']}': {word_data['frequency']} veces")
    
    # Mostrar expresiones más frecuentes
    if current_stats.get('top_expressions'):
        print(f"\n💬 Expresiones más frecuentes:")
        for i, expr_data in enumerate(current_stats['top_expressions'][:5], 1):
            print(f"   {i}. '{expr_data['expression']}': {expr_data['frequency']} veces")

def search_similar_words(word):
    """Buscar palabras similares"""
    try:
        response = requests.post(
            f"{BASE_URL}/learning/search",
            params={"word": word, "limit": 3},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            similar_words = data.get('similar_words', [])
            if similar_words:
                print(f"🔍 Palabras similares a '{word}': {', '.join(similar_words)}")
            else:
                print(f"🔍 No se encontraron palabras similares a '{word}'")
        else:
            print(f"❌ Error buscando palabras similares: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")

def interactive_demo():
    """Demostración interactiva"""
    print("\n🎮 DEMOSTRACIÓN INTERACTIVA")
    print("=" * 40)
    print("💡 Escribe mensajes para que el chatbot aprenda")
    print("💡 Escribe 'stats' para ver estadísticas")
    print("💡 Escribe 'search <palabra>' para buscar similares")
    print("💡 Escribe 'quit' para salir")
    print("=" * 40)
    
    while True:
        try:
            user_input = input("\n💬 Tu mensaje: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 ¡Hasta luego!")
                break
            elif user_input.lower() == 'stats':
                # Mostrar estadísticas
                stats_response = requests.get(f"{BASE_URL}/learning/stats", timeout=10)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print(f"\n📊 ESTADÍSTICAS ACTUALES:")
                    print(f"   - Total palabras: {stats.get('total_words', 0)}")
                    print(f"   - Total expresiones: {stats.get('total_expressions', 0)}")
                    print(f"   - Aprendido hoy: {stats.get('total_learned_today', 0)}")
                continue
            elif user_input.lower().startswith('search '):
                # Buscar palabras similares
                word = user_input[7:].strip()
                if word:
                    search_similar_words(word)
                continue
            elif not user_input:
                continue
            
            # Enviar mensaje y aprender
            result = send_message_and_learn(user_input)
            if result:
                print("✅ Mensaje procesado y aprendido")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def run_demo_scenarios():
    """Ejecutar escenarios de demostración"""
    print("\n🎬 ESCENARIOS DE DEMOSTRACIÓN")
    print("=" * 40)
    
    # Escenarios de prueba
    scenarios = [
        {
            "name": "Saludos y cortesía",
            "messages": [
                "Hola, ¿cómo estás?",
                "Buenos días, espero que tengas un buen día",
                "Gracias por tu ayuda, eres muy amable",
                "Por favor, ¿puedes ayudarme?"
            ]
        },
        {
            "name": "Servicios y productos",
            "messages": [
                "Necesito información sobre sus servicios",
                "¿Cuál es el precio de la consulta?",
                "Me gustaría agendar una cita",
                "¿Tienen descuentos disponibles?"
            ]
        },
        {
            "name": "Soporte y problemas",
            "messages": [
                "Tengo un problema con mi cuenta",
                "Necesito ayuda urgente",
                "¿Pueden resolver mi queja?",
                "No entiendo cómo funciona esto"
            ]
        },
        {
            "name": "Expresiones complejas",
            "messages": [
                "Me gustaría saber más sobre los productos que ofrecen",
                "¿Podrían darme información detallada sobre los precios?",
                "Necesito cancelar mi cita para mañana",
                "Excelente servicio, muy profesional y eficiente"
            ]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Escenario {i}: {scenario['name']}")
        print("-" * 40)
        
        for j, message in enumerate(scenario['messages'], 1):
            print(f"\n{j}. Enviando: '{message}'")
            result = send_message_and_learn(message, f"demo_user_{i}")
            if result:
                print("✅ Aprendido")
            time.sleep(1)  # Pausa entre mensajes
    
    print("\n✅ Todos los escenarios completados")

def main():
    """Función principal de la demostración"""
    print_header()
    
    # Verificar servidor
    if not check_server():
        return
    
    # Obtener estadísticas iniciales
    print("\n📊 Obteniendo estadísticas iniciales...")
    initial_stats = get_initial_stats()
    if initial_stats:
        print(f"📚 Palabras iniciales: {initial_stats.get('total_words', 0)}")
        print(f"💬 Expresiones iniciales: {initial_stats.get('total_expressions', 0)}")
    
    print("\n" + "=" * 60)
    
    # Preguntar tipo de demostración
    print("🎯 ¿Qué tipo de demostración prefieres?")
    print("1. Escenarios automáticos (recomendado)")
    print("2. Demostración interactiva")
    print("3. Solo estadísticas")
    
    try:
        choice = input("\n💭 Tu elección (1-3): ").strip()
        
        if choice == "1":
            run_demo_scenarios()
        elif choice == "2":
            interactive_demo()
        elif choice == "3":
            pass  # Solo mostrar estadísticas finales
        else:
            print("❌ Opción no válida, ejecutando escenarios automáticos...")
            run_demo_scenarios()
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
        return
    
    # Mostrar estadísticas finales
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 60)
    
    try:
        final_stats = requests.get(f"{BASE_URL}/learning/stats", timeout=10)
        if final_stats.status_code == 200:
            stats = final_stats.json()
            show_learning_progress(initial_stats, stats)
            
            print(f"\n🎯 RESUMEN:")
            print(f"   - El chatbot ha aprendido nuevas palabras y expresiones")
            print(f"   - El vocabulario se ha expandido automáticamente")
            print(f"   - El sistema mantiene un rendimiento optimizado")
            print(f"   - El aprendizaje continúa con cada conversación")
            
        else:
            print("❌ Error obteniendo estadísticas finales")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ¡Demostración completada!")
    print("🚀 El sistema de aprendizaje está funcionando correctamente")
    print("📚 El chatbot mejora continuamente con cada interacción")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1) 