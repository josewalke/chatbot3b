#!/usr/bin/env python3
"""
Script de prueba para demostrar la actualización automática de vocabulario
"""

import requests
import json
import time

def test_vocabulary_update():
    """Probar la actualización de vocabulario"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Probando actualización automática de vocabulario...")
    print("=" * 60)
    
    # 1. Agregar nueva corrección ortográfica
    print("\n1️⃣ Agregando corrección ortográfica...")
    new_correction = {
        "type": "spelling_corrections",
        "data": {
            "servicio": ["servisio", "servicio", "servisio", "servicio"],
            "atención": ["atencion", "atención", "atencion", "atención"]
        }
    }
    
    response = requests.post(f"{base_url}/vocabulary/update", json=new_correction)
    if response.status_code == 200:
        print("✅ Corrección ortográfica agregada exitosamente")
    else:
        print(f"❌ Error: {response.text}")
    
    # 2. Agregar nuevos patrones de intención
    print("\n2️⃣ Agregando patrones de intención...")
    new_patterns = {
        "type": "intent_patterns",
        "data": {
            "greeting": ["buenos días", "buenas tardes", "saludos"],
            "products": ["qué productos", "muéstrame", "catalogo"]
        }
    }
    
    response = requests.post(f"{base_url}/vocabulary/update", json=new_patterns)
    if response.status_code == 200:
        print("✅ Patrones de intención agregados exitosamente")
    else:
        print(f"❌ Error: {response.text}")
    
    # 3. Agregar nuevas plantillas de respuesta
    print("\n3️⃣ Agregando plantillas de respuesta...")
    new_templates = {
        "type": "response_templates",
        "data": {
            "greeting": [
                "¡Hola! 🌟 ¡Qué gusto verte! ¿En qué puedo ayudarte hoy?",
                "¡Hola! ✨ ¡Bienvenido! Estoy aquí para hacer tu día más fácil."
            ],
            "product_info": [
                "¡Perfecto! 😊 Te cuento todo sobre {product}:\n\n📦 **Descripción:** {description}\n💰 **Precio:** ${price}\n🔒 **Garantía:** 1 año\n\n¿Te gustaría comprarlo?"
            ]
        }
    }
    
    response = requests.post(f"{base_url}/vocabulary/update", json=new_templates)
    if response.status_code == 200:
        print("✅ Plantillas de respuesta agregadas exitosamente")
    else:
        print(f"❌ Error: {response.text}")
    
    # 4. Recargar vocabulario
    print("\n4️⃣ Recargando vocabulario...")
    response = requests.post(f"{base_url}/vocabulary/reload")
    if response.status_code == 200:
        print("✅ Vocabulario recargado exitosamente")
    else:
        print(f"❌ Error: {response.text}")
    
    # 5. Obtener estadísticas
    print("\n5️⃣ Obteniendo estadísticas...")
    response = requests.get(f"{base_url}/vocabulary/stats")
    if response.status_code == 200:
        stats = response.json()
        print("📊 Estadísticas actuales:")
        for vocab_type, info in stats.items():
            print(f"  • {vocab_type}: {info.get('size', 'N/A')} elementos")
            print(f"    Última actualización: {info.get('last_updated', 'N/A')}")
    else:
        print(f"❌ Error: {response.text}")
    
    # 6. Probar el chatbot con nuevas palabras
    print("\n6️⃣ Probando el chatbot con nuevas palabras...")
    
    test_messages = [
        "servisio",  # Debería corregirse a "servicio"
        "buenos días",  # Nuevo patrón de saludo
        "muéstrame productos",  # Nuevo patrón de productos
        "atencion al cliente"  # Debería corregirse a "atención al cliente"
    ]
    
    for message in test_messages:
        print(f"\n📝 Probando: '{message}'")
        response = requests.post(f"{base_url}/chat/send", json={
            "message": message,
            "user_id": "test_user"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Respuesta: {data.get('message', 'Sin respuesta')[:100]}...")
        else:
            print(f"❌ Error: {response.text}")

def test_bulk_update():
    """Probar actualización masiva desde archivo"""
    
    print("\n🔄 Probando actualización masiva desde archivo...")
    
    # Crear archivo de prueba
    test_data = {
        "spelling_corrections": {
            "prueba": ["pruva", "prueba", "pruva", "prueba"],
            "test": ["test", "test", "test", "test"]
        },
        "intent_patterns": {
            "test": ["probar", "testear", "verificar"]
        },
        "response_templates": {
            "test": [
                "¡Esto es una prueba! 🧪",
                "¡Funcionando correctamente! ✅"
            ]
        }
    }
    
    with open("test_update.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print("✅ Archivo de prueba creado: test_update.json")
    
    # Aquí podrías usar el vocabulary_manager para hacer la actualización masiva
    print("💡 Para actualización masiva, usa: python vocabulary_manager.py")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de actualización de vocabulario...")
    
    try:
        test_vocabulary_update()
        test_bulk_update()
        
        print("\n🎉 ¡Pruebas completadas!")
        print("\n📋 Para usar el administrador interactivo:")
        print("   python vocabulary_manager.py")
        
        print("\n📋 Para actualización masiva:")
        print("   python vocabulary_manager.py")
        print("   Selecciona opción 6 y usa: example_vocabulary_update.json")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:8000") 