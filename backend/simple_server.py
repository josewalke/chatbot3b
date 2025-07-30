from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
import random
from difflib import SequenceMatcher
import time
from datetime import datetime
import uuid
from datetime import datetime, timedelta
import os

# Importar el gestor de vocabulario masivo
try:
    from massive_vocabulary import MassiveVocabularyManager
    VOCABULARY_MANAGER = MassiveVocabularyManager()
    MASSIVE_VOCABULARY_AVAILABLE = True
    print("✅ Sistema de Vocabulario Masivo cargado")
except ImportError as e:
    print(f"⚠️ No se pudo cargar el vocabulario masivo: {e}")
    VOCABULARY_MANAGER = None
    MASSIVE_VOCABULARY_AVAILABLE = False

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

# Memoria de contexto para cada usuario
user_contexts = {}

# Sistema de aprendizaje básico
conversation_patterns = {}
intent_accuracy = {}

# Sistema de contexto mejorado (como ChatGPT)
conversation_context = {}
conversation_memory = {}
user_preferences = {}

# Configuración de creatividad (temperatura)
CREATIVITY_LEVELS = {
    "conservative": 0.3,  # Respuestas más predecibles
    "balanced": 0.7,      # Respuestas equilibradas
    "creative": 0.9       # Respuestas más variadas
}

# Filtros de seguridad
SAFETY_FILTERS = {
    "inappropriate_words": ["malas palabras", "contenido inapropiado"],
    "sensitive_topics": ["información personal", "datos sensibles"],
    "spam_patterns": ["spam", "promoción excesiva"]
}

# Datos de prueba
SERVICES = [
    {"id": 1, "name": "Consulta General", "duration": 30, "price": 50},
    {"id": 2, "name": "Consulta Especializada", "duration": 60, "price": 100},
    {"id": 3, "name": "Seguimiento", "duration": 20, "price": 30}
]

PRODUCTS = [
    {"id": 1, "name": "Producto A", "price": 25.99, "description": "Descripción del producto A"},
    {"id": 2, "name": "Producto B", "price": 49.99, "description": "Descripción del producto B"},
    {"id": 3, "name": "Producto C", "price": 99.99, "description": "Descripción del producto C"}
]

# Definir variables globales con valores por defecto
INTENT_PATTERNS = {
    "greeting": ["hola", "buenos días", "saludos", "hey", "hi", "hello"],
    "appointment": ["cita", "agendar", "consulta", "reservar"],
    "products": ["productos", "catálogo", "catalogo", "todos"],
    "product_info": ["información", "detalles", "saber más", "más info"],
    "purchase": ["comprar", "adquirir", "tomar", "llevar"],
    "support": ["ayuda", "soporte", "problema", "error"],
    "returns": ["devolución", "reembolso", "cambio"],
    "warranty": ["garantía", "garantia", "warranty"],
    "shipping": ["envío", "envio", "entrega", "shipping"],
    "pricing": ["precio", "cuesta", "valor", "coste"]
}

GREETING_RESPONSES = [
    "¡Hola! 🌟 ¡Bienvenido! Soy tu asistente virtual y estoy aquí para hacer tu día más fácil.",
    "¡Hola! ✨ ¡Qué gusto verte! ¿En qué puedo ayudarte hoy?",
    "¡Hola! 😊 ¡Bienvenido! Estoy aquí para asistirte.",
    "¡Hola! 🎉 ¡Qué alegría verte! ¿Cómo puedo ayudarte?"
]

PRODUCT_INFO_RESPONSES = [
    "¡Excelente elección! 🎉 Has seleccionado {product} por ${price}. ¿Te gustaría proceder con la compra?",
    "¡Perfecto! ✨ {product} es una excelente opción. Precio: ${price}. ¿Quieres comprarlo?",
    "¡Genial! 🌟 {product} está disponible por ${price}. ¿Procedemos con la compra?",
    "¡Excelente! 😊 {product} cuesta ${price}. ¿Te interesa adquirirlo?"
]

PURCHASE_RESPONSES = [
    "¡Perfecto! 🛒 Procedamos con tu compra de {product}. ¿Cómo te gustaría pagar?",
    "¡Excelente! 💳 Vamos a procesar tu compra de {product}. ¿Qué método de pago prefieres?",
    "¡Genial! 🎯 Tu {product} está listo para comprar. ¿PayPal, tarjeta o transferencia?",
    "¡Perfecto! 🚀 Completemos tu compra de {product}. ¿Cuál es tu método de pago preferido?"
]

SUPPORT_RESPONSES = [
    "¡Por supuesto! 🆘 Estoy aquí para ayudarte. ¿Cuál es tu consulta?",
    "¡Claro! 💪 Te ayudo con lo que necesites. ¿En qué puedo asistirte?",
    "¡Perfecto! 🤝 Cuenta conmigo para resolver tu problema. ¿Qué necesitas?",
    "¡Excelente! 🎯 Estoy listo para ayudarte. ¿Cuál es tu pregunta?"
]

GENERAL_RESPONSES = [
    "¡Entiendo! 🤔 Déjame ayudarte con eso.",
    "¡Perfecto! ✨ Te ayudo con esa consulta.",
    "¡Genial! 🌟 Estoy aquí para asistirte.",
    "¡Excelente! 😊 Cuenta conmigo para eso."
]

NATURAL_GREETING_RESPONSES = [
    "¡Hola! ✨ ¡Qué gusto verte! ¿En qué puedo ayudarte hoy?",
    "¡Hola! 🌟 ¡Bienvenido! Soy tu asistente virtual y estoy aquí para hacer tu día más fácil.",
    "¡Hola! 😊 ¡Bienvenido! Estoy aquí para asistirte.",
    "¡Hola! 🎉 ¡Qué alegría verte! ¿Cómo puedo ayudarte?"
]

NATURAL_PRODUCT_RESPONSES = [
    "¡Por supuesto! 🌟 Te muestro nuestro catálogo de productos disponibles:\n\n{products}",
    "¡Genial! ✨ Aquí tienes todos nuestros productos:\n\n{products}",
    "¡Perfecto! 😊 Estos son nuestros productos:\n\n{products}",
    "¡Excelente! 🎯 Aquí está nuestro catálogo:\n\n{products}"
]

NATURAL_SUPPORT_RESPONSES = [
    "¡Por supuesto! 🆘 Estoy aquí para ayudarte. ¿Cuál es tu consulta?",
    "¡Claro! 💪 Te ayudo con lo que necesites. ¿En qué puedo asistirte?",
    "¡Perfecto! 🤝 Cuenta conmigo para resolver tu problema. ¿Qué necesitas?",
    "¡Excelente! 🎯 Estoy listo para ayudarte. ¿Cuál es tu pregunta?"
]

NATURAL_CONVERSATION_RESPONSES = [
    "¡Entiendo! 🤔 Déjame ayudarte con eso.",
    "¡Perfecto! ✨ Te ayudo con esa consulta.",
    "¡Genial! 🌟 Estoy aquí para asistirte.",
    "¡Excelente! 😊 Cuenta conmigo para eso."
]

APPOINTMENT_RESPONSES = [
    "¡Perfecto! 📅 Te ayudo a agendar tu cita. ¿Qué día te viene mejor?",
    "¡Genial! ✨ Vamos a programar tu cita. ¿Cuándo te conviene?",
    "¡Excelente! 😊 Te ayudo con la agenda. ¿Qué fecha prefieres?",
    "¡Perfecto! 🎯 Programemos tu cita. ¿Cuándo tienes disponible?"
]

PRODUCTS_RESPONSES = [
    "¡Por supuesto! 🌟 Te muestro nuestro catálogo de productos disponibles:\n\n{products}",
    "¡Genial! ✨ Aquí tienes todos nuestros productos:\n\n{products}",
    "¡Perfecto! 😊 Estos son nuestros productos:\n\n{products}",
    "¡Excelente! 🎯 Aquí está nuestro catálogo:\n\n{products}"
]

RETURNS_RESPONSES = [
    "¡Entiendo! 🔄 Te ayudo con la devolución. ¿Cuál es el motivo?",
    "¡Perfecto! 📦 Procesemos tu devolución. ¿Qué pasó con el producto?",
    "¡Genial! 💰 Te ayudo con el reembolso. ¿Cuál es el problema?",
    "¡Excelente! 🔙 Vamos con la devolución. ¿Qué necesitas?"
]

WARRANTY_RESPONSES = [
    "¡Perfecto! 🛡️ Te ayudo con la garantía. ¿Cuál es el problema?",
    "¡Genial! 🔧 Vamos a revisar tu garantía. ¿Qué falló?",
    "¡Excelente! ⚙️ Te ayudo con el warranty. ¿Cuál es el defecto?",
    "¡Perfecto! 🛠️ Revisemos tu garantía. ¿Qué necesitas?"
]

