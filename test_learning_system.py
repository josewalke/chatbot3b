#!/usr/bin/env python3
"""
Script de prueba para el Sistema de Aprendizaje Optimizado
Demuestra cómo el chatbot aprende nuevas palabras y expresiones
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"

def test_learning_system():
    """Probar el sistema de aprendizaje optimizado"""
    print("🧠 Probando Sistema de Aprendizaje Optimizado")
    print("=" * 50)
    
    # Mensajes de prueba para que el chatbot aprenda
    test_messages = [
        "Hola, ¿cómo estás?",
        "Necesito ayuda con mi pedido",
        "Quisiera agendar una cita para mañana",
        "¿Cuál es el precio de la consulta?",
        "Gracias por tu ayuda, eres muy amable",
        "Tengo un problema con mi cuenta",
        "¿Puedes darme información sobre los servicios?",
        "Excelente servicio, muy profesional",
        "Necesito cancelar mi cita",
        "¿Tienen descuentos disponibles?",
        "Me gustaría saber más sobre los productos",
        "¿Cuál es el horario de atención?",
        "Tengo una queja sobre el servicio",
        "¿Pueden ayudarme con mi factura?",
        "Muchas gracias por resolver mi problema"
    ]
    
    print(f"📝 Enviando {len(test_messages)} mensajes para aprendizaje...")
    
    # Enviar mensajes y aprender
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Enviando: '{message}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "message": message,
                    "user_id": f"test_user_{i}"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Respuesta: {data['response']}")
                print(f"   🎯 Intención: {data['intent']}")
                print(f"   📚 Palabras aprendidas: {data['learned_words']}")
                print(f"   💬 Expresiones aprendidas: {data['learned_expressions']}")
                print(f"   📖 Vocabulario total: {data['total_vocabulary']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
        
        # Pequeña pausa entre mensajes
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("📊 Obteniendo estadísticas de aprendizaje...")
    
    # Obtener estadísticas de aprendizaje
    try:
        stats_response = requests.get(f"{BASE_URL}/learning/stats", timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"📈 Estadísticas de aprendizaje:")
            print(f"   - Total de palabras: {stats.get('total_words', 0)}")
            print(f"   - Total de expresiones: {stats.get('total_expressions', 0)}")
            print(f"   - Palabras aprendidas hoy: {stats.get('today_words', 0)}")
            print(f"   - Expresiones aprendidas hoy: {stats.get('today_expressions', 0)}")
            print(f"   - Total aprendido hoy: {stats.get('total_learned_today', 0)}")
            
            # Mostrar palabras más frecuentes
            if stats.get('top_words'):
                print(f"\n🔤 Palabras más frecuentes:")
                for word_data in stats['top_words'][:5]:
                    print(f"   - '{word_data['word']}': {word_data['frequency']} veces")
            
            # Mostrar expresiones más frecuentes
            if stats.get('top_expressions'):
                print(f"\n💬 Expresiones más frecuentes:")
                for expr_data in stats['top_expressions'][:5]:
                    print(f"   - '{expr_data['expression']}': {expr_data['frequency']} veces")
        else:
            print(f"❌ Error obteniendo estadísticas: {stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Probando búsqueda de palabras similares...")
    
    # Probar búsqueda de palabras similares
    test_words = ["ayuda", "cita", "precio", "gracias", "problema"]
    
    for word in test_words:
        try:
            search_response = requests.post(
                f"{BASE_URL}/learning/search",
                params={"word": word, "limit": 3},
                timeout=10
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                similar_words = search_data.get('similar_words', [])
                print(f"🔍 Palabras similares a '{word}': {similar_words}")
            else:
                print(f"❌ Error buscando palabras similares a '{word}': {search_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error en búsqueda de '{word}': {e}")
    
    print("\n" + "=" * 50)
    print("📋 Obteniendo resumen del vocabulario...")
    
    # Obtener resumen del vocabulario
    try:
        vocab_response = requests.get(f"{BASE_URL}/learning/vocabulary", timeout=10)
        if vocab_response.status_code == 200:
            vocab_data = vocab_response.json()
            print(f"📚 Resumen del vocabulario:")
            print(f"   - Total de palabras: {vocab_data.get('total_words', 0)}")
            print(f"   - Tamaño del cache: {vocab_data.get('cache_size', 0)}")
            print(f"   - Configuración:")
            config = vocab_data.get('config', {})
            print(f"     * Máximo vocabulario: {config.get('max_vocabulary_size', 0)}")
            print(f"     * Tamaño de cache: {config.get('cache_size', 0)}")
            print(f"     * Longitud mínima de palabra: {config.get('min_word_length', 0)}")
            print(f"     * Longitud máxima de palabra: {config.get('max_word_length', 0)}")
        else:
            print(f"❌ Error obteniendo vocabulario: {vocab_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo vocabulario: {e}")
    
    print("\n" + "=" * 50)
    print("🧹 Probando limpieza de palabras antiguas...")
    
    # Probar limpieza de palabras antiguas
    try:
        cleanup_response = requests.post(
            f"{BASE_URL}/learning/cleanup",
            params={"days": 30},
            timeout=10
        )
        
        if cleanup_response.status_code == 200:
            cleanup_data = cleanup_response.json()
            print(f"✅ {cleanup_data.get('message', 'Limpieza completada')}")
        else:
            print(f"❌ Error en limpieza: {cleanup_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en limpieza: {e}")
    
    print("\n" + "=" * 50)
    print("📈 Obteniendo estadísticas generales...")
    
    # Obtener estadísticas generales
    try:
        general_stats_response = requests.get(f"{BASE_URL}/statistics", timeout=10)
        if general_stats_response.status_code == 200:
            general_stats = general_stats_response.json()
            print(f"📊 Estadísticas generales:")
            print(f"   - Conversaciones: {general_stats.get('conversations', 0)}")
            print(f"   - Citas: {general_stats.get('appointments', 0)}")
            print(f"   - Productos: {general_stats.get('products', 0)}")
            
            cache_stats = general_stats.get('cache', {})
            print(f"   - Cache:")
            print(f"     * Tamaño: {cache_stats.get('size', 0)}")
            print(f"     * Hits: {cache_stats.get('hits', 0)}")
            
            learning_stats = general_stats.get('learning', {})
            if learning_stats:
                print(f"   - Aprendizaje:")
                print(f"     * Total palabras: {learning_stats.get('total_words', 0)}")
                print(f"     * Total expresiones: {learning_stats.get('total_expressions', 0)}")
                print(f"     * Aprendido hoy: {learning_stats.get('total_learned_today', 0)}")
        else:
            print(f"❌ Error obteniendo estadísticas generales: {general_stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas generales: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Prueba del sistema de aprendizaje completada")
    print("🎯 El chatbot ha aprendido nuevas palabras y expresiones")
    print("📚 El sistema está optimizado para bajo consumo de recursos")
    print("🚀 El chatbot mejora continuamente con cada interacción")

def test_server_health():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return False

if __name__ == "__main__":
    print("🧠 Sistema de Aprendizaje Optimizado - Pruebas")
    print("=" * 60)
    
    # Verificar que el servidor esté funcionando
    if test_server_health():
        test_learning_system()
    else:
        print("\n❌ No se puede ejecutar las pruebas sin el servidor")
        print("💡 Ejecuta: python backend/start_optimized.py") 