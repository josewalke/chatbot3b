#!/usr/bin/env python3
"""
Demostración del Sistema de Corrección Ortográfica
Muestra cómo el chatbot maneja errores de escritura y variaciones
"""

import requests
import json
import time

def check_server_health():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print("❌ Servidor no responde correctamente")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def test_spell_checker():
    """Probar el corrector ortográfico con diferentes tipos de errores"""
    print("\n🔍 Probando Sistema de Corrección Ortográfica")
    print("=" * 60)
    
    # Casos de prueba con errores comunes en español
    test_cases = [
        # Errores de acentuación
        ("hola", "Hola"),
        ("como estas", "¿Cómo estás?"),
        ("telefono", "teléfono"),
        ("espanol", "español"),
        ("nino", "niño"),
        
        # Errores de ortografía común
        ("baca", "vaca"),
        ("bamos", "vamos"),
        ("sienpre", "siempre"),
        ("grasias", "gracias"),
        ("jente", "gente"),
        
        # Errores de letras dobles
        ("llamar", "llamar"),
        ("yamar", "llamar"),
        ("cayado", "callado"),
        
        # Errores de H muda
        ("ola", "hola"),
        ("acer", "hacer"),
        ("asta", "hasta"),
        
        # Errores de Z/S
        ("caza", "casa"),
        ("pazaro", "pájaro"),
        
        # Errores de X/S
        ("exito", "éxito"),
        ("examen", "examen"),
        
        # Palabras técnicas con errores
        ("tecnologia", "tecnología"),
        ("informacion", "información"),
        ("comunicacion", "comunicación"),
        
        # Palabras largas con errores
        ("supercalifragilisticoespialidoso", "supercalifragilísticoespialidoso"),
        ("electroencefalografista", "electroencefalografista"),
    ]
    
    total_tests = len(test_cases)
    successful_corrections = 0
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}/{total_tests}: '{input_text}'")
        
        try:
            # Enviar mensaje al chatbot
            response = requests.post(
                "http://localhost:8000/chat",
                json={"message": input_text, "user_id": "spell_test"}
            )
            
            if response.status_code == 200:
                data = response.json()
                corrections = data.get('spelling_corrections', [])
                
                if corrections:
                    print(f"   ✅ Correcciones encontradas:")
                    for correction in corrections:
                        original = correction['original']
                        suggestions = correction['suggestions']
                        confidence = correction['confidence']
                        error_type = correction['error_type']
                        
                        print(f"      • '{original}' -> {suggestions[:3]} (confianza: {confidence:.2f}, tipo: {error_type})")
                    
                    successful_corrections += 1
                else:
                    print(f"   ⚠️  No se encontraron correcciones")
                    
            else:
                print(f"   ❌ Error en la respuesta: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error en test: {e}")
        
        time.sleep(0.5)  # Pausa entre tests
    
    print(f"\n📊 Resultados:")
    print(f"   • Tests completados: {total_tests}")
    print(f"   • Correcciones exitosas: {successful_corrections}")
    print(f"   • Tasa de éxito: {(successful_corrections/total_tests)*100:.1f}%")

def test_individual_spell_check():
    """Probar verificación individual de palabras"""
    print("\n🔤 Verificación Individual de Palabras")
    print("=" * 50)
    
    words_to_check = [
        "hola", "telefono", "espanol", "baca", "sienpre",
        "grasias", "jente", "yamar", "acer", "caza"
    ]
    
    for word in words_to_check:
        try:
            response = requests.post(
                "http://localhost:8000/spelling/check",
                params={"word": word}
            )
            
            if response.status_code == 200:
                data = response.json()
                is_correct = data['is_correct']
                suggestions = data.get('suggestions', [])
                confidence = data.get('confidence', 0.0)
                
                status = "✅" if is_correct else "❌"
                print(f"{status} '{word}': {suggestions[:3]} (confianza: {confidence:.2f})")
            else:
                print(f"❌ Error verificando '{word}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con '{word}': {e}")
        
        time.sleep(0.3)

def show_spelling_stats():
    """Mostrar estadísticas del corrector ortográfico"""
    print("\n📈 Estadísticas del Corrector Ortográfico")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/spelling/stats")
        
        if response.status_code == 200:
            stats = response.json()
            
            print(f"   • Total de variaciones: {stats.get('total_variations', 0)}")
            print(f"   • Palabras únicas: {stats.get('unique_words', 0)}")
            print(f"   • Similitud promedio: {stats.get('avg_similarity', 0.0):.2f}")
            
            variations = stats.get('spelling_variations', {})
            if variations:
                print(f"   • Frecuencia total: {variations.get('total_frequency', 0)}")
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_learning_variations():
    """Probar aprendizaje de nuevas variaciones"""
    print("\n🎓 Aprendizaje de Nuevas Variaciones")
    print("=" * 50)
    
    variations_to_learn = [
        ("hola", "ola"),
        ("teléfono", "telefono"),
        ("español", "espanol"),
        ("gracias", "grasias"),
        ("gente", "jente")
    ]
    
    for correct_word, variation in variations_to_learn:
        try:
            response = requests.post(
                "http://localhost:8000/spelling/learn",
                params={
                    "correct_word": correct_word,
                    "variation": variation,
                    "error_type": "demo_test"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Aprendida: '{variation}' -> '{correct_word}'")
            else:
                print(f"❌ Error aprendiendo '{variation}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con '{variation}': {e}")
        
        time.sleep(0.3)

def interactive_spell_test():
    """Modo interactivo para probar el corrector"""
    print("\n🎮 Modo Interactivo - Corrector Ortográfico")
    print("=" * 50)
    print("Escribe palabras con errores para ver las correcciones")
    print("Escribe 'salir' para terminar")
    
    while True:
        try:
            word = input("\n📝 Palabra a verificar: ").strip()
            
            if word.lower() == 'salir':
                break
            
            if not word:
                continue
            
            response = requests.post(
                "http://localhost:8000/spelling/check",
                params={"word": word}
            )
            
            if response.status_code == 200:
                data = response.json()
                is_correct = data['is_correct']
                suggestions = data.get('suggestions', [])
                confidence = data.get('confidence', 0.0)
                error_type = data.get('error_type', 'unknown')
                
                if is_correct:
                    print(f"✅ '{word}' está correcta")
                else:
                    print(f"❌ '{word}' tiene errores:")
                    print(f"   • Sugerencias: {suggestions[:5]}")
                    print(f"   • Confianza: {confidence:.2f}")
                    print(f"   • Tipo de error: {error_type}")
            else:
                print(f"❌ Error en la verificación")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal de demostración"""
    print("🤖 Demostración del Sistema de Corrección Ortográfica")
    print("=" * 70)
    print("Este sistema hace que el chatbot sea más robusto")
    print("cuando aprende de fuentes correctas como la RAE")
    print()
    
    # Verificar servidor
    if not check_server_health():
        print("\n💡 Asegúrate de que el servidor esté ejecutándose:")
        print("   python backend/start_optimized.py")
        return
    
    # Ejecutar tests
    test_spell_checker()
    test_individual_spell_check()
    show_spelling_stats()
    test_learning_variations()
    
    # Modo interactivo
    print("\n" + "="*70)
    interactive_spell_test()
    
    print("\n🎉 ¡Demostración completada!")
    print("\n💡 El chatbot ahora puede:")
    print("   • Detectar errores de escritura")
    print("   • Sugerir correcciones")
    print("   • Aprender variaciones ortográficas")
    print("   • Ser más tolerante con errores comunes")

if __name__ == "__main__":
    main() 