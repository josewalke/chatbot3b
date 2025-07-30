#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Optimizado para Chatbot Inteligente
Versión optimizada para bajo consumo de recursos
"""

import asyncio
import json
import sqlite3
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from functools import lru_cache
from datetime import datetime
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

# Importar el sistema de aprendizaje optimizado
from optimized_learning import vocabulary_learner, LearningConfig
from auto_learning import auto_learner
from spell_checker import spell_checker
from continuous_learning import continuous_learner

# Configurar logging optimizado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración optimizada
@dataclass
class OptimizedConfig:
    APP_NAME: str = "Chatbot Inteligente Optimizado"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    DATABASE_URL: str = "sqlite:///chatbot_optimized.db"
    DATABASE_PATH: str = "chatbot_optimized.db"
    CACHE_MAX_SIZE: int = 1000
    CACHE_TTL: int = 3600
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "chatbot_optimized.log"
    USE_OPENAI: bool = False # Desactivar por defecto para ahorrar recursos
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 100
    USE_STRIPE: bool = False
    USE_EMAIL: bool = False
    USE_TELEGRAM: bool = False
    USE_FACEBOOK: bool = False
    SECRET_KEY: str = "chatbot-optimized-secret-key-2024"
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    RESPONSE_CACHE_TTL: int = 300
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    VOCABULARY_CACHE_SIZE: int = 500
    INTENT_PATTERNS_CACHE_SIZE: int = 100
    RESPONSE_CACHE_SIZE: int = 200
    CONTEXT_CACHE_SIZE: int = 100
    ENABLE_LEARNING: bool = True  # Habilitar aprendizaje optimizado

# Configuración global
config = OptimizedConfig()

# Cache optimizado
class OptimizedCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}

    def get(self, key):
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None

    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            least_used = min(self.access_count.items(), key=lambda x: x[1])
            del self.cache[least_used[0]]
            del self.access_count[least_used[0]]

        self.cache[key] = value
        self.access_count[key] = 1

# Instancia de cache global
cache = OptimizedCache(config.CACHE_MAX_SIZE)

# Base de datos optimizada
class OptimizedDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializar base de datos optimizada"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Tabla de conversaciones
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        message TEXT,
                        response TEXT,
                        intent TEXT,
                        timestamp TEXT,
                        learned_words INTEGER DEFAULT 0,
                        learned_expressions INTEGER DEFAULT 0
                    )
                """)
                
                # Tabla de citas
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        date TEXT,
                        time TEXT,
                        service TEXT,
                        status TEXT DEFAULT 'pending',
                        created_at TEXT
                    )
                """)
                
                # Tabla de productos
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        price REAL,
                        description TEXT,
                        category TEXT,
                        stock INTEGER DEFAULT 0
                    )
                """)
                
                # Tabla de ventas
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        product_id INTEGER,
                        quantity INTEGER,
                        total REAL,
                        date TEXT
                    )
                """)
                
                # Crear índices para optimizar consultas
                conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_user_id ON sales(user_id)")
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")

# Instancia de base de datos
db = OptimizedDatabase(config.DATABASE_PATH)

# Patrones de intención optimizados
INTENT_PATTERNS = {
    "greeting": ["hola", "buenos días", "buenas tardes", "buenas noches", "saludos"],
    "farewell": ["adiós", "hasta luego", "nos vemos", "chao", "hasta pronto"],
    "appointment": ["cita", "agendar", "reservar", "horario", "consulta", "visita"],
    "sales": ["comprar", "producto", "precio", "costo", "venta", "pago"],
    "support": ["ayuda", "problema", "error", "soporte", "asistencia"],
    "thanks": ["gracias", "muchas gracias", "te agradezco"],
    "information": ["información", "datos", "detalles", "saber más"],
    "complaint": ["queja", "reclamo", "problema", "mal servicio"],
    "praise": ["excelente", "muy bien", "perfecto", "genial"]
}

# Respuestas optimizadas
RESPONSES = {
    "greeting": [
        "¡Hola! ¿En qué puedo ayudarte hoy?",
        "¡Buenos días! ¿Cómo estás?",
        "¡Hola! Estoy aquí para asistirte."
    ],
    "farewell": [
        "¡Hasta luego! Que tengas un buen día.",
        "¡Nos vemos pronto!",
        "¡Que tengas éxito!"
    ],
    "appointment": [
        "Te ayudo a agendar una cita. ¿Qué día prefieres?",
        "Perfecto, vamos a programar tu consulta. ¿Tienes alguna preferencia de horario?",
        "Claro, ¿qué tipo de servicio necesitas?"
    ],
    "sales": [
        "Tenemos varios productos disponibles. ¿Qué te interesa?",
        "Te puedo mostrar nuestros productos y precios.",
        "¿Qué tipo de producto estás buscando?"
    ],
    "support": [
        "Estoy aquí para ayudarte. ¿Cuál es el problema?",
        "Te ayudo a resolver tu consulta. ¿Puedes darme más detalles?",
        "No te preocupes, vamos a solucionarlo juntos."
    ],
    "thanks": [
        "¡De nada! Es un placer ayudarte.",
        "¡Gracias a ti por confiar en mí!",
        "¡Me alegra haber podido ayudarte!"
    ],
    "information": [
        "Con gusto te proporciono la información que necesitas.",
        "Te ayudo con los detalles que buscas.",
        "¿Qué información específica necesitas?"
    ],
    "complaint": [
        "Lamento mucho escuchar eso. Te ayudo a resolver el problema.",
        "Entiendo tu preocupación. Vamos a solucionarlo.",
        "Me disculpo por la situación. ¿Cómo puedo ayudarte?"
    ],
    "praise": [
        "¡Muchas gracias! Me alegra saber que estoy ayudando bien.",
        "¡Gracias! Es muy gratificante recibir tu feedback positivo.",
        "¡Me hace muy feliz! Seguiré esforzándome por ayudarte mejor."
    ],
    "default": [
        "Entiendo. ¿Puedes darme más detalles?",
        "Interesante. ¿Qué más me puedes contar?",
        "Gracias por compartir eso. ¿En qué más puedo ayudarte?"
    ]
}

@lru_cache(maxsize=256)
def normalize_text(text: str) -> str:
    """Normalizar texto de forma optimizada"""
    if not text:
        return ""
    
    # Limpiar y normalizar
    normalized = re.sub(r'[^\w\s]', '', text.lower().strip())
    return normalized

@lru_cache(maxsize=256)
def understand_intent(message: str) -> str:
    """Entender intención de forma optimizada"""
    normalized = normalize_text(message)

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if pattern in normalized:
                return intent
    return "greeting"

def get_response(intent: str) -> str:
    """Obtener respuesta optimizada"""
    responses = RESPONSES.get(intent, RESPONSES["default"])
    return responses[0] if responses else "Entiendo. ¿En qué más puedo ayudarte?"

# Modelos Pydantic optimizados
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"

class ChatResponse(BaseModel):
    response: str
    intent: str
    learned_words: int = 0
    learned_expressions: int = 0
    total_vocabulary: int = 0
    spelling_corrections: List[Dict] = []

class AppointmentRequest(BaseModel):
    user_id: str
    date: str
    time: str
    service: str

class ProductRequest(BaseModel):
    name: str
    price: float
    description: str
    category: str
    stock: int = 0

# Aplicación FastAPI optimizada
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    debug=config.DEBUG
)

# Configurar CORS optimizado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz optimizado"""
    return {
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "status": "running",
        "optimizations": {
            "cache_size": len(cache.cache),
            "learning_enabled": config.ENABLE_LEARNING,
            "vocabulary_size": vocabulary_learner.get_vocabulary_summary()["total_words"] if config.ENABLE_LEARNING else 0
        }
    }

