import requests
import json

# URL base del servidor
BASE_URL = "http://localhost:8000"

def test_health():
    """Probar endpoint de salud"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat():
    """Probar chat del chatbot"""
    try:
        data = {
            "message": "Hola, quiero agendar una cita",
            "user_id": "test_user_123"
        }
        response = requests.post(f"{BASE_URL}/chat/send", json=data)
        print(f"✅ Chat test: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_appointments():
    """Probar APIs de citas"""
    try:
        # Obtener citas disponibles
        response = requests.get(f"{BASE_URL}/appointments/available-slots")
        print(f"✅ Available slots: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Crear una cita de prueba
        appointment_data = {
            "user_id": "test_user_123",
            "service_id": 1,
            "date": "2024-01-15",
            "time": "10:00",
            "notes": "Cita de prueba"
        }
        response = requests.post(f"{BASE_URL}/appointments/create", json=appointment_data)
        print(f"✅ Create appointment: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        return True
    except Exception as e:
        print(f"❌ Appointments test failed: {e}")
        return False

def test_products():
    """Probar APIs de productos"""
    try:
        response = requests.get(f"{BASE_URL}/sales/products")
        print(f"✅ Products test: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Products test failed: {e}")
        return False

def test_customer_service():
    """Probar APIs de atención al cliente"""
    try:
        data = {
            "query": "¿Cuál es su política de devoluciones?",
            "user_id": "test_user_123"
        }
        response = requests.post(f"{BASE_URL}/support/query", json=data)
        print(f"✅ Customer service test: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Customer service test failed: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🤖 Probando Chatbot APIs...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Chat", test_chat),
        ("Appointments", test_appointments),
        ("Products", test_products),
        ("Customer Service", test_customer_service)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Probando: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DE LAS PRUEBAS:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Total: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! El chatbot está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()