SHIPPING_RESPONSES = [
    "¡Entiendo! 🚚 Te ayudo con el envío. ¿Cuál es tu dirección?",
    "¡Perfecto! 📦 Vamos con el shipping. ¿Dónde lo enviamos?",
    "¡Genial! 🚛 Procesemos tu entrega. ¿Cuál es tu ubicación?",
    "¡Excelente! 📮 Te ayudo con el envío. ¿Dónde lo mandamos?"
]

PRICING_RESPONSES = [
    "¡Perfecto! 💰 Te ayudo con el precio. ¿Qué producto te interesa?",
    "¡Genial! 💵 Vamos a revisar los precios. ¿Cuál te llama la atención?",
    "¡Excelente! 💸 Te muestro los costos. ¿Qué quieres saber?",
    "¡Perfecto! 🏷️ Revisemos los precios. ¿Qué te interesa?"
]

# Diccionario de correcciones ortográficas comunes (MUY EXPANDIDO)
SPELLING_CORRECTIONS = {
    # Saludos y expresiones básicas
    "hola": ["ola", "hla", "hol", "ola", "hla", "hola", "ola", "hla", "hol"],
    "buenos": ["buenos", "buenos", "buenos", "buenos"],
    "días": ["dias", "días", "dias", "dias"],
    "dias": ["días", "días", "dias", "dias"],
    "tardes": ["tardes", "tardes", "tardes", "tardes"],
    "noches": ["noches", "noches", "noches", "noches"],
    "saludos": ["saludos", "saludos", "saludos", "saludos"],
    "hey": ["hey", "hey", "hey", "hey"],
    "hi": ["hi", "hi", "hi", "hi"],
    "hello": ["hello", "hello", "hello", "hello"],
    
    # Productos y compras
    "producto": ["produto", "product", "prodcto", "prodcuto", "produto", "prodcto", "prodcuto", "produto"],
    "productos": ["produtos", "products", "prodctos", "produtos", "prodctos", "produtos"],
    "produto": ["producto", "producto", "producto", "producto"],
    "produtos": ["productos", "productos", "productos", "productos"],
    "prodcto": ["producto", "producto", "producto", "producto"],
    "prodctos": ["productos", "productos", "productos", "productos"],
    "prodcuto": ["producto", "producto", "producto", "producto"],
    "prodcutos": ["productos", "productos", "productos", "productos"],
    
    # Verbos de acción
    "quiero": ["kiero", "kero", "quero", "kiero", "kiero", "kiero", "kero", "quero"],
    "kiero": ["quiero", "quiero", "quiero", "quiero"],
    "kero": ["quiero", "quiero", "quiero", "quiero"],
    "quero": ["quiero", "quiero", "quiero", "quiero"],
    "comprar": ["komprar", "comprar", "komprar", "komprar", "komprar", "komprar"],
    "komprar": ["comprar", "comprar", "comprar", "comprar"],
    "adquirir": ["adquirir", "adquirir", "adquirir", "adquirir"],
    "tomar": ["tomar", "tomar", "tomar", "tomar"],
    "llevar": ["llevar", "llevar", "llevar", "llevar"],
    "obtener": ["obtener", "obtener", "obtener", "obtener"],
    "conseguir": ["conseguir", "conseguir", "conseguir", "conseguir"],
    "buscar": ["buscar", "buscar", "buscar", "buscar"],
    "encontrar": ["encontrar", "encontrar", "encontrar", "encontrar"],
    
    # Interés y preferencias
    "interesa": ["interesa", "interesa", "interesa", "interesa"],
    "interesado": ["interesado", "interesado", "interesado", "interesado"],
    "interesada": ["interesada", "interesada", "interesada", "interesada"],
    "gusta": ["gusta", "gusta", "gusta", "gusta"],
    "gusto": ["gusto", "gusto", "gusto", "gusto"],
    "gustan": ["gustan", "gustan", "gustan", "gustan"],
    "me gusta": ["me gusta", "me gusta", "me gusta", "me gusta"],
    "me gustan": ["me gustan", "me gustan", "me gustan", "me gustan"],
    "me interesa": ["me interesa", "me interesa", "me interesa", "me interesa"],
    "me interesan": ["me interesan", "me interesan", "me interesan", "me interesan"],
    
    # Información y consultas
    "información": ["informacion", "informasión", "informasión", "infomacion", "infomacion", "informacion"],
    "informacion": ["información", "informasión", "informasión", "infomacion", "información"],
    "infomacion": ["información", "información", "información", "información"],
    "informasión": ["información", "información", "información", "información"],
    "saber": ["saber", "saber", "saber", "saber"],
    "conocer": ["conocer", "conocer", "conocer", "conocer"],
    "entender": ["entender", "entender", "entender", "entender"],
    "explicar": ["explicar", "explicar", "explicar", "explicar"],
    "explica": ["explica", "explica", "explica", "explica"],
    "explicame": ["explicame", "explicame", "explicame", "explicame"],
    "cuéntame": ["cuentame", "cuéntame", "cuentame", "cuentame"],
    "cuentame": ["cuéntame", "cuéntame", "cuentame", "cuentame"],
    "hablame": ["ablame", "hablame", "ablame", "ablame"],
    "ablame": ["hablame", "hablame", "hablame", "hablame"],
    "dime": ["dime", "dime", "dime", "dime"],
    "muéstrame": ["muestrame", "muéstrame", "muestrame", "muestrame"],
    "muestrame": ["muéstrame", "muéstrame", "muestrame", "muestrame"],
    "dame": ["dame", "dame", "dame", "dame"],
    "necesito": ["nesesito", "necesito", "nesesito", "neseito", "nesesito", "neseito"],
    "nesesito": ["necesito", "necesito", "necesito", "necesito"],
    "neseito": ["necesito", "necesito", "necesito", "necesito"],
    
    # Ayuda y soporte
    "ayuda": ["ayuda", "ayuda", "ayuda", "ayuda"],
    "ayudame": ["ayudame", "ayudame", "ayudame", "ayudame"],
    "soporte": ["soporte", "soporte", "soporte", "soporte"],
    "asistencia": ["asistencia", "asistencia", "asistencia", "asistencia"],
    "problema": ["problema", "problema", "problema", "problema"],
    "problemas": ["problemas", "problemas", "problemas", "problemas"],
    "duda": ["duda", "duda", "duda", "duda"],
    "dudas": ["dudas", "dudas", "dudas", "dudas"],
    "pregunta": ["pregunta", "pregunta", "pregunta", "pregunta"],
    "preguntas": ["preguntas", "preguntas", "preguntas", "preguntas"],
    "consulta": ["consulta", "consulta", "consulta", "consulta"],
    "consultas": ["consultas", "consultas", "consultas", "consultas"],
    
    # Citas y agendamiento
    "cita": ["sita", "cita", "sita", "sita"],
    "sita": ["cita", "cita", "cita", "cita"],
    "citas": ["sitas", "citas", "sitas", "sitas"],
    "sitas": ["citas", "citas", "citas", "citas"],
    "agendar": ["agendar", "agendar", "agendar", "agendar"],
    "reservar": ["reservar", "reservar", "reservar", "reservar"],
    "programar": ["programar", "programar", "programar", "programar"],
    "solicitar": ["solicitar", "solicitar", "solicitar", "solicitar"],
    "anotar": ["anotar", "anotar", "anotar", "anotar"],
    "pedir": ["pedir", "pedir", "pedir", "pedir"],
    "hacer": ["hacer", "hacer", "hacer", "hacer"],
    "sacar": ["sacar", "sacar", "sacar", "sacar"],
    
    # Devoluciones y reembolsos
    "devolución": ["devolucion", "devolusión", "devolusión", "devolucion", "devolucion"],
    "devolucion": ["devolución", "devolusión", "devolusión", "devolucion", "devolución"],
    "devolver": ["devolver", "devolver", "devolver", "devolver"],
    "reembolso": ["reembolso", "reembolso", "reembolso", "reembolso"],
    "reembolsar": ["reembolsar", "reembolsar", "reembolsar", "reembolsar"],
    "política": ["politica", "política", "politica", "politica"],
    "politica": ["política", "política", "politica", "politica"],
    
    # Garantías
    "garantía": ["garantia", "garantía", "garantía", "garantia", "garantia"],
    "garantia": ["garantía", "garantía", "garantía", "garantia", "garantía"],
    "garantizado": ["garantizado", "garantizado", "garantizado", "garantizado"],
    "warranty": ["warranty", "warranty", "warranty", "warranty"],
    
    # Envíos y entregas
    "envío": ["envio", "envío", "envío", "envio", "envio"],
    "envio": ["envío", "envío", "envío", "envio", "envío"],
    "entrega": ["entrega", "entrega", "entrega", "entrega"],
    "delivery": ["delivery", "delivery", "delivery", "delivery"],
    "shipping": ["shipping", "shipping", "shipping", "shipping"],
    "enviar": ["enviar", "enviar", "enviar", "enviar"],
    "mandar": ["mandar", "mandar", "mandar", "mandar"],
    "recibir": ["recibir", "recibir", "recibir", "recibir"],
    "llegar": ["llegar", "llegar", "llegar", "llegar"],
    "tiempo": ["tiempo", "tiempo", "tiempo", "tiempo"],
    "cuando": ["cuando", "cuando", "cuando", "cuando"],
    "cuándo": ["cuando", "cuándo", "cuando", "cuando"],
    "cuanto": ["cuánto", "cuánto", "cuanto", "cuanto"],
    "cuánto": ["cuanto", "cuánto", "cuanto", "cuanto"],
    
    # Precios y costos
    "precio": ["presio", "precio", "presio", "presio", "presio"],
    "presio": ["precio", "precio", "precio", "precio"],
    "costo": ["costo", "costo", "costo", "costo"],
    "cost": ["cost", "cost", "cost", "cost"],
    "valor": ["valor", "valor", "valor", "valor"],
    "cuesta": ["cuesta", "cuesta", "cuesta", "cuesta"],
    "vale": ["vale", "vale", "vale", "vale"],
    "caro": ["caro", "caro", "caro", "caro"],
    "barato": ["barato", "barato", "barato", "barato"],
    "económico": ["economico", "económico", "economico", "economico"],
    "economico": ["económico", "económico", "economico", "economico"],
    "descuento": ["descuento", "descuento", "descuento", "descuento"],
    "oferta": ["oferta", "oferta", "oferta", "oferta"],
    "promoción": ["promocion", "promoción", "promocion", "promocion"],
    "promocion": ["promoción", "promoción", "promocion", "promocion"],
    
    # Catálogo y productos
    "catálogo": ["catalogo", "catálogo", "catalogo", "catalogo"],
    "catalogo": ["catálogo", "catálogo", "catalogo", "catalogo"],
    "catalog": ["catalog", "catalog", "catalog", "catalog"],
    "merchandise": ["merchandise", "merchandise", "merchandise", "merchandise"],
    "mostrar": ["mostrar", "mostrar", "mostrar", "mostrar"],
    "ver": ["ver", "ver", "ver", "ver"],
    "listar": ["listar", "listar", "listar", "listar"],
    "todos": ["todos", "todos", "todos", "todos"],
    "todas": ["todas", "todas", "todas", "todas"],
    "todo": ["todo", "todo", "todo", "todo"],
    "toda": ["toda", "toda", "toda", "toda"],
    "disponibles": ["disponibles", "disponibles", "disponibles", "disponibles"],
    "disponible": ["disponible", "disponible", "disponible", "disponible"],
    "hay": ["hay", "hay", "hay", "hay"],
    "tienes": ["tienes", "tienes", "tienes", "tienes"],
    "tienen": ["tienen", "tienen", "tienen", "tienen"],
    
    # Características y detalles
    "características": ["caracteristicas", "características", "caracteristicas", "caracteristicas"],
    "caracteristicas": ["características", "características", "caracteristicas", "caracteristicas"],
    "detalles": ["detalles", "detalles", "detalles", "detalles"],
    "detalle": ["detalle", "detalle", "detalle", "detalle"],
    "especificaciones": ["especificaciones", "especificaciones", "especificaciones", "especificaciones"],
    "especificación": ["especificacion", "especificación", "especificacion", "especificacion"],
    "especificacion": ["especificación", "especificación", "especificacion", "especificacion"],
    "descripción": ["descripcion", "descripción", "descripcion", "descripcion"],
    "descripcion": ["descripción", "descripción", "descripcion", "descripcion"],
    
    # Proceso y procedimientos
    "proceso": ["proceso", "proceso", "proceso", "proceso"],
    "procedimiento": ["procedimiento", "procedimiento", "procedimiento", "procedimiento"],
    "paso": ["paso", "paso", "paso", "paso"],
    "pasos": ["pasos", "pasos", "pasos", "pasos"],
    "cómo": ["como", "cómo", "como", "como"],
    "como": ["cómo", "cómo", "como", "como"],
    "qué": ["que", "qué", "que", "que"],
    "que": ["qué", "qué", "que", "que"],
    "dónde": ["donde", "dónde", "donde", "donde"],
    "donde": ["dónde", "dónde", "donde", "donde"],
    
    # Artículos y preposiciones
    "el": ["el", "el", "el", "el"],
    "la": ["la", "la", "la", "la"],
    "las": ["las", "las", "las", "las"],
    "los": ["los", "los", "los", "los"],
    "un": ["un", "un", "un", "un"],
    "una": ["una", "una", "una", "una"],
    "unas": ["unas", "unas", "unas", "unas"],
    "unos": ["unos", "unos", "unos", "unos"],
    "del": ["del", "del", "del", "del"],
    "con": ["con", "con", "con", "con"],
    "sin": ["sin", "sin", "sin", "sin"],
    "por": ["por", "por", "por", "por"],
    "para": ["para", "para", "para", "para"],
    "sobre": ["sobre", "sobre", "sobre", "sobre"],
    "entre": ["entre", "entre", "entre", "entre"],
    "hacia": ["hacia", "hacia", "hacia", "hacia"],
    "hasta": ["hasta", "hasta", "hasta", "hasta"],
    "desde": ["desde", "desde", "desde", "desde"],
    "durante": ["durante", "durante", "durante", "durante"],
    "mediante": ["mediante", "mediante", "mediante", "mediante"],
    "según": ["segun", "según", "segun", "segun"],
    "segun": ["según", "según", "segun", "segun"],
    "contra": ["contra", "contra", "contra", "contra"],
    "tras": ["tras", "tras", "tras", "tras"],
    "ante": ["ante", "ante", "ante", "ante"],
    "bajo": ["bajo", "bajo", "bajo", "bajo"],
    "cabe": ["cabe", "cabe", "cabe", "cabe"],
    "conforme": ["conforme", "conforme", "conforme", "conforme"],
    "excepto": ["excepto", "excepto", "excepto", "excepto"],
    "salvo": ["salvo", "salvo", "salvo", "salvo"],
    "vía": ["via", "vía", "via", "via"],
    "via": ["vía", "vía", "via", "via"],
    
    # Pronombres
    "me": ["me", "me", "me", "me"],
    "te": ["te", "te", "te", "te"],
    "se": ["se", "se", "se", "se"],
    "nos": ["nos", "nos", "nos", "nos"],
    "os": ["os", "os", "os", "os"],
    "le": ["le", "le", "le", "le"],
    "les": ["les", "les", "les", "les"],
    "lo": ["lo", "lo", "lo", "lo"],
    
    # Prefijos y sufijos
    "pro": ["pro", "pro", "pro", "pro"],
    "anti": ["anti", "anti", "anti", "anti"],
    "pre": ["pre", "pre", "pre", "pre"],
    "post": ["post", "post", "post", "post"],
    "re": ["re", "re", "re", "re"],
    "sub": ["sub", "sub", "sub", "sub"],
    "super": ["super", "super", "super", "super"],
    "ultra": ["ultra", "ultra", "ultra", "ultra"],
    "extra": ["extra", "extra", "extra", "extra"],
    "intra": ["intra", "intra", "intra", "intra"],
    "inter": ["inter", "inter", "inter", "inter"],
    "trans": ["trans", "trans", "trans", "trans"],
    "cis": ["cis", "cis", "cis", "cis"],
    "ex": ["ex", "ex", "ex", "ex"],
    "co": ["co", "co", "co", "co"]
}

