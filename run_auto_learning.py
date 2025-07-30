#!/usr/bin/env python3
"""
Script simple para ejecutar aprendizaje automático
Ejecuta el sistema de aprendizaje automático sin necesidad de configurar Python
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    import asyncio
    from auto_learning import auto_learner
    
    async def main():
        print("🤖 Iniciando aprendizaje automático...")
        print("=" * 50)
        
        # Ejecutar sesión de aprendizaje
        results = await auto_learner.run_full_learning_session()
        
        print(f"\n📊 Resultados:")
        print(f"   • Palabras aprendidas: {results['total_words_learned']:,}")
        print(f"   • Expresiones aprendidas: {results['total_expressions_learned']:,}")
        
        print(f"\n📈 Por fuente:")
        for source, result in results['sources'].items():
            status = result.get('status', 'unknown')
            words = result.get('words_learned', 0)
            expressions = result.get('expressions_learned', 0)
            print(f"   • {source}: {status} ({words} palabras, {expressions} expresiones)")
        
        # Mostrar estadísticas
        stats = auto_learner.get_learning_stats()
        print(f"\n📊 Estadísticas totales:")
        print(f"   • Sesiones: {stats.get('total_sessions', 0)}")
        print(f"   • Total palabras: {stats.get('total_words_learned', 0):,}")
        print(f"   • Total expresiones: {stats.get('total_expressions_learned', 0):,}")
        
        print("\n✅ ¡Aprendizaje completado!")
        print("\n💡 El chatbot ahora tiene más vocabulario y puede responder mejor.")
        
    if __name__ == "__main__":
        asyncio.run(main())
        
except ImportError as e:
    print("❌ Error: No se pueden importar las dependencias.")
    print("💡 Asegúrate de tener Python instalado y ejecutar:")
    print("   pip install -r backend/requirements_optimized.txt")
    print(f"   Error específico: {e}")
    
except Exception as e:
    print(f"❌ Error ejecutando aprendizaje automático: {e}")
    print("💡 Verifica que el servidor esté configurado correctamente.") 