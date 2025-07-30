#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Vocabulario Masivo para Chatbot Inteligente
Incluye todas las palabras posibles en español con variaciones y correcciones
"""

import json
import re
import os
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple
import requests
import time

class MassiveVocabularyManager:
    """Gestor de vocabulario masivo para el chatbot"""
    
    def __init__(self):
        self.vocabulary_dir = "vocabulary"
        self.ensure_vocabulary_dir()
        
        # Diccionarios principales
        self.spelling_corrections = {}
        self.intent_patterns = {}
        self.response_templates = {}
        self.product_keywords = {}
        self.conversation_flow = {}
        
        # Vocabulario masivo
        self.massive_vocabulary = set()
        self.word_frequency = {}
        self.synonyms = {}
        self.context_words = {}
        
        # Cargar vocabulario inicial
        self.load_massive_vocabulary()
    
    def ensure_vocabulary_dir(self):
        """Asegurar que existe el directorio de vocabulario"""
        if not os.path.exists(self.vocabulary_dir):
            os.makedirs(self.vocabulary_dir)
    
    def load_massive_vocabulary(self):
        """Cargar vocabulario masivo desde archivos"""
        print("🔄 Cargando vocabulario masivo...")
        
        # Cargar desde archivos existentes
        self.load_from_files()
        
        # Generar vocabulario adicional
        self.generate_massive_vocabulary()
        
        # Guardar vocabulario masivo
        self.save_massive_vocabulary()
        
        print(f"✅ Vocabulario masivo cargado: {len(self.massive_vocabulary)} palabras")
    
    def load_from_files(self):
        """Cargar vocabulario desde archivos JSON existentes"""
        files = {
            'spelling_corrections': 'spelling_corrections.json',
            'intent_patterns': 'intent_patterns.json',
            'response_templates': 'response_templates.json',
            'product_keywords': 'product_keywords.json',
            'conversation_flow': 'conversation_flow.json'
        }
        
        for key, filename in files.items():
            filepath = os.path.join(self.vocabulary_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if key == 'spelling_corrections':
                            self.spelling_corrections = data
                        elif key == 'intent_patterns':
                            self.intent_patterns = data
                        elif key == 'response_templates':
                            self.response_templates = data
                        elif key == 'product_keywords':
                            self.product_keywords = data
                        elif key == 'conversation_flow':
                            self.conversation_flow = data
                        
                        # Agregar palabras al vocabulario masivo
                        self.add_to_massive_vocabulary(data)
                        
                except Exception as e:
                    print(f"⚠️ Error cargando {filename}: {e}")
    
    def generate_massive_vocabulary(self):
        """Generar vocabulario masivo con todas las palabras posibles"""
        print("🧠 Generando vocabulario masivo...")
        
        # 1. Palabras básicas del español
        basic_words = self.get_basic_spanish_words()
        self.massive_vocabulary.update(basic_words)
        
        # 2. Variaciones ortográficas comunes
        variations = self.generate_spelling_variations()
        self.massive_vocabulary.update(variations)
        
        # 3. Sinónimos y expresiones
        synonyms = self.generate_synonyms()
        self.massive_vocabulary.update(synonyms)
        
        # 4. Palabras contextuales
        context_words = self.generate_context_words()
        self.massive_vocabulary.update(context_words)
        
        # 5. Expresiones coloquiales
        colloquial = self.generate_colloquial_expressions()
        self.massive_vocabulary.update(colloquial)
        
        # 6. Términos técnicos y profesionales
        technical = self.generate_technical_terms()
        self.massive_vocabulary.update(technical)
        
        # 7. Neologismos y palabras modernas
        neologisms = self.generate_neologisms()
        self.massive_vocabulary.update(neologisms)
    
    def get_basic_spanish_words(self) -> Set[str]:
        """Obtener palabras básicas del español"""
        words = set()
        
        # Artículos
        articles = ["el", "la", "los", "las", "un", "una", "unos", "unas"]
        words.update(articles)
        
        # Pronombres
        pronouns = [
            "yo", "tú", "él", "ella", "nosotros", "nosotras", "vosotros", "vosotras",
            "ellos", "ellas", "me", "te", "le", "nos", "os", "les", "se", "mi", "tu",
            "su", "nuestro", "nuestra", "vuestro", "vuestra", "su", "sus", "este",
            "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel", "aquella",
            "aquellos", "aquellas", "que", "quien", "cual", "cuales", "cuanto", "cuanta",
            "cuantos", "cuantas", "donde", "cuando", "como", "porque", "si", "no"
        ]
        words.update(pronouns)
        
        # Verbos comunes
        common_verbs = [
            "ser", "estar", "tener", "hacer", "poder", "deber", "querer", "ir", "venir",
            "dar", "ver", "saber", "decir", "llegar", "pasar", "quedar", "poner",
            "parecer", "creer", "pensar", "sentir", "vivir", "trabajar", "estudiar",
            "comer", "beber", "dormir", "despertar", "levantar", "acostar", "vestir",
            "lavar", "limpiar", "cocinar", "comprar", "vender", "pagar", "cobrar",
            "ganar", "perder", "encontrar", "buscar", "encontrar", "perder", "ganar",
            "ayudar", "necesitar", "querer", "gustar", "amar", "odiar", "temer",
            "esperar", "esperar", "esperar", "esperar", "esperar", "esperar"
        ]
        words.update(common_verbs)
        
        # Sustantivos comunes
        common_nouns = [
            "casa", "coche", "trabajo", "familia", "amigo", "tiempo", "dinero",
            "agua", "comida", "ropa", "libro", "teléfono", "computadora", "internet",
            "televisión", "radio", "música", "película", "pelicula", "pelicula",
            "película", "película", "película", "película", "película", "película"
        ]
        words.update(common_nouns)
        
        # Adjetivos comunes
        common_adjectives = [
            "bueno", "malo", "grande", "pequeño", "nuevo", "viejo", "bonito",
            "feo", "alto", "bajo", "gordo", "delgado", "fuerte", "débil",
            "rico", "pobre", "feliz", "triste", "contento", "enojado", "cansado",
            "energético", "energetico", "energetico", "energético", "energético"
        ]
        words.update(common_adjectives)
        
        # Adverbios comunes
        common_adverbs = [
            "muy", "más", "menos", "bien", "mal", "rápido", "lento", "ahora",
            "antes", "después", "siempre", "nunca", "a veces", "a veces", "a veces"
        ]
        words.update(common_adverbs)
        
        return words
    
    def generate_spelling_variations(self) -> Set[str]:
        """Generar variaciones ortográficas comunes"""
        variations = set()
        
        # Patrones de errores comunes
        error_patterns = {
            'h': ['j', ''],  # hola -> ola, jola
            'v': ['b'],      # vender -> bender
            'b': ['v'],      # buscar -> vuscar
            'c': ['k', 's'], # casa -> kasa, sasa
            'k': ['c', 'qu'], # kilo -> cilo, quilo
            'z': ['s'],      # zapato -> sapato
            's': ['z'],      # casa -> caza
            'll': ['y'],     # llave -> yave
            'ñ': ['ni'],     # año -> anio
            'rr': ['r'],     # perro -> pero
            'qu': ['k'],     # que -> ke
            'gu': ['g'],     # guerra -> gerra
            'ch': ['sh'],    # chico -> shico
            'j': ['h'],      # jamón -> hamón
            'g': ['j'],      # gente -> jente
            'x': ['ks'],     # taxi -> taksi
            'w': ['gu'],     # web -> gueb
            'y': ['ll'],     # yo -> llo
            'i': ['y'],      # día -> dya
            'u': ['w'],      # agua -> agwa
        }
        
        # Aplicar variaciones a palabras comunes
        common_words = [
            "hola", "buenos", "dias", "tardes", "noches", "gracias", "por favor",
            "quiero", "necesito", "busco", "encuentro", "compro", "vendo", "ayudo",
            "producto", "servicio", "precio", "costo", "valor", "dinero", "pago",
            "cita", "consulta", "agenda", "reserva", "horario", "fecha", "tiempo",
            "informacion", "detalles", "especificaciones", "caracteristicas",
            "garantia", "devolucion", "reembolso", "envio", "entrega", "shipping"
        ]
        
        for word in common_words:
            variations.add(word)
            
            # Generar variaciones con errores comunes
            for original, replacements in error_patterns.items():
                if original in word:
                    for replacement in replacements:
                        new_word = word.replace(original, replacement)
                        variations.add(new_word)
            
            # Variaciones sin acentos
            no_accents = word.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            if no_accents != word:
                variations.add(no_accents)
            
            # Variaciones con acentos incorrectos
            with_accents = word.replace('a', 'á').replace('e', 'é').replace('i', 'í').replace('o', 'ó').replace('u', 'ú')
            if with_accents != word:
                variations.add(with_accents)
        
        return variations
    
    def generate_synonyms(self) -> Set[str]:
        """Generar sinónimos y expresiones similares"""
        synonyms = set()
        
        # Sinónimos por categoría
        synonym_groups = {
            "saludos": ["hola", "buenos días", "buenas tardes", "buenas noches", "saludos", "hey", "hi", "hello", "qué tal", "cómo estás", "cómo va", "qué pasa"],
            "despedidas": ["adiós", "hasta luego", "nos vemos", "chao", "bye", "hasta la vista", "hasta pronto", "cuídate", "que tengas un buen día"],
            "agradecimiento": ["gracias", "muchas gracias", "te agradezco", "mil gracias", "gracias por todo", "te lo agradezco", "muy agradecido"],
            "productos": ["producto", "artículo", "item", "mercancía", "bien", "cosa", "objeto", "elemento"],
            "comprar": ["comprar", "adquirir", "obtener", "conseguir", "tomar", "llevar", "adquirir", "purchasear", "buy"],
            "información": ["información", "info", "datos", "detalles", "especificaciones", "características", "particularidades"],
            "precio": ["precio", "costo", "valor", "coste", "tarifa", "precio", "valor", "cost"],
            "ayuda": ["ayuda", "soporte", "asistencia", "apoyo", "auxilio", "help", "support"],
            "problema": ["problema", "issue", "error", "fallo", "defecto", "inconveniente", "dificultad"],
            "cita": ["cita", "consulta", "agenda", "reserva", "cita previa", "appointment", "booking"],
            "servicio": ["servicio", "atención", "asistencia", "ayuda", "soporte", "service"],
            "garantía": ["garantía", "warranty", "garantia", "aseguramiento", "protección"],
            "devolución": ["devolución", "devolucion", "reembolso", "cambio", "return", "refund"],
            "envío": ["envío", "envio", "entrega", "shipping", "delivery", "transporte"],
            "tiempo": ["tiempo", "tiempo", "duración", "periodo", "lapso", "time", "duration"]
        }
        
        for category, words in synonym_groups.items():
            synonyms.update(words)
        
        return synonyms
    
    def generate_context_words(self) -> Set[str]:
        """Generar palabras contextuales"""
        context_words = set()
        
        # Palabras de contexto comercial
        commercial_context = [
            "tienda", "negocio", "empresa", "compañía", "compania", "compañia", "companía",
            "cliente", "usuario", "consumidor", "comprador", "vendedor", "proveedor",
            "catálogo", "catalogo", "inventario", "stock", "existencias", "disponibilidad",
            "oferta", "promoción", "promocion", "descuento", "rebaja", "liquidación",
            "factura", "recibo", "ticket", "comprobante", "documento", "contrato"
        ]
        context_words.update(commercial_context)
        
        # Palabras de contexto médico
        medical_context = [
            "doctor", "médico", "medico", "especialista", "consultorio", "clínica",
            "hospital", "enfermero", "enfermera", "paciente", "diagnóstico", "diagnostico",
            "tratamiento", "medicamento", "medicina", "receta", "síntoma", "sintoma",
            "dolor", "malestar", "enfermedad", "cura", "mejora", "recuperación"
        ]
        context_words.update(medical_context)
        
        # Palabras de contexto tecnológico
        tech_context = [
            "computadora", "ordenador", "laptop", "tablet", "smartphone", "teléfono",
            "internet", "web", "sitio", "página", "aplicación", "app", "software",
            "hardware", "programa", "sistema", "red", "conexión", "wifi", "bluetooth",
            "cámara", "pantalla", "teclado", "mouse", "ratón", "impresora", "escáner"
        ]
        context_words.update(tech_context)
        
        return context_words
    
    def generate_colloquial_expressions(self) -> Set[str]:
        """Generar expresiones coloquiales"""
        colloquial = set()
        
        # Expresiones coloquiales comunes
        expressions = [
            "qué tal", "cómo va", "qué pasa", "qué onda", "qué hay", "qué cuentas",
            "todo bien", "todo mal", "más o menos", "así así", "regular", "bien",
            "genial", "excelente", "fantástico", "terrible", "horrible", "pésimo",
            "vale", "ok", "okay", "perfecto", "exacto", "correcto", "incorrecto",
            "claro", "obvio", "evidente", "seguro", "cierto", "verdad", "mentira",
            "tal vez", "quizás", "quizas", "a lo mejor", "probablemente", "posiblemente",
            "definitivamente", "absolutamente", "completamente", "totalmente"
        ]
        colloquial.update(expressions)
        
        return colloquial
    
    def generate_technical_terms(self) -> Set[str]:
        """Generar términos técnicos"""
        technical = set()
        
        # Términos técnicos generales
        general_tech = [
            "algoritmo", "programación", "programacion", "código", "codigo", "desarrollo",
            "implementación", "implementacion", "integración", "integracion", "API",
            "base de datos", "servidor", "cliente", "protocolo", "interfaz", "usuario",
            "administrador", "configuración", "configuracion", "instalación", "instalacion",
            "actualización", "actualizacion", "versión", "version", "compatible"
        ]
        technical.update(general_tech)
        
        # Términos de e-commerce
        ecommerce_terms = [
            "carrito", "checkout", "pago", "tarjeta", "crédito", "débito", "transferencia",
            "paypal", "stripe", "mercadopago", "bitcoin", "criptomoneda", "wallet",
            "facturación", "facturacion", "impuestos", "IVA", "descuento", "cupón",
            "código promocional", "codigo promocional", "envío gratis", "envio gratis"
        ]
        technical.update(ecommerce_terms)
        
        return technical
    
    def generate_neologisms(self) -> Set[str]:
        """Generar neologismos y palabras modernas"""
        neologisms = set()
        
        # Palabras modernas y neologismos
        modern_words = [
            "selfie", "hashtag", "trending", "viral", "influencer", "youtuber",
            "streaming", "podcast", "webinar", "zoom", "teams", "slack", "discord",
            "instagram", "facebook", "twitter", "tiktok", "linkedin", "whatsapp",
            "telegram", "signal", "uber", "airbnb", "netflix", "spotify", "amazon",
            "google", "youtube", "wikipedia", "reddit", "twitch", "discord"
        ]
        neologisms.update(modern_words)
        
        return neologisms
    
    def add_to_massive_vocabulary(self, data):
        """Agregar palabras de un diccionario al vocabulario masivo"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    self.massive_vocabulary.add(key.lower())
                    self.massive_vocabulary.add(value.lower())
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            self.massive_vocabulary.add(item.lower())
                            self.massive_vocabulary.add(key.lower())
    
    def save_massive_vocabulary(self):
        """Guardar vocabulario masivo en archivos"""
        # Guardar vocabulario masivo
        massive_vocab_file = os.path.join(self.vocabulary_dir, "massive_vocabulary.json")
        with open(massive_vocab_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_words": len(self.massive_vocabulary),
                "words": list(self.massive_vocabulary),
                "categories": {
                    "basic_words": len(self.get_basic_spanish_words()),
                    "variations": len(self.generate_spelling_variations()),
                    "synonyms": len(self.generate_synonyms()),
                    "context_words": len(self.generate_context_words()),
                    "colloquial": len(self.generate_colloquial_expressions()),
                    "technical": len(self.generate_technical_terms()),
                    "neologisms": len(self.generate_neologisms())
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Vocabulario masivo guardado: {massive_vocab_file}")
    
    def get_vocabulary_stats(self) -> Dict:
        """Obtener estadísticas del vocabulario"""
        return {
            "total_words": len(self.massive_vocabulary),
            "spelling_corrections": len(self.spelling_corrections),
            "intent_patterns": len(self.intent_patterns),
            "response_templates": len(self.response_templates),
            "product_keywords": len(self.product_keywords),
            "conversation_flow": len(self.conversation_flow),
            "categories": {
                "basic_words": len(self.get_basic_spanish_words()),
                "variations": len(self.generate_spelling_variations()),
                "synonyms": len(self.generate_synonyms()),
                "context_words": len(self.generate_context_words()),
                "colloquial": len(self.generate_colloquial_expressions()),
                "technical": len(self.generate_technical_terms()),
                "neologisms": len(self.generate_neologisms())
            }
        }
    
    def find_similar_words(self, word: str, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Encontrar palabras similares en el vocabulario masivo"""
        similar_words = []
        
        for vocab_word in self.massive_vocabulary:
            similarity = SequenceMatcher(None, word.lower(), vocab_word.lower()).ratio()
            if similarity >= threshold:
                similar_words.append((vocab_word, similarity))
        
        # Ordenar por similitud
        similar_words.sort(key=lambda x: x[1], reverse=True)
        return similar_words
    
    def expand_vocabulary_from_text(self, text: str):
        """Expandir vocabulario desde un texto"""
        words = re.findall(r'\b\w+\b', text.lower())
        new_words = set(words) - self.massive_vocabulary
        
        if new_words:
            self.massive_vocabulary.update(new_words)
            print(f"📝 Agregadas {len(new_words)} nuevas palabras al vocabulario")
            self.save_massive_vocabulary()
        
        return len(new_words)

def main():
    """Función principal para probar el vocabulario masivo"""
    print("🚀 Iniciando Sistema de Vocabulario Masivo...")
    
    manager = MassiveVocabularyManager()
    
    # Mostrar estadísticas
    stats = manager.get_vocabulary_stats()
    print("\n📊 Estadísticas del Vocabulario Masivo:")
    print(f"   Total de palabras: {stats['total_words']:,}")
    print(f"   Correcciones ortográficas: {stats['spelling_corrections']}")
    print(f"   Patrones de intención: {stats['intent_patterns']}")
    print(f"   Plantillas de respuesta: {stats['response_templates']}")
    print(f"   Palabras clave de productos: {stats['product_keywords']}")
    print(f"   Flujos de conversación: {stats['conversation_flow']}")
    
    print("\n📋 Categorías:")
    for category, count in stats['categories'].items():
        print(f"   {category.replace('_', ' ').title()}: {count:,}")
    
    # Probar búsqueda de palabras similares
    test_words = ["hola", "producto", "cita", "ayuda", "precio"]
    print("\n🔍 Prueba de búsqueda de palabras similares:")
    for word in test_words:
        similar = manager.find_similar_words(word, threshold=0.6)
        print(f"   '{word}' -> {len(similar)} palabras similares")
        if similar:
            top_similar = similar[:3]
            print(f"      Top 3: {[w[0] for w in top_similar]}")
    
    print("\n✅ Sistema de Vocabulario Masivo listo!")

if __name__ == "__main__":
    main() 