@app.get("/health")
async def health_check():
    """Verificación de salud optimizada"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_hits": sum(cache.access_count.values()),
        "learning_stats": vocabulary_learner.get_learning_stats() if config.ENABLE_LEARNING else {}
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat optimizado con aprendizaje integrado y corrección ortográfica"""
    try:
        # Verificar cache primero
        cache_key = f"chat_{hash(request.message + request.user_id)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return ChatResponse(**cached_response)

        # Verificar ortografía y obtener correcciones
        spelling_corrections = []
        words = request.message.split()
        
        for word in words:
            # Limpiar palabra de puntuación
            clean_word = re.sub(r'[^\wáéíóúñü]', '', word.lower())
            if clean_word and len(clean_word) > 2:  # Solo palabras de 3+ caracteres
                spell_check = spell_checker.check_spelling(clean_word)
                if not spell_check['is_correct'] and spell_check['suggestions']:
                    spelling_corrections.append({
                        'original': word,
                        'suggestions': spell_check['suggestions'],
                        'confidence': spell_check['confidence'],
                        'error_type': spell_check['error_type']
                    })

        # Procesar mensaje
        intent = understand_intent(request.message)
        response = get_response(intent)
        
        # Aprender del mensaje si está habilitado
        learned_words = 0
        learned_expressions = 0
        total_vocabulary = 0
        
        if config.ENABLE_LEARNING:
            learning_result = vocabulary_learner.learn_from_text(request.message, intent)
            learned_words = learning_result["words"]
            learned_expressions = learning_result["expressions"]
            total_vocabulary = learning_result["total_vocabulary"]
            
            # Aprender variaciones ortográficas
            for correction in spelling_corrections:
                if correction['suggestions']:
                    spell_checker.learn_variation(
                        correction['suggestions'][0], 
                        correction['original'], 
                        'user_input'
                    )

        # Guardar en base de datos de forma asíncrona
        await asyncio.to_thread(db._save_conversation, request.user_id, request.message, response, intent, learned_words, learned_expressions)

        # Crear respuesta
        chat_response = ChatResponse(
            response=response,
            intent=intent,
            learned_words=learned_words,
            learned_expressions=learned_expressions,
            total_vocabulary=total_vocabulary,
            spelling_corrections=spelling_corrections
        )

        # Guardar en cache
        cache.set(cache_key, chat_response.dict())

        return chat_response

    except Exception as e:
        logger.error(f"Error en chat: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/learning/stats")
