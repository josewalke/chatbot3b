"""
Script de configuración para aprendizaje automático
Descarga vocabulario español de la RAE y configura el sistema
"""

import asyncio
import requests
import os
from pathlib import Path
from backend.auto_learning import auto_learner

async def download_spanish_vocabulary():
    """Descargar vocabulario español de la RAE"""
    print("📚 Descargando vocabulario español de la RAE...")
    
    # Crear directorio si no existe
    learning_dir = Path("learning_data")
    learning_dir.mkdir(exist_ok=True)
    
    # URLs del diccionario español
    urls = [
        "https://raw.githubusercontent.com/JorgeDuenasLerin/diccionario-espanol-txt/master/0_palabras_todas.txt",
        "https://raw.githubusercontent.com/JorgeDuenasLerin/diccionario-espanol-txt/master/0_palabras_todas_no_conjugaciones.txt"
    ]
    
    total_words = 0
    
    for i, url in enumerate(urls):
        try:
            print(f"📥 Descargando desde: {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                filename = f"spanish_vocabulary_{i+1}.txt"
                filepath = learning_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                word_count = len(response.text.splitlines())
                total_words += word_count
                print(f"✅ Descargado: {filename} ({word_count:,} palabras)")
            else:
                print(f"❌ Error descargando {url}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con {url}: {e}")
    
    print(f"\n🎉 Total de palabras descargadas: {total_words:,}")
    return total_words

async def run_initial_learning():
    """Ejecutar aprendizaje inicial"""
    print("\n🚀 Iniciando aprendizaje automático inicial...")
    
    try:
        # Ejecutar sesión completa de aprendizaje
        results = await auto_learner.run_full_learning_session()
        
        print(f"\n📊 Resultados del aprendizaje:")
        print(f"   • Palabras aprendidas: {results['total_words_learned']:,}")
        print(f"   • Expresiones aprendidas: {results['total_expressions_learned']:,}")
        
        print(f"\n📈 Estadísticas por fuente:")
        for source, result in results['sources'].items():
            status = result.get('status', 'unknown')
            words = result.get('words_learned', 0)
            expressions = result.get('expressions_learned', 0)
            print(f"   • {source}: {status} ({words} palabras, {expressions} expresiones)")
        
        return results
        
    except Exception as e:
        print(f"❌ Error en aprendizaje inicial: {e}")
        return None

async def setup_auto_learning():
    """Configurar sistema de aprendizaje automático completo"""
    print("🤖 Configurando sistema de aprendizaje automático...")
    print("=" * 60)
    
    # Paso 1: Descargar vocabulario español
    words_downloaded = await download_spanish_vocabulary()
    
    if words_downloaded == 0:
        print("⚠️  No se pudieron descargar palabras. Continuando con datos sintéticos...")
    
    # Paso 2: Ejecutar aprendizaje inicial
    learning_results = await run_initial_learning()
    
    # Paso 3: Mostrar estadísticas finales
    if learning_results:
        stats = auto_learner.get_learning_stats()
        print(f"\n📊 Estadísticas finales:")
        print(f"   • Sesiones de aprendizaje: {stats.get('total_sessions', 0)}")
        print(f"   • Total palabras aprendidas: {stats.get('total_words_learned', 0):,}")
        print(f"   • Total expresiones aprendidas: {stats.get('total_expressions_learned', 0):,}")
    
    print("\n✅ Configuración completada!")
    print("\n🎯 El chatbot ahora puede aprender automáticamente de:")
    print("   • Vocabulario español de la RAE")
    print("   • Datos sintéticos generados")
    print("   • APIs públicas")
    print("   • Archivos de texto locales")
    
    print("\n💡 Para ejecutar aprendizaje manual:")
    print("   python -c \"import asyncio; from backend.auto_learning import auto_learner; asyncio.run(auto_learner.run_full_learning_session())\"")

if __name__ == "__main__":
    asyncio.run(setup_auto_learning()) 