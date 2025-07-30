#!/usr/bin/env python3
"""
Test específico para errores fonéticos como "escrivir" vs "escribir"
"""
import requests
import json

def test_phonetic_errors():
    """Probar errores fonéticos específicos"""
    
    # Casos de prueba con errores fonéticos
    test_cases = [
        "escrivir",    # V/B error
        "escrivir",    # V/B error  
        "baca",        # B/V error
        "jente",       # J/G error
        "yamar",       # Y/LL error
        "caza",        # Z/S error
        "grasias",     # S/C error
        "ola",         # H muda
        "sienpre",     # I/E error
        "telefono",    # Acentuación
        "espanol",     # Acentuación
        "nino",        # Ñ/N error
    ]
    
    print("🔍 **Probando errores fonéticos específicos**")
    print("=" * 50)
    
    for word in test_cases:
        try:
            # Verificar ortografía
            response = requests.post(
                "http://localhost:8000/spelling/check",
                params={"word": word}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📝 **Palabra**: '{word}'")
                print(f"   ✅ Correcta: {result['is_correct']}")
                
                if not result['is_correct'] and result['suggestions']:
                    print(f"   🔧 Sugerencias: {result['suggestions']}")
                    print(f"   🎯 Confianza: {result['confidence']:.2f}")
                    print(f"   📊 Tipo de error: {result['error_type']}")
                else:
                    print("   ✅ Sin correcciones necesarias")
            else:
                print(f"❌ Error verificando '{word}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con '{word}': {e}")
    
    print("\n" + "=" * 50)

def test_chat_with_errors():
    """Probar el chat con mensajes que contienen errores"""
    
    test_messages = [
        "hola, quiero escrivir un mensaje",
        "necesito ayuda con mi telefono",
        "grasias por la informacion",
        "sienpre me ayuda mucho",
        "ola, como estas?",
        "jente muy amable aqui"
    ]
    
    print("\n💬 **Probando chat con errores ortográficos**")
    print("=" * 50)
    
    for message in test_messages:
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "message": message,
                    "user_id": "test_user"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n👤 **Usuario**: '{message}'")
                print(f"🤖 **Chatbot**: '{result['response']}'")
                
                if result['spelling_corrections']:
                    print("   🔍 **Correcciones detectadas**:")
                    for correction in result['spelling_corrections']:
                        print(f"      '{correction['original']}' → {correction['suggestions']}")
                else:
                    print("   ✅ Sin correcciones necesarias")
            else:
                print(f"❌ Error en chat: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con mensaje '{message}': {e}")

def main():
    """Función principal"""
    print("🎯 **Test de Errores Fonéticos - Sistema de Corrección Ortográfica**")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        health_check = requests.get("http://localhost:8000/health")
        if health_check.status_code != 200:
            print("❌ El servidor no está corriendo. Ejecuta: python backend/start_optimized.py")
            return
    except:
        print("❌ No se puede conectar al servidor. Ejecuta: python backend/start_optimized.py")
        return
    
    print("✅ Servidor conectado correctamente")
    
    # Ejecutar tests
    test_phonetic_errors()
    test_chat_with_errors()
    
    print("\n🎉 **Test completado!**")
    print("\n💡 **Nota**: El sistema maneja automáticamente errores fonéticos como:")
    print("   - B/V (baca → vaca)")
    print("   - G/J (jente → gente)") 
    print("   - LL/Y (yamar → llamar)")
    print("   - H muda (ola → hola)")
    print("   - Acentuación (telefono → teléfono)")

if __name__ == "__main__":
    main() 