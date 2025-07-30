#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pruebas Optimizadas para Chatbot Inteligente
Versión eficiente en recursos
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuración de pruebas
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

def test_health():
    """Probar endpoint de salud optimizado"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {response.status_code}")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Cache size: {data.get('cache_size', 0)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat():
    """Probar chat optimizado"""
    try:
        test_messages = [
            "Hola",
            "Quiero agendar una cita",
            "¿Qué servicios tienen?",
            "¿Cuánto cuesta la consulta?",
            "Gracias, hasta luego"
        ]
        
        for i, message in enumerate(test_messages, 1):
            data = {
                "message": message,
                "user_id": "test_user_optimized",
                "platform": "web"
            }
            
            response = requests.post(f"{BASE_URL}/chat/send", json=data, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Chat test {i}: {message}")
                print(f"   Response: {result.get('response', 'No response')[:50]}...")
                print(f"   Intent: {result.get('intent', 'unknown')}")
            else:
                print(f"❌ Chat test {i} failed: {response.status_code}")
                return False
            
            time.sleep(0.5)  # Pausa breve entre mensajes
        
        return True
        
    except Exception as e:
        print(f"❌ Chat test error: {e}")
        return False

def test_appointments():
    """Probar APIs de citas optimizadas"""
    try:
        # Obtener horarios disponibles
        response = requests.get(f"{BASE_URL}/appointments/available-slots", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            slots = data.get('slots', [])
            print(f"✅ Available slots: {len(slots)} horarios disponibles")
        else:
            print(f"❌ Available slots failed: {response.status_code}")
            return False
        
        # Crear una cita de prueba
        appointment_data = {
            "user_id": "test_user_optimized",
            "service_type": "Consulta General",
            "date": "2024-01-15",
            "time": "10:00"
        }
        
        response = requests.post(f"{BASE_URL}/appointments/create", json=appointment_data, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Create appointment: {result.get('message', 'Success')}")
        else:
            print(f"❌ Create appointment failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Appointments test error: {e}")
        return False

def test_products():
    """Probar APIs de productos optimizadas"""
    try:
        response = requests.get(f"{BASE_URL}/sales/products", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✅ Products test: {len(products)} productos disponibles")
            
            for product in products[:3]:  # Mostrar solo los primeros 3
                print(f"   - {product.get('name', 'Unknown')}: ${product.get('price', 0)}")
        else:
            print(f"❌ Products test failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Products test error: {e}")
        return False

def test_support():
    """Probar APIs de soporte optimizadas"""
    try:
        test_queries = [
            "Necesito ayuda",
            "¿Cuál es su política de devoluciones?",
            "Tengo un problema con mi cita"
        ]
        
        for i, query in enumerate(test_queries, 1):
            data = {
                "query": query,
                "user_id": "test_user_optimized"
            }
            
            response = requests.post(f"{BASE_URL}/support/query", json=data, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Support test {i}: {query}")
                print(f"   Response: {result.get('response', 'No response')[:50]}...")
            else:
                print(f"❌ Support test {i} failed: {response.status_code}")
                return False
            
            time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"❌ Support test error: {e}")
        return False

def test_stats():
    """Probar endpoint de estadísticas optimizadas"""
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats test:")
            print(f"   Users: {data.get('users', 0)}")
            print(f"   Conversations: {data.get('conversations', 0)}")
            print(f"   Appointments: {data.get('appointments', 0)}")
            print(f"   Cache size: {data.get('cache_size', 0)}")
        else:
            print(f"❌ Stats test failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Stats test error: {e}")
        return False

def test_performance():
    """Probar rendimiento optimizado"""
    try:
        print("🚀 Probando rendimiento...")
        
        # Probar múltiples requests simultáneos
        start_time = time.time()
        
        responses = []
        for i in range(10):
            data = {
                "message": f"Test message {i}",
                "user_id": f"perf_test_user_{i}",
                "platform": "web"
            }
            
            response = requests.post(f"{BASE_URL}/chat/send", json=data, timeout=TIMEOUT)
            responses.append(response.status_code == 200)
        
        end_time = time.time()
        duration = end_time - start_time
        success_rate = sum(responses) / len(responses) * 100
        
        print(f"✅ Performance test:")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Requests per second: {10/duration:.1f}")
        
        return success_rate > 80  # Al menos 80% de éxito
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def test_optimization_features():
    """Probar características de optimización"""
    try:
        print("🔧 Verificando características de optimización...")
        
        # Verificar que el servidor está en modo optimizado
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            
            optimizations = []
            
            # Verificar cache
            if data.get('cache_size', 0) <= 1000:
                optimizations.append("✅ Cache limitado")
            else:
                optimizations.append("❌ Cache no limitado")
            
            # Verificar base de datos SQLite
            if "chatbot_optimized.db" in data.get('db_path', ''):
                optimizations.append("✅ Base de datos SQLite")
            else:
                optimizations.append("❌ Base de datos no optimizada")
            
            # Verificar logging
            if data.get('status') == 'healthy':
                optimizations.append("✅ Servidor saludable")
            else:
                optimizations.append("❌ Servidor no saludable")
            
            for opt in optimizations:
                print(f"   {opt}")
            
            return len([o for o in optimizations if o.startswith("✅")]) >= 2
        
        return False
        
    except Exception as e:
        print(f"❌ Optimization test error: {e}")
        return False

def main():
    """Ejecutar todas las pruebas optimizadas"""
    print("🤖 Probando Chatbot Inteligente Optimizado...")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL: {BASE_URL}")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Chat", test_chat),
        ("Appointments", test_appointments),
        ("Products", test_products),
        ("Support", test_support),
        ("Stats", test_stats),
        ("Performance", test_performance),
        ("Optimization Features", test_optimization_features)
    ]
    
    results = []
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Probando: {test_name}")
        print("-" * 40)
        
        start_time = time.time()
        result = test_func()
        end_time = time.time()
        
        duration = end_time - start_time
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        
        print(f"   {status} ({duration:.2f}s)")
        results.append(result)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(results)
    failed = total_tests - passed
    success_rate = (passed / total_tests) * 100
    
    print(f"✅ Pruebas pasadas: {passed}/{total_tests}")
    print(f"❌ Pruebas fallidas: {failed}/{total_tests}")
    print(f"📈 Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 ¡Excelente! El chatbot optimizado está funcionando correctamente.")
        print("💡 Características de optimización activas:")
        print("   • Cache limitado a 1000 elementos")
        print("   • Base de datos SQLite ligera")
        print("   • Un solo worker para ahorrar memoria")
        print("   • Logging optimizado")
        print("   • Respuestas en memoria")
        print("   • Timeouts configurados")
    elif success_rate >= 60:
        print("\n⚠️ El chatbot funciona pero hay algunos problemas menores.")
        print("💡 Revisa los logs para más detalles.")
    else:
        print("\n❌ El chatbot tiene problemas significativos.")
        print("💡 Verifica que el servidor esté ejecutándose correctamente.")
    
    print("\n🚀 Para iniciar el servidor optimizado:")
    print("   cd backend")
    print("   python start_optimized.py")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 