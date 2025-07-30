#!/usr/bin/env python3
"""
Monitor del Sistema de Aprendizaje Continuo
Monitorea el progreso del aprendizaje en tiempo real
"""
import requests
import time
import json
from datetime import datetime, timedelta
import os

def clear_screen():
    """Limpiar pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_learning_stats():
    """Obtener estadísticas del aprendizaje"""
    try:
        response = requests.get("http://localhost:8000/continuous-learning/stats")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return None

def format_duration(seconds):
    """Formatear duración en formato legible"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def format_time_ago(timestamp_str):
    """Formatear tiempo transcurrido"""
    if not timestamp_str:
        return "Nunca"
    
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timestamp.tzinfo)
        diff = now - timestamp
        
        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}s"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m"
        else:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h"
    except:
        return "Desconocido"

def display_stats(stats, start_time):
    """Mostrar estadísticas formateadas"""
    clear_screen()
    
    print("🎯 **Monitor del Sistema de Aprendizaje Continuo**")
    print("=" * 60)
    print(f"🕒 Iniciado: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Actualizado: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    if not stats:
        print("❌ No se pueden obtener estadísticas")
        return
    
    learning_stats = stats['continuous_learning_stats']
    config = stats['config']
    
    # Estado del sistema
    status = "✅ EJECUTÁNDOSE" if stats['is_running'] else "⏸️ DETENIDO"
    print(f"🔄 Estado del Sistema: {status}")
    print()
    
    # Estadísticas principales
    print("📊 **Estadísticas Principales**")
    print(f"   📈 Sesiones totales: {learning_stats['total_sessions']}")
    print(f"   📚 Palabras aprendidas: {learning_stats['total_words_learned']:,}")
    print(f"   💬 Expresiones aprendidas: {learning_stats['total_expressions_learned']:,}")
    print(f"   ⏱️ Duración promedio: {format_duration(learning_stats['avg_duration_seconds'])}")
    print(f"   ❌ Sesiones con error: {learning_stats['error_sessions']}")
    print()
    
    # Información de tiempo
    print("⏰ **Información de Tiempo**")
    if learning_stats['last_training']:
        last_training = format_time_ago(learning_stats['last_training'])
        print(f"   🕒 Última sesión: {last_training} atrás")
    
    if learning_stats['next_training_in_minutes']:
        next_training = learning_stats['next_training_in_minutes']
        print(f"   ⏰ Próxima sesión: en {next_training} minutos")
    
    print(f"   ⏱️ Intervalo configurado: {config['training_interval_minutes']} minutos")
    print()
    
    # Configuración
    print("⚙️ **Configuración Activa**")
    print(f"   📄 Archivos de texto: {'✅' if config['enable_text_files'] else '❌'}")
    print(f"   🌐 APIs públicas: {'✅' if config['enable_api_learning'] else '❌'}")
    print(f"   🤖 Datos sintéticos: {'✅' if config['enable_synthetic_data'] else '❌'}")
    print(f"   📚 Corpus español: {'✅' if config['enable_spanish_corpus'] else '❌'}")
    print()
    
    # Progreso del día
    print("📅 **Progreso del Día**")
    today = datetime.now().date()
    today_words = learning_stats.get('today_words', 0)
    today_expressions = learning_stats.get('today_expressions', 0)
    print(f"   📚 Palabras hoy: {today_words}")
    print(f"   💬 Expresiones hoy: {today_expressions}")
    print(f"   📈 Total aprendido hoy: {today_words + today_expressions}")
    print()
    
    # Rendimiento
    print("⚡ **Rendimiento**")
    if learning_stats['total_sessions'] > 0:
        success_rate = ((learning_stats['total_sessions'] - learning_stats['error_sessions']) / learning_stats['total_sessions']) * 100
        print(f"   🎯 Tasa de éxito: {success_rate:.1f}%")
    
    if learning_stats['avg_duration_seconds'] > 0:
        words_per_minute = (learning_stats['total_words_learned'] / learning_stats['total_sessions']) / (learning_stats['avg_duration_seconds'] / 60)
        print(f"   📚 Palabras/minuto: {words_per_minute:.1f}")
    
    print()
    print("💡 Presiona Ctrl+C para detener el monitor")
    print("=" * 60)

def monitor_learning():
    """Monitorear el aprendizaje continuo"""
    start_time = datetime.now()
    
    print("🎯 **Monitor del Sistema de Aprendizaje Continuo**")
    print("=" * 60)
    print("Iniciando monitor...")
    print("Presiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        while True:
            stats = get_learning_stats()
            display_stats(stats, start_time)
            time.sleep(10)  # Actualizar cada 10 segundos
            
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido por el usuario")
        print("👋 ¡Hasta luego!")

def show_help():
    """Mostrar ayuda"""
    print("""
🎯 **Monitor del Sistema de Aprendizaje Continuo**

Uso:
  python monitor_continuous_learning.py

Funciones:
  • Monitoreo en tiempo real del aprendizaje
  • Estadísticas detalladas del sistema
  • Información de rendimiento
  • Estado de configuración

Requisitos:
  • Servidor optimizado ejecutándose
  • Aprendizaje continuo iniciado

Comandos útiles:
  • Iniciar servidor: python backend/start_optimized.py
  • Iniciar aprendizaje: python start_continuous_learning.py
  • Ver estadísticas: curl http://localhost:8000/continuous-learning/stats
""")

def main():
    """Función principal"""
    # Verificar argumentos
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    # Verificar que el servidor esté corriendo
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code != 200:
            print("❌ El servidor no está corriendo")
            print("💡 Ejecuta: python backend/start_optimized.py")
            return
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("💡 Ejecuta: python backend/start_optimized.py")
        return
    
    # Iniciar monitor
    monitor_learning()

if __name__ == "__main__":
    main() 