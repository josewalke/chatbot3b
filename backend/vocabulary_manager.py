#!/usr/bin/env python3
"""
Administrador de Vocabulario del Chatbot
Permite actualizar palabras clave, patrones y respuestas sin modificar el código
"""

import json
import os
import requests
from datetime import datetime

class VocabularyManager:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.vocabulary_files = {
            'spelling_corrections': 'vocabulary/spelling_corrections.json',
            'intent_patterns': 'vocabulary/intent_patterns.json',
            'response_templates': 'vocabulary/response_templates.json'
        }
    
    def add_spelling_correction(self, correct_word, variations):
        """Agregar corrección ortográfica"""
        try:
            # Cargar correcciones actuales
            with open(self.vocabulary_files['spelling_corrections'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Agregar nueva corrección
            data['corrections'][correct_word] = variations
            data['last_updated'] = datetime.now().isoformat()
            
            # Guardar
            with open(self.vocabulary_files['spelling_corrections'], 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Actualizar en el servidor
            response = requests.post(f"{self.base_url}/vocabulary/update", json={
                'type': 'spelling_corrections',
                'data': {correct_word: variations}
            })
            
            if response.status_code == 200:
                print(f"✅ Corrección agregada: '{correct_word}' → {variations}")
                return True
            else:
                print(f"❌ Error actualizando servidor: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def add_intent_pattern(self, intent, patterns):
        """Agregar patrón de intención"""
        try:
            # Cargar patrones actuales
            with open(self.vocabulary_files['intent_patterns'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Agregar nuevos patrones
            if intent not in data['patterns']:
                data['patterns'][intent] = []
            data['patterns'][intent].extend(patterns)
            data['last_updated'] = datetime.now().isoformat()
            
            # Guardar
            with open(self.vocabulary_files['intent_patterns'], 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Actualizar en el servidor
            response = requests.post(f"{self.base_url}/vocabulary/update", json={
                'type': 'intent_patterns',
                'data': {intent: patterns}
            })
            
            if response.status_code == 200:
                print(f"✅ Patrones agregados para '{intent}': {patterns}")
                return True
            else:
                print(f"❌ Error actualizando servidor: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def add_response_template(self, response_type, templates):
        """Agregar plantilla de respuesta"""
        try:
            # Cargar plantillas actuales
            with open(self.vocabulary_files['response_templates'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Agregar nuevas plantillas
            if response_type not in data:
                data[response_type] = []
            data[response_type].extend(templates)
            data['last_updated'] = datetime.now().isoformat()
            
            # Guardar
            with open(self.vocabulary_files['response_templates'], 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Actualizar en el servidor
            response = requests.post(f"{self.base_url}/vocabulary/update", json={
                'type': 'response_templates',
                'data': {response_type: templates}
            })
            
            if response.status_code == 200:
                print(f"✅ Plantillas agregadas para '{response_type}': {len(templates)} plantillas")
                return True
            else:
                print(f"❌ Error actualizando servidor: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def reload_vocabulary(self):
        """Recargar vocabulario en el servidor"""
        try:
            response = requests.post(f"{self.base_url}/vocabulary/reload")
            if response.status_code == 200:
                print("✅ Vocabulario recargado exitosamente")
                return True
            else:
                print(f"❌ Error recargando vocabulario: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def get_stats(self):
        """Obtener estadísticas del vocabulario"""
        try:
            response = requests.get(f"{self.base_url}/vocabulary/stats")
            if response.status_code == 200:
                stats = response.json()
                print("📊 Estadísticas del Vocabulario:")
                for vocab_type, info in stats.items():
                    print(f"  • {vocab_type}: {info.get('size', 'N/A')} elementos")
                    print(f"    Última actualización: {info.get('last_updated', 'N/A')}")
                return stats
            else:
                print(f"❌ Error obteniendo estadísticas: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def bulk_update_from_file(self, filename):
        """Actualizar vocabulario desde archivo JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                updates = json.load(f)
            
            success_count = 0
            total_count = 0
            
            for update_type, data in updates.items():
                if update_type == 'spelling_corrections':
                    for word, variations in data.items():
                        if self.add_spelling_correction(word, variations):
                            success_count += 1
                        total_count += 1
                
                elif update_type == 'intent_patterns':
                    for intent, patterns in data.items():
                        if self.add_intent_pattern(intent, patterns):
                            success_count += 1
                        total_count += 1
                
                elif update_type == 'response_templates':
                    for template_type, templates in data.items():
                        if self.add_response_template(template_type, templates):
                            success_count += 1
                        total_count += 1
            
            print(f"✅ Actualización masiva completada: {success_count}/{total_count} exitosas")
            return success_count == total_count
            
        except Exception as e:
            print(f"❌ Error en actualización masiva: {e}")
            return False

def main():
    """Función principal con menú interactivo"""
    manager = VocabularyManager()
    
    print("🤖 Administrador de Vocabulario del Chatbot")
    print("=" * 50)
    
    while True:
        print("\n📋 Opciones disponibles:")
        print("1. Agregar corrección ortográfica")
        print("2. Agregar patrón de intención")
        print("3. Agregar plantilla de respuesta")
        print("4. Recargar vocabulario")
        print("5. Ver estadísticas")
        print("6. Actualización masiva desde archivo")
        print("0. Salir")
        
        choice = input("\n🔧 Selecciona una opción: ").strip()
        
        if choice == "1":
            correct_word = input("📝 Palabra correcta: ").strip()
            variations_input = input("🔄 Variaciones (separadas por coma): ").strip()
            variations = [v.strip() for v in variations_input.split(",")]
            
            if manager.add_spelling_correction(correct_word, variations):
                print("✅ Corrección agregada exitosamente")
        
        elif choice == "2":
            intent = input("🎯 Intención (greeting, products, purchase, etc.): ").strip()
            patterns_input = input("🔍 Patrones regex (separados por coma): ").strip()
            patterns = [p.strip() for p in patterns_input.split(",")]
            
            if manager.add_intent_pattern(intent, patterns):
                print("✅ Patrones agregados exitosamente")
        
        elif choice == "3":
            response_type = input("💬 Tipo de respuesta (greeting, product_info, etc.): ").strip()
            templates_input = input("📝 Plantillas (separadas por |): ").strip()
            templates = [t.strip() for t in templates_input.split("|")]
            
            if manager.add_response_template(response_type, templates):
                print("✅ Plantillas agregadas exitosamente")
        
        elif choice == "4":
            manager.reload_vocabulary()
        
        elif choice == "5":
            manager.get_stats()
        
        elif choice == "6":
            filename = input("📁 Archivo JSON con actualizaciones: ").strip()
            if os.path.exists(filename):
                manager.bulk_update_from_file(filename)
            else:
                print("❌ Archivo no encontrado")
        
        elif choice == "0":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main() 