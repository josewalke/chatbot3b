#!/usr/bin/env python3
"""
Script para iniciar el aprendizaje continuo automáticamente
"""
import requests
import time
import json
from datetime import datetime

def start_continuous_learning():
    """Iniciar el aprendizaje continuo"""
    try:
        print("🚀 Iniciando aprendizaje continuo...")
        
        # Verificar que el servidor esté corriendo
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code != 200:
            print("❌ El servidor no está corriendo. Ejecuta primero: python backend/start_optimized.py")
            return False
        
        # Iniciar aprendizaje continuo
        response = requests.post("http://localhost:8000/continuous-learning/start")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Aprendizaje continuo iniciado correctamente")
            print(f"   📊 Estado: {'Ejecutándose' if result['is_running'] else 'Detenido'}")
            print(f"   ⏰ Intervalo: {result['interval_minutes']} minutos")
            return True
        else:
            print(f"❌ Error iniciando aprendizaje continuo: {response.status_code}")
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

def monitor_learning():
    """Monitorear el aprendizaje continuo"""
    print("\n👀 **Monitoreando aprendizaje continuo...**")
    print("Presiona Ctrl+C para detener")
    print("=" * 50)
    
    try:
        while True:
            show_learning_stats()
            print("\n⏰ Esperando 60 segundos...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido")

def main():
    """Función principal"""
    print("🎯 **Sistema de Aprendizaje Continuo**")
    print("=" * 40)
    
    # Iniciar aprendizaje continuo
    if start_continuous_learning():
        print("\n✅ El chatbot ahora aprenderá automáticamente cada 30 minutos")
        print("📚 Fuentes de aprendizaje:")
        print("   • Archivos de texto locales")
        print("   • APIs públicas")
        print("   • Datos sintéticos generados")
        print("   • Corpus español en línea")
        
        # Mostrar estadísticas iniciales
        show_learning_stats()
        
        # Preguntar si quiere monitorear
        print("\n¿Quieres monitorear el aprendizaje continuo? (s/n): ", end="")
        try:
            response = input().lower()
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                monitor_learning()
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
    
    else:
        print("❌ No se pudo iniciar el aprendizaje continuo")

if __name__ == "__main__":
    main() 