# Sistema de vocabulario dinámico
VOCABULARY_FILES = {
    'spelling_corrections': 'vocabulary/spelling_corrections.json',
    'intent_patterns': 'vocabulary/intent_patterns.json',
    'response_templates': 'vocabulary/response_templates.json',
    'product_keywords': 'vocabulary/product_keywords.json',
    'conversation_flow': 'vocabulary/conversation_flow.json'
}

def load_vocabulary_file(filename):
    """Cargar archivo de vocabulario con manejo de errores"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️ Archivo de vocabulario no encontrado: {filename}")
            return {}
    except Exception as e:
        print(f"❌ Error cargando vocabulario {filename}: {e}")
        return {}

def save_vocabulary_file(filename, data):
    """Guardar archivo de vocabulario"""
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Vocabulario guardado: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error guardando vocabulario {filename}: {e}")
        return False

def reload_vocabulary():
    """Recargar todo el vocabulario desde archivos"""
    global SPELLING_CORRECTIONS, INTENT_PATTERNS, GREETING_RESPONSES, PRODUCT_INFO_RESPONSES, PURCHASE_RESPONSES, SUPPORT_RESPONSES, GENERAL_RESPONSES, NATURAL_GREETING_RESPONSES, NATURAL_PRODUCT_RESPONSES, NATURAL_SUPPORT_RESPONSES, NATURAL_CONVERSATION_RESPONSES, APPOINTMENT_RESPONSES, PRODUCTS_RESPONSES, RETURNS_RESPONSES, WARRANTY_RESPONSES, SHIPPING_RESPONSES, PRICING_RESPONSES
    
    # Cargar correcciones ortográficas
    spelling_data = load_vocabulary_file(VOCABULARY_FILES['spelling_corrections'])
    if spelling_data:
        SPELLING_CORRECTIONS = spelling_data.get('corrections', SPELLING_CORRECTIONS)
    
    # Cargar patrones de intención
    patterns_data = load_vocabulary_file(VOCABULARY_FILES['intent_patterns'])
    if patterns_data:
        INTENT_PATTERNS = patterns_data.get('patterns', INTENT_PATTERNS)
    
    # Cargar plantillas de respuesta
    responses_data = load_vocabulary_file(VOCABULARY_FILES['response_templates'])
    if responses_data:
        GREETING_RESPONSES = responses_data.get('greeting', GREETING_RESPONSES)
        PRODUCT_INFO_RESPONSES = responses_data.get('product_info', PRODUCT_INFO_RESPONSES)
        PURCHASE_RESPONSES = responses_data.get('purchase', PURCHASE_RESPONSES)
        SUPPORT_RESPONSES = responses_data.get('support', SUPPORT_RESPONSES)
        GENERAL_RESPONSES = responses_data.get('general', GENERAL_RESPONSES)
        NATURAL_GREETING_RESPONSES = responses_data.get('natural_greeting', NATURAL_GREETING_RESPONSES)
        NATURAL_PRODUCT_RESPONSES = responses_data.get('natural_product', NATURAL_PRODUCT_RESPONSES)
        NATURAL_SUPPORT_RESPONSES = responses_data.get('natural_support', NATURAL_SUPPORT_RESPONSES)
        NATURAL_CONVERSATION_RESPONSES = responses_data.get('natural_conversation', NATURAL_CONVERSATION_RESPONSES)
        APPOINTMENT_RESPONSES = responses_data.get('appointment', APPOINTMENT_RESPONSES)
        PRODUCTS_RESPONSES = responses_data.get('products', PRODUCTS_RESPONSES)
        RETURNS_RESPONSES = responses_data.get('returns', RETURNS_RESPONSES)
        WARRANTY_RESPONSES = responses_data.get('warranty', WARRANTY_RESPONSES)
        SHIPPING_RESPONSES = responses_data.get('shipping', SHIPPING_RESPONSES)
        PRICING_RESPONSES = responses_data.get('pricing', PRICING_RESPONSES)
    
    print("🔄 Vocabulario recargado desde archivos externos")

def initialize_vocabulary_files():
    """Inicializar archivos de vocabulario si no existen"""
    # Crear directorio de vocabulario
    os.makedirs('vocabulary', exist_ok=True)
    
    # Correcciones ortográficas
    if not os.path.exists(VOCABULARY_FILES['spelling_corrections']):
        spelling_data = {
            'corrections': SPELLING_CORRECTIONS,
            'last_updated': datetime.now().isoformat(),
            'description': 'Correcciones ortográficas y sinónimos'
        }
        save_vocabulary_file(VOCABULARY_FILES['spelling_corrections'], spelling_data)
    
    # Patrones de intención
    if not os.path.exists(VOCABULARY_FILES['intent_patterns']):
        patterns_data = {
            'patterns': INTENT_PATTERNS,
            'last_updated': datetime.now().isoformat(),
            'description': 'Patrones regex para detectar intenciones'
        }
        save_vocabulary_file(VOCABULARY_FILES['intent_patterns'], patterns_data)
    
    # Plantillas de respuesta
    if not os.path.exists(VOCABULARY_FILES['response_templates']):
        responses_data = {
            'greeting': GREETING_RESPONSES,
            'product_info': PRODUCT_INFO_RESPONSES,
            'purchase': PURCHASE_RESPONSES,
            'support': SUPPORT_RESPONSES,
            'general': GENERAL_RESPONSES,
            'natural_greeting': NATURAL_GREETING_RESPONSES,
            'natural_product': NATURAL_PRODUCT_RESPONSES,
            'natural_support': NATURAL_SUPPORT_RESPONSES,
            'natural_conversation': NATURAL_CONVERSATION_RESPONSES,
            'appointment': APPOINTMENT_RESPONSES,
            'products': PRODUCTS_RESPONSES,
            'returns': RETURNS_RESPONSES,
            'warranty': WARRANTY_RESPONSES,
            'shipping': SHIPPING_RESPONSES,
            'pricing': PRICING_RESPONSES,
            'last_updated': datetime.now().isoformat(),
            'description': 'Plantillas de respuesta dinámicas'
        }
        save_vocabulary_file(VOCABULARY_FILES['response_templates'], responses_data)
    
    print("📁 Archivos de vocabulario inicializados")

# Endpoint para actualizar vocabulario
@app.route('/vocabulary/update', methods=['POST'])
def update_vocabulary():
    """Actualizar vocabulario dinámicamente"""
    try:
        data = request.get_json()
        vocabulary_type = data.get('type')
        new_data = data.get('data')
        
        if not vocabulary_type or not new_data:
            return jsonify({'error': 'Tipo y datos requeridos'}), 400
        
        if vocabulary_type == 'spelling_corrections':
            filename = VOCABULARY_FILES['spelling_corrections']
            current_data = load_vocabulary_file(filename)
            current_data['corrections'].update(new_data)
            current_data['last_updated'] = datetime.now().isoformat()
            save_vocabulary_file(filename, current_data)
            
        elif vocabulary_type == 'intent_patterns':
            filename = VOCABULARY_FILES['intent_patterns']
            current_data = load_vocabulary_file(filename)
            current_data['patterns'].update(new_data)
            current_data['last_updated'] = datetime.now().isoformat()
            save_vocabulary_file(filename, current_data)
            
        elif vocabulary_type == 'response_templates':
            filename = VOCABULARY_FILES['response_templates']
            current_data = load_vocabulary_file(filename)
            current_data.update(new_data)
            current_data['last_updated'] = datetime.now().isoformat()
            save_vocabulary_file(filename, current_data)
        
        # Recargar vocabulario
        reload_vocabulary()
        
        return jsonify({
            'message': f'Vocabulario {vocabulary_type} actualizado exitosamente',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para obtener vocabulario actual
@app.route('/vocabulary/get/<vocabulary_type>', methods=['GET'])
def get_vocabulary(vocabulary_type):
    """Obtener vocabulario actual"""
    try:
        if vocabulary_type in VOCABULARY_FILES:
            filename = VOCABULARY_FILES[vocabulary_type]
            data = load_vocabulary_file(filename)
            return jsonify(data)
        else:
            return jsonify({'error': 'Tipo de vocabulario no válido'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para recargar vocabulario
@app.route('/vocabulary/reload', methods=['POST'])
def reload_vocabulary_endpoint():
    """Recargar vocabulario manualmente"""
    try:
        reload_vocabulary()
        return jsonify({
            'message': 'Vocabulario recargado exitosamente',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para estadísticas de vocabulario
@app.route('/vocabulary/stats', methods=['GET'])
def vocabulary_stats():
    """Obtener estadísticas del vocabulario"""
    try:
        stats = {}
        for vocab_type, filename in VOCABULARY_FILES.items():
            data = load_vocabulary_file(filename)
            if data:
                stats[vocab_type] = {
                    'last_updated': data.get('last_updated'),
                    'description': data.get('description'),
                    'size': len(data)
                }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def similarity(a, b):
    """Calcular similitud entre dos strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_text(text):
    """Normalizar texto para mejorar la detección de intenciones"""
    if not text:
        return ""
    
    # Convertir a minúsculas
    normalized = text.lower().strip()
    
    # Aplicar correcciones ortográficas
    for correct_word, variations in SPELLING_CORRECTIONS.items():
        for variation in variations:
            if variation in normalized:
                normalized = normalized.replace(variation, correct_word)
    
    # Normalizar espacios múltiples
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized

def fuzzy_match(text, patterns, threshold=0.7):
    """
    Compara un texto con una lista de patrones usando SequenceMatcher para encontrar la mejor coincidencia.
    Retorna la coincidencia si la similitud supera el umbral, de lo contrario None.
    """
    best_match = None
    best_score = 0

    for pattern in patterns:
        score = SequenceMatcher(None, text.lower(), pattern.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = pattern
    
    if best_score >= threshold:
        return best_match
    return None

# Mejorar la función extract_product_name para ser más flexible
def extract_product_name(message):
    """Extraer nombre del producto de un mensaje (con tolerancia a errores mejorada)"""
    # Normalizar el mensaje
    normalized_message = normalize_text(message)
    original_message = message.lower()
    
    # Patrones más flexibles para detectar productos
    product_patterns = [
        r"producto\s*([abc])",
        r"del\s+producto\s*([abc])",
        r"el\s+producto\s*([abc])",
        r"producto([abc])",
        r"produto\s*([abc])",
        r"prodcto\s*([abc])",
        r"prodcuto\s*([abc])",
        r"produto([abc])",
        r"prodcto([abc])",
        r"prodcuto([abc])"
    ]
    
    # Buscar con patrones exactos
    for pattern in product_patterns:
        match = re.search(pattern, normalized_message.lower())
        if match:
            product_letter = match.group(1).upper()
            for product in PRODUCTS:
                if product['name'].endswith(product_letter):
                    return product
    
    # Buscar con similitud de texto completo
    for product in PRODUCTS:
        product_name_lower = product['name'].lower()
        product_name_simple = product_name_lower.replace('producto ', '')
        
        # Verificar si el mensaje contiene el nombre del producto
        if product_name_lower in normalized_message or product_name_simple in normalized_message:
            return product
        
        # Verificar similitud con el nombre del producto
        if similarity(normalized_message, product_name_lower) > 0.5:
            return product
        
        # Verificar si contiene "producto" + letra
        if f"producto{product_name_simple}" in normalized_message:
            return product
    
    # Buscar palabras clave que indiquen interés en productos específicos
    interest_keywords = ["me interesa", "quiero", "me gusta", "dame", "muéstrame", "hablame"]
    product_indicators = ["productoa", "productob", "productoc", "produtoa", "produtob", "produtoc"]
    
    for keyword in interest_keywords:
        if keyword in normalized_message:
            for indicator in product_indicators:
                if indicator in normalized_message:
                    # Extraer la letra del producto
                    if "a" in indicator:
                        return PRODUCTS[0]  # Producto A
                    elif "b" in indicator:
                        return PRODUCTS[1]  # Producto B
                    elif "c" in indicator:
                        return PRODUCTS[2]  # Producto C
    
    return None

# Mejorar la función understand_intent para ser más precisa
def understand_intent(message):
    """Entender la intención del mensaje con scoring mejorado"""
    # Normalizar el mensaje
    normalized_message = normalize_text(message)
    original_message = message.lower()
    
    best_intent = "general"
    best_score = 0
    
    # Patrones mejorados para product_info y purchase
    product_interest_patterns = [
        r"me\s+interesa\s+(el\s+)?(producto\s*[abc]|produto\s*[abc]|prodcto\s*[abc])",
        r"quiero\s+(el\s+)?(producto\s*[abc]|produto\s*[abc]|prodcto\s*[abc])",
        r"me\s+gusta\s+(el\s+)?(producto\s*[abc]|produto\s*[abc]|prodcto\s*[abc])",
        r"dame\s+(el\s+)?(producto\s*[abc]|produto\s*[abc]|prodcto\s*[abc])",
        r"muéstrame\s+(el\s+)?(producto\s*[abc]|produto\s*[abc]|prodcto\s*[abc])",
        r"hablame\s+(del\s+)?(producto\s*[abc]|produto\s*[abc]|prodcto\s*[abc])"
    ]
    
    # Verificar primero si es interés en producto específico
    for pattern in product_interest_patterns:
        if re.search(pattern, normalized_message, re.IGNORECASE):
            return "product_info"  # Prioridad alta para productos específicos
    
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        
        # Verificar patrones regex en mensaje normalizado
        for pattern in patterns:
            if re.search(pattern, normalized_message, re.IGNORECASE):
                score += 10
        
        # Verificar patrones regex en mensaje original
        for pattern in patterns:
            if re.search(pattern, original_message, re.IGNORECASE):
                score += 8
        
        # Búsqueda fuzzy para patrones que no coincidieron exactamente
        fuzzy_match_result = fuzzy_match(normalized_message, patterns)
        if fuzzy_match_result:
            score += 5
        
        # Bonificaciones específicas mejoradas
        if intent == "product_info":
            if any(word in normalized_message for word in ["hablame", "cuéntame", "dime", "información"]):
                score += 10
            if any(word in normalized_message for word in ["producto", "produto", "prodcto"]):
                score += 8
        elif intent == "purchase":
            if any(word in normalized_message for word in ["quiero", "comprar", "adquirir", "me interesa"]):
                score += 8
            if any(word in normalized_message for word in ["producto", "produto", "prodcto"]):
                score += 6
        elif intent == "greeting":
            if any(word in normalized_message for word in ["hola", "buenos días", "saludos"]):
                score += 5
        
        # Verificar palabras clave adicionales (con tolerancia mejorada)
        keywords = {
            "greeting": ["hola", "buenos días", "saludos", "hey"],
            "appointment": ["cita", "agendar", "consulta"],
            "products": ["productos", "catálogo", "catalogo", "todos"],
            "support": ["ayuda", "soporte", "problema"],
            "returns": ["devolución", "reembolso"],
            "warranty": ["garantía", "garantia"],
            "shipping": ["envío", "envio", "entrega"],
            "pricing": ["precio", "cuesta", "valor"]
        }
        
        if intent in keywords:
            for keyword in keywords[intent]:
                # Buscar coincidencias exactas y aproximadas
                if keyword in normalized_message:
                    score += 3
                elif similarity(keyword, normalized_message) > 0.8:
                    score += 2
        
        if score > best_score:
            best_score = score
            best_intent = intent
    
    return best_intent

def get_dynamic_response(intent, product=None):
    """Obtener una respuesta dinámica y creativa"""
    if intent == "greeting":
        return random.choice(GREETING_RESPONSES)
    elif intent == "product_info" and product:
        template = random.choice(PRODUCT_INFO_RESPONSES)
        return template.format(
            product_name=product['name'],
            description=product['description'],
            price=product['price']
        )
    elif intent == "purchase" and product:
        template = random.choice(PURCHASE_RESPONSES)
        return template.format(
            product_name=product['name'],
            price=product['price']
        )
    elif intent == "support":
        return random.choice(SUPPORT_RESPONSES)
    elif intent == "general":
        return random.choice(GENERAL_RESPONSES)
    else:
        return random.choice(GENERAL_RESPONSES)

def update_user_context(user_id, message, intent, metadata=None):
    """Actualizar el contexto del usuario"""
    if user_id not in user_contexts:
        user_contexts[user_id] = {
            'conversation_history': [],
            'last_intent': None,
            'selected_product': None,
            'appointment_flow': False
        }
    
    context = user_contexts[user_id]
    context['conversation_history'].append({
        'message': message,
        'intent': intent,
        'metadata': metadata
    })
    
    # Mantener solo los últimos 10 mensajes
    if len(context['conversation_history']) > 10:
        context['conversation_history'] = context['conversation_history'][-10:]
    
    context['last_intent'] = intent
    
    if metadata and 'selected_product' in metadata:
        context['selected_product'] = metadata['selected_product']

def learn_from_conversation(user_id, message, intent, was_correct=True):
    """Sistema de aprendizaje básico"""
    if user_id not in conversation_patterns:
        conversation_patterns[user_id] = {}
    
    if intent not in intent_accuracy:
        intent_accuracy[intent] = {"correct": 0, "total": 0}
    
    # Actualizar precisión
    intent_accuracy[intent]["total"] += 1
    if was_correct:
        intent_accuracy[intent]["correct"] += 1
    
    # Guardar patrones de conversación
    pattern_key = f"{message[:20]}..."  # Primeros 20 caracteres
    if pattern_key not in conversation_patterns[user_id]:
        conversation_patterns[user_id][pattern_key] = []
    
    conversation_patterns[user_id][pattern_key].append({
        "intent": intent,
        "timestamp": time.time(),
        "was_correct": was_correct
    })

def get_context_aware_response(user_id, intent, message):
    """Obtener respuesta basada en el contexto del usuario (mejorada)"""
    if user_id not in user_contexts:
        return None
    
    context = user_contexts[user_id]
    last_intent = context.get('last_intent')
    selected_product = context.get('selected_product')
    
    # Si el usuario está en flujo de compra y menciona un producto
    if intent == "purchase" or intent == "product_info":
        product = extract_product_name(message)
        if product:
            if intent == "purchase":
                return f"¡Perfecto! 🛍️ Veo que te interesa {product['name']}. ¿Quieres proceder con la compra por ${product['price']}?"
            else:
                return f"¡Excelente! ✨ Te cuento todo sobre {product['name']}:\n\n📦 **Descripción:** {product['description']}\n💰 **Precio:** ${product['price']}\n🔒 **Garantía:** 1 año\n\n¿Te gustaría comprarlo o saber más detalles?"
    
    # Si el usuario está en flujo de citas
    if last_intent == "appointment" and intent == "appointment":
        return "¡Genial! 🌟 Veo que quieres agendar una cita. ¿Qué servicio específico te interesa más?"
    
    # Si el usuario está preguntando sobre productos después de ver el catálogo
    if last_intent == "products" and (intent == "product_info" or intent == "purchase"):
        return "¡Perfecto! 🌟 Veo que quieres más información sobre un producto específico. ¿Cuál te interesa?"
    
    # Si el usuario menciona un producto específico sin contexto previo
    if intent == "product_info" or intent == "purchase":
        product = extract_product_name(message)
        if product:
            if intent == "purchase":
                return f"¡Fantástico! 🎉 Has seleccionado {product['name']} por ${product['price']}. ¿Te gustaría proceder con la compra?"
            else:
                return f"¡Por supuesto! 😊 Te cuento sobre {product['name']}:\n\n📦 **Descripción:** {product['description']}\n💰 **Precio:** ${product['price']}\n🔒 **Garantía:** 1 año\n\n¿Te gustaría comprarlo?"
    
    # NUEVO: Si el usuario pregunta "más de ese producto" o similar, usar el producto seleccionado previamente
    if selected_product and any(word in message.lower() for word in ["ese", "este", "mismo", "más", "mas", "detalles", "información", "informacion"]):
        if intent == "product_info" or intent == "purchase":
            return f"¡Perfecto! ✨ Te cuento más sobre {selected_product['name']}:\n\n📦 **Descripción:** {selected_product['description']}\n💰 **Precio:** ${selected_product['price']}\n🔒 **Garantía:** 1 año\n📦 **Envío:** Gratis en compras superiores a $50\n\n¿Te gustaría:\n• 💳 Comprar este producto\n• 📦 Ver información de envío\n• 🔒 Saber más sobre la garantía\n• 🛍️ Ver otros productos"
    
    return None

def improve_response_quality(message, intent, product=None):
    """Mejorar la calidad de la respuesta basada en el mensaje"""
    # Detectar urgencia
    urgent_words = ["urgente", "inmediato", "ahora", "ya", "rápido"]
    is_urgent = any(word in message.lower() for word in urgent_words)
    
    # Detectar tono emocional
    positive_words = ["me gusta", "excelente", "perfecto", "genial", "fantástico"]
    negative_words = ["no me gusta", "malo", "terrible", "pésimo", "horrible"]
    
    is_positive = any(word in message.lower() for word in positive_words)
    is_negative = any(word in message.lower() for word in negative_words)
    
    # Personalizar respuesta
    if is_urgent:
        return "¡Entiendo que es urgente! 🚀 Te ayudo inmediatamente:"
    elif is_positive:
        return "¡Me alegra que te guste! 😊 "
    elif is_negative:
        return "Entiendo tu preocupación. 😔 Te ayudo a resolverlo:"
    
    return ""

def get_conversation_context(user_id):
    """Obtener contexto completo de la conversación (como ChatGPT)"""
    if user_id not in conversation_context:
        conversation_context[user_id] = {
            'messages': [],
            'current_topic': None,
            'user_mood': 'neutral',
            'conversation_style': 'balanced',
            'last_interaction': None,
            'preferences': {}
        }
    return conversation_context[user_id]

def update_conversation_context(user_id, message, response, intent):
    """Actualizar contexto de conversación"""
    context = get_conversation_context(user_id)
    
    # Agregar mensaje al historial
    context['messages'].append({
        'timestamp': datetime.now(),
        'user_message': message,
        'bot_response': response,
        'intent': intent,
        'user_id': user_id
    })
    
    # Mantener solo los últimos 20 mensajes (como ChatGPT)
    if len(context['messages']) > 20:
        context['messages'] = context['messages'][-20:]
    
    # Actualizar tema actual
    context['current_topic'] = intent
    
    # Detectar estado de ánimo del usuario
    mood_indicators = {
        'positive': ['me gusta', 'excelente', 'perfecto', 'genial', 'fantástico', 'encanta'],
        'negative': ['no me gusta', 'malo', 'terrible', 'pésimo', 'horrible', 'molesta'],
        'urgent': ['urgente', 'inmediato', 'ya', 'rápido', 'ahora']
    }
    
    for mood, indicators in mood_indicators.items():
        if any(indicator in message.lower() for indicator in indicators):
            context['user_mood'] = mood
            break
    
    # Actualizar última interacción
    context['last_interaction'] = datetime.now()

def generate_natural_response(intent, context=None, creativity_level="balanced"):
    """Generar respuesta natural y conversacional (estilo ChatGPT)"""
    # Seleccionar nivel de creatividad
    temperature = CREATIVITY_LEVELS.get(creativity_level, 0.7)
    
    # Usar más variaciones si la temperatura es alta
    if temperature > 0.8:
        response_pools = {
            "greeting": NATURAL_GREETING_RESPONSES + GREETING_RESPONSES,
            "products": NATURAL_PRODUCT_RESPONSES + PRODUCTS_RESPONSES,
            "support": NATURAL_SUPPORT_RESPONSES + SUPPORT_RESPONSES,
            "general": NATURAL_CONVERSATION_RESPONSES + GENERAL_RESPONSES
        }
    else:
        response_pools = {
            "greeting": GREETING_RESPONSES,
            "products": PRODUCTS_RESPONSES,
            "support": SUPPORT_RESPONSES,
            "general": GENERAL_RESPONSES
        }
    
    # Seleccionar respuesta basada en contexto
    if context and context.get('user_mood') == 'urgent':
        return "¡Entiendo que es urgente! 🚀 Te ayudo inmediatamente:"
    elif context and context.get('user_mood') == 'negative':
        return "Entiendo tu preocupación. 😔 Te ayudo a resolverlo:"
    elif context and context.get('user_mood') == 'positive':
        return "¡Me alegra que te guste! 😊 "
    
    # Respuesta normal
    if intent in response_pools:
        return random.choice(response_pools[intent])
    else:
        return random.choice(GENERAL_RESPONSES)

def apply_safety_filters(message, response):
    """Aplicar filtros de seguridad (como ChatGPT)"""
    # Verificar contenido inapropiado
    for category, words in SAFETY_FILTERS.items():
        for word in words:
            if word in message.lower():
                return "Entiendo tu consulta, pero prefiero mantener la conversación profesional y respetuosa. ¿En qué más puedo ayudarte?"
    
    # Verificar spam
    if message.count('!') > 3 or message.count('?') > 3:
        return "Entiendo tu entusiasmo, pero mantengamos la conversación clara. ¿En qué puedo ayudarte?"
    
    return response

# Mejorar la función create_conversation_flow para manejar mejor el contexto
def create_conversation_flow(user_id, message, intent):
    """Crear flujo de conversación natural (mejorado)"""
    context = get_conversation_context(user_id)
    
    # Detectar si es continuación de conversación
    if context['messages']:
        last_message = context['messages'][-1]
        last_intent = last_message.get('intent')
        
        # Si el usuario está continuando el mismo tema
        if last_intent == intent:
            if intent == "products":
                return "¡Perfecto! 🌟 Veo que quieres explorar más productos. ¿Te gustaría ver algo específico?"
            elif intent == "appointment":
                return "¡Genial! ✨ Veo que sigues interesado en agendar una cita. ¿Qué servicio te llama más la atención?"
            elif intent == "support":
                return "¡Claro! 😊 Veo que necesitas más ayuda. ¿Hay algo específico en lo que pueda asistirte?"
        
        # Si el usuario menciona un producto después de ver el catálogo
        if last_intent == "products" and (intent == "product_info" or intent == "purchase"):
            product = extract_product_name(message)
            if product:
                if intent == "purchase":
                    return f"¡Excelente elección! 🎉 Has seleccionado {product['name']} por ${product['price']}. ¿Te gustaría proceder con la compra?"
                else:
                    return f"¡Perfecto! ✨ Te cuento sobre {product['name']}:\n\n📦 **Descripción:** {product['description']}\n💰 **Precio:** ${product['price']}\n🔒 **Garantía:** 1 año\n\n¿Te gustaría comprarlo?"
        
        # NUEVO: Si el usuario pregunta sobre "ese producto" o similar
        if any(word in message.lower() for word in ["ese", "este", "mismo", "más", "mas", "detalles", "información", "informacion"]):
            # Buscar en el contexto si hay un producto seleccionado
            user_context = user_contexts.get(user_id, {})
            selected_product = user_context.get('selected_product')
            
            if selected_product and (intent == "product_info" or intent == "purchase"):
                return f"¡Perfecto! ✨ Te cuento más sobre {selected_product['name']}:\n\n📦 **Descripción:** {selected_product['description']}\n💰 **Precio:** ${selected_product['price']}\n🔒 **Garantía:** 1 año\n📦 **Envío:** Gratis en compras superiores a $50\n\n¿Te gustaría:\n• 💳 Comprar este producto\n• 📦 Ver información de envío\n• 🔒 Saber más sobre la garantía\n• 🛍️ Ver otros productos"
    
    # Si es un tema nuevo
    return None

def generate_empathetic_response(user_id, message, intent):
    """Generar respuesta empática (como ChatGPT)"""
    context = get_conversation_context(user_id)
    
    # Detectar patrones emocionales
    if any(word in message.lower() for word in ['problema', 'difícil', 'complicado', 'confuso']):
        return "Entiendo que puede ser complicado. 😔 Te ayudo a resolverlo paso a paso. ¿Qué te gustaría hacer?"
    
    if any(word in message.lower() for word in ['gracias', 'grax', 'thx']):
        return "¡De nada! 😊 Me alegra mucho haber podido ayudarte. ¿Hay algo más en lo que pueda asistirte?"
    
    if any(word in message.lower() for word in ['no sé', 'no se', 'confundido', 'perdido']):
        return "No te preocupes, entiendo que puede ser confuso. 😊 Te guío paso a paso. ¿Qué te gustaría hacer?"
    
    # Respuesta normal
    return None

@app.route('/')
def home():
    return jsonify({"message": "Chatbot API funcionando!", "status": "ok"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "chatbot-api"})

@app.route('/chat/send', methods=['POST'])
def chat_send():
    try:
        data = request.get_json()
        message = data.get('message', '').lower()
        user_id = data.get('user_id', 'unknown')
        
        print(f"Recibido mensaje: {message} de usuario: {user_id}")
        
        # Mejorar normalización con vocabulario masivo
        enhanced_message = enhance_normalize_text_with_massive_vocabulary(message)
        print(f"Mensaje normalizado: {enhanced_message}")
        
        # Entender la intención del mensaje
        intent = understand_intent(enhanced_message)
        print(f"Intención detectada: {intent}")
        
        # Obtener contexto de conversación
        context = get_conversation_context(user_id)
        
        # Verificar filtros de seguridad
        safety_check = apply_safety_filters(enhanced_message, None)
        if safety_check:
            response = {
                "message": safety_check,
                "intent": "safety_filter",
                "metadata": {
                    "action": "safety_response"
                }
            }
        else:
            # Generar respuesta empática
            empathetic_response = generate_empathetic_response(user_id, enhanced_message, intent)
            if empathetic_response:
                response = {
                    "message": empathetic_response,
                    "intent": intent,
                    "metadata": {
                        "action": "empathetic_response"
                    }
                }
            else:
                # Crear flujo de conversación natural
                flow_response = create_conversation_flow(user_id, enhanced_message, intent)
                if flow_response:
                    response = {
                        "message": flow_response,
                        "intent": intent,
                        "metadata": {
                            "action": "conversation_flow"
                        }
                    }
                else:
                    # Obtener respuesta basada en contexto
                    context_response = get_context_aware_response(user_id, intent, enhanced_message)
                    if context_response:
                        response = {
                            "message": context_response,
                            "intent": intent,
                            "metadata": {
                                "action": "context_aware_response"
                            }
                        }
                    else:
                        # Generar respuesta natural y conversacional
                        natural_response = generate_natural_response(intent, context)
                        
                        # Generar respuesta dinámica basada en la intención
                        if intent == "greeting":
                            response = {
                                "message": natural_response,
                                "intent": "greeting",
                                "metadata": {
                                    "action": "show_options"
                                }
                            }
                        
                        elif intent == "appointment":
                            response = {
                                "message": random.choice(APPOINTMENT_RESPONSES),
                                "intent": "appointment",
                                "metadata": {
                                    "action": "show_services",
                                    "services": SERVICES
                                }
                            }
                        
                        elif intent == "products":
                            response = {
                                "message": natural_response,
                                "intent": "sales",
                                "metadata": {
                                    "action": "show_products",
                                    "products": PRODUCTS
                                }
                            }
                        
                        elif intent == "product_info":
                            selected_product = extract_product_name(message)
                            if selected_product:
                                response = {
                                    "message": f"¡Por supuesto! 😊 Te cuento sobre {selected_product['name']}:\n\n📦 **Descripción:** {selected_product['description']}\n💰 **Precio:** ${selected_product['price']}\n🔒 **Garantía:** 1 año\n\n¿Te gustaría comprarlo o saber más detalles?",
                                    "intent": "product_info",
                                    "metadata": {
                                        "action": "show_product_details",
                                        "selected_product": selected_product
                                    }
                                }
                            else:
                                response = {
                                    "message": "¡Claro! ✨ Te muestro nuestros productos disponibles para que puedas elegir cuál te interesa:",
                                    "intent": "sales",
                                    "metadata": {
                                        "action": "show_products",
                                        "products": PRODUCTS
                                    }
                                }
                        
                        elif intent == "purchase":
                            selected_product = extract_product_name(message)
                            if selected_product:
                                response = {
                                    "message": f"¡Excelente elección! 🎉 Has seleccionado {selected_product['name']} por ${selected_product['price']}.\n\n¿Te gustaría proceder con la compra? Puedo ayudarte con:\n• 💳 Procesar el pago\n• 📦 Información de envío\n• 🔒 Garantía del producto\n• 📞 Contactar un agente",
                                    "intent": "purchase",
                                    "metadata": {
                                        "action": "show_purchase_options",
                                        "selected_product": selected_product
                                    }
                                }
                            else:
                                response = {
                                    "message": "¡Perfecto! 🛍️ Te muestro nuestros productos disponibles para que puedas elegir:",
                                    "intent": "sales",
                                    "metadata": {
                                        "action": "show_products",
                                        "products": PRODUCTS
                                    }
                                }
                        
                        elif intent == "support":
                            response = {
                                "message": natural_response,
                                "intent": "support",
                                "metadata": {
                                    "action": "show_support_options"
                                }
                            }
                        
                        elif intent == "returns":
                            response = {
                                "message": random.choice(RETURNS_RESPONSES),
                                "intent": "support",
                                "metadata": {
                                    "action": "show_support_options"
                                }
                            }
                        
                        elif intent == "warranty":
                            response = {
                                "message": random.choice(WARRANTY_RESPONSES),
                                "intent": "support",
                                "metadata": {
                                    "action": "show_support_options"
                                }
                            }
                        
                        elif intent == "shipping":
                            response = {
                                "message": random.choice(SHIPPING_RESPONSES),
                                "intent": "sales",
                                "metadata": {
                                    "action": "show_products",
                                    "products": PRODUCTS
                                }
                            }
                        
                        elif intent == "pricing":
                            response = {
                                "message": random.choice(PRICING_RESPONSES),
                                "intent": "sales",
                                "metadata": {
                                    "action": "show_products",
                                    "products": PRODUCTS
                                }
                            }
                        
                        else:  # intent == "general"
                            response = {
                                "message": natural_response,
                                "intent": "general",
                                "metadata": {
                                    "action": "show_options"
                                }
                            }
        
        # Mejorar calidad de respuesta
        quality_prefix = improve_response_quality(message, intent)
        if quality_prefix:
            response["message"] = quality_prefix + response["message"]
        
        # Actualizar contexto de conversación
        update_conversation_context(user_id, message, response["message"], intent)
        
        # Actualizar contexto del usuario
        update_user_context(user_id, message, intent, response.get('metadata'))
        
        # Aprender de la conversación
        learn_from_conversation(user_id, message, intent, was_correct=True)
        
        # Actualizar vocabulario masivo desde la conversación
        update_massive_vocabulary_from_conversation(user_id, message, intent, response["message"])
        
        print(f"Respuesta: {response}")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error en chat_send: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/appointments/available-slots')
def available_slots():
    slots = []
    for hour in range(9, 18):
        slots.append(f"{hour:02d}:00")
        slots.append(f"{hour:02d}:30")
    
    return jsonify({
        "available_slots": slots,
        "services": SERVICES
    })

@app.route('/sales/products')
def get_products():
    return jsonify({"products": PRODUCTS})

@app.route('/support/query', methods=['POST'])
def support_query():
    data = request.get_json()
    query = data.get('query', '').lower()
    
    if any(word in query for word in ["devolución", "reembolso"]):
        response = "Nuestra política de devoluciones permite reembolsos dentro de los 30 días de la compra."
    elif any(word in query for word in ["garantía", "garantia"]):
        response = "Todos nuestros productos tienen garantía de 1 año."
    elif any(word in query for word in ["envío", "envio", "entrega"]):
        response = "Los envíos se realizan en 2-3 días hábiles."
    else:
        response = "Gracias por tu consulta. Un agente te contactará pronto."
    
    return jsonify({
        "response": response,
        "escalated": False,
        "ticket_id": f"TKT-{len(query)}"
    })

@app.route('/chat/stats')
def get_chat_stats():
    """Obtener estadísticas del chatbot"""
    return jsonify({
        "intent_accuracy": intent_accuracy,
        "total_conversations": len(user_contexts),
        "patterns_learned": len(conversation_patterns)
    })

# Agregar nuevo endpoint para estadísticas de conversación
@app.route('/chat/conversation-stats')
def get_conversation_stats():
    """Obtener estadísticas de conversación (como ChatGPT)"""
    total_conversations = len(conversation_context)
    total_messages = sum(len(ctx['messages']) for ctx in conversation_context.values())
    
    # Análisis de temas más comunes
    topic_analysis = {}
    for ctx in conversation_context.values():
        for msg in ctx['messages']:
            intent = msg.get('intent', 'unknown')
            topic_analysis[intent] = topic_analysis.get(intent, 0) + 1
    
    return jsonify({
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "topic_analysis": topic_analysis,
        "average_messages_per_conversation": total_messages / max(total_conversations, 1),
        "active_conversations": len([ctx for ctx in conversation_context.values() 
                                   if ctx.get('last_interaction') and 
                                   datetime.now() - ctx['last_interaction'] < timedelta(hours=1)])
    })

def expand_vocabulary_from_message(message):
    """Expandir vocabulario desde un mensaje del usuario"""
    if not MASSIVE_VOCABULARY_AVAILABLE:
        return 0
    
    try:
        # Extraer palabras del mensaje
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Agregar al vocabulario masivo
        new_words = set(words) - VOCABULARY_MANAGER.massive_vocabulary
        
        if new_words:
            VOCABULARY_MANAGER.massive_vocabulary.update(new_words)
            print(f"📝 Agregadas {len(new_words)} nuevas palabras al vocabulario masivo")
            
            # Actualizar correcciones ortográficas
            for word in new_words:
                if word not in SPELLING_CORRECTIONS:
                    SPELLING_CORRECTIONS[word] = [word]
            
            return len(new_words)
        
        return 0
    except Exception as e:
        print(f"⚠️ Error expandiendo vocabulario: {e}")
        return 0

def find_best_match_in_massive_vocabulary(word, threshold=0.6):
    """Encontrar la mejor coincidencia en el vocabulario masivo"""
    if not MASSIVE_VOCABULARY_AVAILABLE:
        return word, 0.0
    
    try:
        similar_words = VOCABULARY_MANAGER.find_similar_words(word, threshold)
        if similar_words:
            best_match, similarity = similar_words[0]
            return best_match, similarity
        return word, 0.0
    except Exception as e:
        print(f"⚠️ Error buscando en vocabulario masivo: {e}")
        return word, 0.0

def enhance_normalize_text_with_massive_vocabulary(text):
    """Mejorar la normalización de texto usando el vocabulario masivo"""
    if not text:
        return ""
    
    # Normalización básica
    normalized = normalize_text(text)
    
    if MASSIVE_VOCABULARY_AVAILABLE:
        try:
            # Buscar palabras similares en el vocabulario masivo
            words = re.findall(r'\b\w+\b', normalized)
            enhanced_words = []
            
            for word in words:
                best_match, similarity = find_best_match_in_massive_vocabulary(word)
                if similarity > 0.8:  # Solo si la similitud es muy alta
                    enhanced_words.append(best_match)
                else:
                    enhanced_words.append(word)
            
            # Reconstruir el texto
            enhanced_text = ' '.join(enhanced_words)
            return enhanced_text
        except Exception as e:
            print(f"⚠️ Error en normalización mejorada: {e}")
            return normalized
    
    return normalized

def get_massive_vocabulary_stats():
    """Obtener estadísticas del vocabulario masivo"""
    if not MASSIVE_VOCABULARY_AVAILABLE:
        return {"error": "Vocabulario masivo no disponible"}
    
    try:
        stats = VOCABULARY_MANAGER.get_vocabulary_stats()
        return {
            "massive_vocabulary": stats,
            "available": True,
            "total_words": stats['total_words'],
            "categories": stats['categories']
        }
    except Exception as e:
        return {"error": f"Error obteniendo estadísticas: {e}"}

def update_massive_vocabulary_from_conversation(user_id, message, intent, response):
    """Actualizar vocabulario masivo desde la conversación"""
    if not MASSIVE_VOCABULARY_AVAILABLE:
        return
    
    try:
        # Expandir vocabulario desde el mensaje del usuario
        new_words_user = expand_vocabulary_from_message(message)
        
        # Expandir vocabulario desde la respuesta del bot
        new_words_bot = expand_vocabulary_from_message(response)
        
        # Aprender patrones de conversación
        if user_id not in conversation_patterns:
            conversation_patterns[user_id] = []
        
        pattern = {
            "message": message,
            "intent": intent,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        conversation_patterns[user_id].append(pattern)
        
        # Mantener solo los últimos 50 patrones
        if len(conversation_patterns[user_id]) > 50:
            conversation_patterns[user_id] = conversation_patterns[user_id][-50:]
        
        total_new_words = new_words_user + new_words_bot
        if total_new_words > 0:
            print(f"🧠 Aprendizaje: {total_new_words} nuevas palabras agregadas al vocabulario masivo")
            
            # Guardar vocabulario actualizado
            VOCABULARY_MANAGER.save_massive_vocabulary()
    
    except Exception as e:
        print(f"⚠️ Error actualizando vocabulario masivo: {e}")

@app.route('/vocabulary/massive/stats', methods=['GET'])
def massive_vocabulary_stats():
    """Obtener estadísticas del vocabulario masivo"""
    stats = get_massive_vocabulary_stats()
    return jsonify(stats)

@app.route('/vocabulary/massive/search', methods=['POST'])
def search_massive_vocabulary():
    """Buscar palabras similares en el vocabulario masivo"""
    try:
        data = request.get_json()
        word = data.get('word', '').lower()
        threshold = data.get('threshold', 0.6)
        
        if not MASSIVE_VOCABULARY_AVAILABLE:
            return jsonify({"error": "Vocabulario masivo no disponible"})
        
        similar_words = VOCABULARY_MANAGER.find_similar_words(word, threshold)
        
        return jsonify({
            "word": word,
            "similar_words": similar_words[:10],  # Top 10
            "total_found": len(similar_words)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vocabulary/massive/expand', methods=['POST'])
def expand_massive_vocabulary():
    """Expandir vocabulario masivo desde texto"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not MASSIVE_VOCABULARY_AVAILABLE:
            return jsonify({"error": "Vocabulario masivo no disponible"})
        
        new_words = VOCABULARY_MANAGER.expand_vocabulary_from_text(text)
        
        return jsonify({
            "text": text,
            "new_words_added": new_words,
            "total_words": len(VOCABULARY_MANAGER.massive_vocabulary)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vocabulary/massive/learn', methods=['POST'])
def learn_from_conversation_massive():
    """Aprender desde una conversación completa"""
    try:
        data = request.get_json()
        conversation = data.get('conversation', [])
        
        if not MASSIVE_VOCABULARY_AVAILABLE:
            return jsonify({"error": "Vocabulario masivo no disponible"})
        
        total_new_words = 0
        for message in conversation:
            if isinstance(message, str):
                new_words = VOCABULARY_MANAGER.expand_vocabulary_from_text(message)
                total_new_words += new_words
        
        return jsonify({
            "conversation_length": len(conversation),
            "new_words_added": total_new_words,
            "total_words": len(VOCABULARY_MANAGER.massive_vocabulary)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando Chatbot Inteligente Avanzado con Técnicas de ChatGPT...")
    print("📡 Servidor disponible en: http://localhost:8000")
    print("📚 Endpoints disponibles:")
    print("   - GET  /health")
    print("   - POST /chat/send")
    print("   - GET  /appointments/available-slots")
    print("   - GET  /sales/products")
    print("   - POST /support/query")
    print("   - GET  /chat/stats")
    print("   - GET  /chat/conversation-stats")
    print("   - POST /vocabulary/update")
    print("   - GET  /vocabulary/get/<type>")
    print("   - POST /vocabulary/reload")
    print("   - GET  /vocabulary/stats")
    print("   - GET  /vocabulary/massive/stats")
    print("   - POST /vocabulary/massive/search")
    print("   - POST /vocabulary/massive/expand")
    print("   - POST /vocabulary/massive/learn")
    print("🧠 Características avanzadas:")
    print("   - Memoria de contexto por usuario")
    print("   - Detección de intenciones con scoring")
    print("   - Respuestas dinámicas y creativas")
    print("   - Patrones regex avanzados")
    print("   - Extracción inteligente de productos")
    print("   - Corrección automática de errores ortográficos")
    print("   - Búsqueda fuzzy para coincidencias aproximadas")
    print("   - Sistema de aprendizaje básico")
    print("   - Respuestas basadas en contexto")
    print("   - Detección de urgencia y tono emocional")
    print("   - Estadísticas de precisión")
    print("   - Vocabulario dinámico actualizable")
    print("   - Técnicas de ChatGPT implementadas:")
    print("     • Contexto de conversación mejorado")
    print("     • Respuestas naturales y conversacionales")
    print("     • Ajuste de creatividad (temperatura)")
    print("     • Filtros de seguridad")
    print("     • Flujo de conversación natural")
    print("     • Respuestas empáticas")
    print("     • Análisis de temas de conversación")
    
    # Inicializar archivos de vocabulario
    print("📁 Inicializando archivos de vocabulario...")
    initialize_vocabulary_files()
    
    # Recargar vocabulario desde archivos
    print("🔄 Cargando vocabulario desde archivos...")
    reload_vocabulary()
    
    # Iniciar servidor en modo debug
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True) 