async def get_learning_stats():
    """Obtener estadísticas de aprendizaje"""
    if not config.ENABLE_LEARNING:
        return {"error": "Learning system is disabled"}
    
    return vocabulary_learner.get_learning_stats()

@app.get("/learning/vocabulary")
async def get_vocabulary_summary():
    """Obtener resumen del vocabulario"""
    if not config.ENABLE_LEARNING:
        return {"error": "Learning system is disabled"}
    
    return vocabulary_learner.get_vocabulary_summary()

@app.post("/learning/search")
async def search_similar_words(word: str, limit: int = 5):
    """Buscar palabras similares"""
    if not config.ENABLE_LEARNING:
        return {"error": "Learning system is disabled"}
    
    similar_words = vocabulary_learner.search_similar_words(word, limit)
    return {"word": word, "similar_words": similar_words}

@app.post("/learning/cleanup")
async def cleanup_old_words(days: int = 30):
    """Limpiar palabras antiguas"""
    if not config.ENABLE_LEARNING:
        return {"error": "Learning system is disabled"}
    
    vocabulary_learner.cleanup_old_words(days)
    return {"message": f"Cleanup completed for words older than {days} days"}

@app.post("/auto-learning/start")
async def start_auto_learning():
    """Iniciar aprendizaje automático"""
    try:
        results = await auto_learner.run_full_learning_session()
        return {
            "status": "success",
            "message": "Aprendizaje automático completado",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error en aprendizaje automático: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auto-learning/stats")
async def get_auto_learning_stats():
    """Obtener estadísticas de aprendizaje automático"""
    try:
        stats = auto_learner.get_learning_stats()
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/spelling/stats")
async def get_spelling_stats():
    """Obtener estadísticas del corrector ortográfico"""
    try:
        stats = spell_checker.get_variations_stats()
        return {
            "spelling_variations": stats,
            "total_variations": stats.get('total_variations', 0),
            "unique_words": stats.get('unique_words', 0),
            "avg_similarity": stats.get('avg_similarity', 0.0)
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de ortografía: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/spelling/check")
async def check_spelling(word: str):
    """Verificar ortografía de una palabra específica"""
    try:
        result = spell_checker.check_spelling(word)
        return {
            "word": word,
            "is_correct": result['is_correct'],
            "suggestions": result.get('suggestions', []),
            "confidence": result.get('confidence', 0.0),
            "error_type": result.get('error_type', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error verificando ortografía: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/spelling/learn")
async def learn_spelling_variation(correct_word: str, variation: str, error_type: str = "manual"):
    """Aprender una nueva variación ortográfica manualmente"""
    try:
        spell_checker.learn_variation(correct_word, variation, error_type)
        return {
            "status": "success",
            "message": f"Variación aprendida: '{variation}' -> '{correct_word}'",
            "correct_word": correct_word,
            "variation": variation,
            "error_type": error_type
        }
    except Exception as e:
        logger.error(f"Error aprendiendo variación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS DE APRENDIZAJE CONTINUO =====

@app.post("/continuous-learning/start")
async def start_continuous_learning():
    """Iniciar el aprendizaje continuo en segundo plano"""
    try:
        continuous_learner.start_continuous_learning()
        return {
            "status": "success",
            "message": "Aprendizaje continuo iniciado",
            "is_running": continuous_learner.is_running,
            "interval_minutes": continuous_learner.config.training_interval_minutes
        }
    except Exception as e:
        logger.error(f"Error iniciando aprendizaje continuo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/continuous-learning/stop")
async def stop_continuous_learning():
    """Detener el aprendizaje continuo"""
    try:
        continuous_learner.stop_continuous_learning()
        return {
            "status": "success",
            "message": "Aprendizaje continuo detenido",
            "is_running": continuous_learner.is_running
        }
    except Exception as e:
        logger.error(f"Error deteniendo aprendizaje continuo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/continuous-learning/stats")
async def get_continuous_learning_stats():
    """Obtener estadísticas del aprendizaje continuo"""
    try:
        stats = continuous_learner.get_learning_stats()
        return {
            "continuous_learning_stats": stats,
            "is_running": continuous_learner.is_running,
            "config": {
                "training_interval_minutes": continuous_learner.config.training_interval_minutes,
                "enable_text_files": continuous_learner.config.enable_text_files,
                "enable_api_learning": continuous_learner.config.enable_api_learning,
                "enable_synthetic_data": continuous_learner.config.enable_synthetic_data,
                "enable_spanish_corpus": continuous_learner.config.enable_spanish_corpus
            }
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de aprendizaje continuo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/continuous-learning/config")
async def update_continuous_learning_config(
    training_interval_minutes: Optional[int] = None,
    enable_text_files: Optional[bool] = None,
    enable_api_learning: Optional[bool] = None,
    enable_synthetic_data: Optional[bool] = None,
    enable_spanish_corpus: Optional[bool] = None
):
    """Actualizar configuración del aprendizaje continuo"""
    try:
        if training_interval_minutes is not None:
            continuous_learner.config.training_interval_minutes = training_interval_minutes
        if enable_text_files is not None:
            continuous_learner.config.enable_text_files = enable_text_files
        if enable_api_learning is not None:
            continuous_learner.config.enable_api_learning = enable_api_learning
        if enable_synthetic_data is not None:
            continuous_learner.config.enable_synthetic_data = enable_synthetic_data
        if enable_spanish_corpus is not None:
            continuous_learner.config.enable_spanish_corpus = enable_spanish_corpus
        
        return {
            "status": "success",
            "message": "Configuración actualizada",
            "config": {
                "training_interval_minutes": continuous_learner.config.training_interval_minutes,
                "enable_text_files": continuous_learner.config.enable_text_files,
                "enable_api_learning": continuous_learner.config.enable_api_learning,
                "enable_synthetic_data": continuous_learner.config.enable_synthetic_data,
                "enable_spanish_corpus": continuous_learner.config.enable_spanish_corpus
            }
        }
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Métodos de base de datos
def _save_conversation(self, user_id: str, message: str, response: str, intent: str, learned_words: int, learned_expressions: int):
    """Guardar conversación en base de datos"""
    try:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations (user_id, message, response, intent, timestamp, learned_words, learned_expressions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, message, response, intent, datetime.now().isoformat(), learned_words, learned_expressions))
            conn.commit()
    except Exception as e:
        logger.error(f"Error guardando conversación: {e}")

# Agregar método a la clase OptimizedDatabase
OptimizedDatabase._save_conversation = _save_conversation

# Endpoints adicionales optimizados
@app.get("/appointments")
async def get_appointments(user_id: str = None):
    """Obtener citas optimizado"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            if user_id:
                cursor = conn.execute("SELECT * FROM appointments WHERE user_id = ?", (user_id,))
            else:
                cursor = conn.execute("SELECT * FROM appointments")
            
            appointments = []
            for row in cursor:
                appointments.append({
                    "id": row[0],
                    "user_id": row[1],
                    "date": row[2],
                    "time": row[3],
                    "service": row[4],
                    "status": row[5]
                })
            
            return {"appointments": appointments}
    except Exception as e:
        logger.error(f"Error obteniendo citas: {e}")
        raise HTTPException(status_code=500, detail="Error interno")

@app.post("/appointments")
async def create_appointment(appointment: AppointmentRequest):
    """Crear cita optimizado"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            conn.execute("""
                INSERT INTO appointments (user_id, date, time, service, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (appointment.user_id, appointment.date, appointment.time, appointment.service, datetime.now().isoformat()))
            conn.commit()
        
        return {"message": "Cita creada exitosamente"}
    except Exception as e:
        logger.error(f"Error creando cita: {e}")
        raise HTTPException(status_code=500, detail="Error interno")

@app.get("/products")
async def get_products():
    """Obtener productos optimizado"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("SELECT * FROM products")
            products = []
            for row in cursor:
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "price": row[2],
                    "description": row[3],
                    "category": row[4],
                    "stock": row[5]
                })
            
            return {"products": products}
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        raise HTTPException(status_code=500, detail="Error interno")

@app.post("/products")
async def create_product(product: ProductRequest):
    """Crear producto optimizado"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            conn.execute("""
                INSERT INTO products (name, price, description, category, stock)
                VALUES (?, ?, ?, ?, ?)
            """, (product.name, product.price, product.description, product.category, product.stock))
            conn.commit()
        
        return {"message": "Producto creado exitosamente"}
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno")

@app.get("/statistics")
async def get_statistics():
    """Obtener estadísticas optimizadas"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            # Estadísticas de conversaciones
            total_conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            total_appointments = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
            total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            
            # Estadísticas de aprendizaje
            learning_stats = vocabulary_learner.get_learning_stats() if config.ENABLE_LEARNING else {}
            
            return {
                "conversations": total_conversations,
                "appointments": total_appointments,
                "products": total_products,
                "learning": learning_stats,
                "cache": {
                    "size": len(cache.cache),
                    "hits": sum(cache.access_count.values())
                }
            }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno")

if __name__ == "__main__":
    print(f"🚀 Iniciando {config.APP_NAME} v{config.APP_VERSION}")
    print(f"📊 Configuración optimizada:")
    print(f"   - Workers: {config.WORKERS}")
    print(f"   - Cache size: {config.CACHE_MAX_SIZE}")
    print(f"   - Learning enabled: {config.ENABLE_LEARNING}")
    print(f"   - Database: {config.DATABASE_PATH}")
    
    uvicorn.run(
        "optimized_server:app",
        host=config.HOST,
        port=config.PORT,
        workers=config.WORKERS,
        log_level=config.LOG_LEVEL.lower()
    ) 