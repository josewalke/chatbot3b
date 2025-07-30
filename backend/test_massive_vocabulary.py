#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el Sistema de Vocabulario Masivo
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8000"

def test_massive_vocabulary():
    """Probar el sistema de vocabulario masivo"""
    print("🧪 Probando Sistema de Vocabulario Masivo...")
    
    # 1. Obtener estadísticas del vocabulario masivo
    print("\n📊 1. Obteniendo estadísticas del vocabulario masivo...")
    try:
        response = requests.get(f"{BASE_URL}/vocabulary/massive/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Estadísticas obtenidas:")
            print(f"   - Total de palabras: {stats.get('total_words', 0):,}")
            print(f"   - Disponible: {stats.get('available', False)}")
            if 'categories' in stats:
                print(f"   - Categorías:")
                for category, count in stats['categories'].items():
                    print(f"     • {category.replace('_', ' ').title()}: {count:,}")
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Buscar palabras similares
    print("\n🔍 2. Probando búsqueda de palabras similares...")
    test_words = ["hola", "producto", "cita", "ayuda", "precio", "kiero", "produto"]
    
    for word in test_words:
        try:
            response = requests.post(f"{BASE_URL}/vocabulary/massive/search", 
                                  json={"word": word, "threshold": 0.6})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ '{word}' -> {result.get('total_found', 0)} palabras similares")
                if result.get('similar_words'):
                    top_similar = result['similar_words'][:3]
                    print(f"   Top 3: {[w[0] for w in top_similar]}")
            else:
                print(f"❌ Error buscando '{word}': {response.status_code}")
        except Exception as e:
            print(f"❌ Error buscando '{word}': {e}")
    
    # 3. Expandir vocabulario desde texto
    print("\n📝 3. Probando expansión de vocabulario...")
    test_texts = [
        "Hola, me interesa comprar un producto nuevo",
        "Necesito ayuda con mi cita médica",
        "Quiero saber más sobre los precios y garantías"
    ]
    
    for text in test_texts:
        try:
            response = requests.post(f"{BASE_URL}/vocabulary/massive/expand", 
                                  json={"text": text})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Texto: '{text[:50]}...'")
                print(f"   - Nuevas palabras: {result.get('new_words_added', 0)}")
                print(f"   - Total palabras: {result.get('total_words', 0):,}")
            else:
                print(f"❌ Error expandiendo vocabulario: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 4. Aprender desde conversación
    print("\n🧠 4. Probando aprendizaje desde conversación...")
    test_conversation = [
        "Hola, ¿cómo estás?",
        "Me interesa saber más sobre los productos",
        "¿Cuáles son los precios?",
        "Gracias por la información",
        "¿Tienen garantía?"
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/vocabulary/massive/learn", 
                              json={"conversation": test_conversation})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversación procesada:")
            print(f"   - Longitud: {result.get('conversation_length', 0)} mensajes")
            print(f"   - Nuevas palabras: {result.get('new_words_added', 0)}")
            print(f"   - Total palabras: {result.get('total_words', 0):,}")
        else:
            print(f"❌ Error procesando conversación: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Probar chat con vocabulario masivo
    print("\n💬 5. Probando chat con vocabulario masivo...")
    test_messages = [
        "hola",
        "kiero saber mas del produto",
        "me interesa la cita",
        "ayuda con el precio",
        "gracias por todo"
    ]
    
    for message in test_messages:
        try:
            response = requests.post(f"{BASE_URL}/chat/send", 
                                  json={"message": message, "user_id": "test_user"})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Mensaje: '{message}'")
                print(f"   - Intención: {result.get('intent', 'unknown')}")
                print(f"   - Respuesta: {result.get('message', '')[:100]}...")
            else:
                print(f"❌ Error enviando mensaje: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Pruebas del Sistema de Vocabulario Masivo completadas!")

def test_vocabulary_learning():
    """Probar el aprendizaje automático del vocabulario"""
    print("\n🧠 Probando Aprendizaje Automático del Vocabulario...")
    
    # Simular una conversación completa
    conversation_messages = [
        "Hola, ¿cómo estás?",
        "Me interesa comprar un producto",
        "¿Cuál es el precio?",
        "¿Tienen garantía?",
        "Perfecto, gracias"
    ]
    
    user_id = "learning_test_user"
    
    for i, message in enumerate(conversation_messages):
        try:
            print(f"\n📝 Mensaje {i+1}: '{message}'")
            response = requests.post(f"{BASE_URL}/chat/send", 
                                  json={"message": message, "user_id": user_id})
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Intención: {result.get('intent', 'unknown')}")
                print(f"   ✅ Respuesta: {result.get('message', '')[:80]}...")
                
                # Pequeña pausa para simular conversación real
                time.sleep(0.5)
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Prueba de aprendizaje completada!")

def main():
    """Función principal"""
    print("🚀 Iniciando Pruebas del Sistema de Vocabulario Masivo...")
    
    # Verificar que el servidor esté funcionando
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
        else:
            print("❌ Servidor no responde correctamente")
            return
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return
    
    # Ejecutar pruebas
    test_massive_vocabulary()
    test_vocabulary_learning()
    
    print("\n🎉 Todas las pruebas completadas exitosamente!")

if __name__ == "__main__":
    main() 