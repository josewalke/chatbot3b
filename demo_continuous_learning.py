#!/usr/bin/env python3
"""
Demostración del Sistema de Aprendizaje Continuo
Muestra cómo el chatbot aprende automáticamente en segundo plano
"""
import requests
import time
import json
from datetime import datetime

def check_server_health():
    """Verificar que el servidor esté corriendo"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Servidor conectado correctamente")
            return True
        else:
            print("❌ Servidor no responde correctamente")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("💡 Ejecuta: python backend/start_optimized.py")
        return False

def start_continuous_learning():
    """Iniciar el aprendizaje continuo"""
    try:
        print("🚀 Iniciando aprendizaje continuo...")
        
        response = requests.post("http://localhost:8000/continuous-learning/start")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Aprendizaje continuo iniciado")
            print(f"   📊 Estado: {'Ejecutándose' if result['is_running'] else 'Detenido'}")
            print(f"   ⏰ Intervalo: {result['interval_minutes']} minutos")
            return True
        else:
            print(f"❌ Error iniciando aprendizaje: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_learning_stats():
    """Mostrar estadísticas del aprendizaje"""
    try:
        response = requests.get("http://localhost:8000/continuous-learning/stats")
        
        if response.status_code == 200:
            stats = response.json()
            
            print("\n📊 **Estadísticas del Aprendizaje Continuo**")
            print("=" * 50)
            
            learning_stats = stats['continuous_learning_stats']
            config = stats['config']
            
            print(f"🔄 Estado: {'✅ Ejecutándose' if stats['is_running'] else '⏸️ Detenido'}")
            print(f"📈 Sesiones totales: {learning_stats['total_sessions']}")
            print(f"📚 Palabras aprendidas: {learning_stats['total_words_learned']}")
            print(f"💬 Expresiones aprendidas: {learning_stats['total_expressions_learned']}")
            print(f"⏱️ Duración promedio: {learning_stats['avg_duration_seconds']:.1f} segundos")
            print(f"❌ Sesiones con error: {learning_stats['error_sessions']}")
            
            if learning_stats['last_training']:
                print(f"🕒 Última sesión: {learning_stats['last_training']}")
            
            if learning_stats['next_training_in_minutes']:
                print(f"⏰ Próxima sesión en: {learning_stats['next_training_in_minutes']} minutos")
            
            print("\n⚙️ **Configuración**")
            print(f"   📄 Archivos de texto: {'✅' if config['enable_text_files'] else '❌'}")
            print(f"   🌐 APIs: {'✅' if config['enable_api_learning'] else '❌'}")
            print(f"   🤖 Datos sintéticos: {'✅' if config['enable_synthetic_data'] else '❌'}")
            print(f"   📚 Corpus español: {'✅' if config['enable_spanish_corpus'] else '❌'}")
            
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_chat_with_learning():
    """Probar el chat mientras aprende"""
    test_messages = [
        "Hola, necesito ayuda con mi pedido",
        "¿Cuál es el precio de este producto?",
        "Me gustaría agendar una cita para mañana",
        "Tengo un problema técnico con mi cuenta",
        "¿Pueden ayudarme con la configuración?",
        "Muchas gracias por tu asistencia"
    ]
    
    print("\n💬 **Probando chat con aprendizaje automático**")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "message": message,
                    "user_id": f"demo_user_{i}"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n👤 **Mensaje {i}**: '{message}'")
                print(f"🤖 **Respuesta**: '{result['response']}'")
                print(f"📚 **Aprendido**: {result['learned_words']} palabras, {result['learned_expressions']} expresiones")
                print(f"📊 **Total vocabulario**: {result['total_vocabulary']} palabras")
                
                if result['spelling_corrections']:
                    print("   🔍 **Correcciones ortográficas**:")
                    for correction in result['spelling_corrections']:
                        print(f"      '{correction['original']}' → {correction['suggestions']}")
                
            else:
                print(f"❌ Error en chat {i}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con mensaje {i}: {e}")
        
        time.sleep(1)  # Pausa entre mensajes

def monitor_learning_progress():
    """Monitorear el progreso del aprendizaje"""
    print("\n👀 **Monitoreando progreso del aprendizaje...**")
    print("Presiona Ctrl+C para detener")
    print("=" * 50)
    
    try:
        while True:
            show_learning_stats()
            print("\n⏰ Esperando 30 segundos...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido")

def configure_learning():
    """Configurar el aprendizaje continuo"""
    print("\n⚙️ **Configurando aprendizaje continuo**")
    print("=" * 40)
    
    try:
        # Configurar para aprendizaje más frecuente (15 minutos)
        config_data = {
            "training_interval_minutes": 15,
            "enable_text_files": True,
            "enable_api_learning": True,
            "enable_synthetic_data": True,
            "enable_spanish_corpus": True
        }
        
        response = requests.post(
            "http://localhost:8000/continuous-learning/config",
            params=config_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Configuración actualizada")
            print(f"   ⏰ Intervalo: {result['config']['training_interval_minutes']} minutos")
            print(f"   📄 Archivos: {'✅' if result['config']['enable_text_files'] else '❌'}")
            print(f"   🌐 APIs: {'✅' if result['config']['enable_api_learning'] else '❌'}")
            print(f"   🤖 Sintéticos: {'✅' if result['config']['enable_synthetic_data'] else '❌'}")
            print(f"   📚 Corpus: {'✅' if result['config']['enable_spanish_corpus'] else '❌'}")
        else:
            print(f"❌ Error configurando: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🎯 **Demostración del Sistema de Aprendizaje Continuo**")
    print("=" * 60)
    
    # Verificar servidor
    if not check_server_health():
        return
    
    # Iniciar aprendizaje continuo
    if start_continuous_learning():
        print("\n✅ El chatbot ahora aprenderá automáticamente")
        print("📚 Fuentes de aprendizaje activadas:")
        print("   • Archivos de texto locales")
        print("   • APIs públicas")
        print("   • Datos sintéticos generados")
        print("   • Corpus español en línea")
        
        # Configurar aprendizaje
        configure_learning()
        
        # Mostrar estadísticas iniciales
        show_learning_stats()
        
        # Probar chat con aprendizaje
        test_chat_with_learning()
        
        # Preguntar si quiere monitorear
        print("\n¿Quieres monitorear el progreso del aprendizaje? (s/n): ", end="")
        try:
            response = input().lower()
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                monitor_learning_progress()
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
    
    else:
        print("❌ No se pudo iniciar el aprendizaje continuo")

if __name__ == "__main__":
    main() 