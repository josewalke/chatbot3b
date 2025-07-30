#!/usr/bin/env python3
"""
Servidor de prueba simple para el Chatbot Inteligente
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import logging
import sqlite3
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Chatbot Inteligente - Servidor de Prueba",
    description="Servidor optimizado para pruebas",
    version="1.0.0"
)

# Modelos Pydantic
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"

class ChatResponse(BaseModel):
    response: str
    intent: str
    status: str = "success"
    timestamp: str = ""

# Base de datos simple
class SimpleDatabase:
    def __init__(self, db_path: str = "test_chatbot.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializar base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        message TEXT,
                        response TEXT,
                        intent TEXT,
                        timestamp TEXT
                    )
                """)
                conn.commit()
                logger.info("✅ Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def save_conversation(self, user_id: str, message: str, response: str, intent: str):
        """Guardar conversación"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO conversations (user_id, message, response, intent, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, message, response, intent, datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Error guardando conversación: {e}")

# Instancia de base de datos
db = SimpleDatabase()

# Funciones de procesamiento
def understand_intent(message: str) -> str:
    """Entender la intención del mensaje"""
    message_lower = message.lower()
    
    # Patrones simples
    if any(word in message_lower for word in ["hola", "buenos días", "buenas"]):
        return "saludo"
    elif any(word in message_lower for word in ["adiós", "hasta luego", "chao"]):
        return "despedida"
    elif any(word in message_lower for word in ["ayuda", "soporte", "problema"]):
        return "soporte"
    elif any(word in message_lower for word in ["cita", "appointment", "reserva"]):
        return "cita"
    elif any(word in message_lower for word in ["producto", "precio", "comprar"]):
        return "venta"
    else:
        return "general"

def get_response(intent: str, message: str) -> str:
    """Obtener respuesta según la intención"""
    responses = {
        "saludo": [
            "¡Hola! ¿En qué puedo ayudarte hoy?",
            "¡Buenos días! ¿Cómo estás?",
            "¡Hola! Soy tu asistente virtual. ¿En qué puedo servirte?"
        ],
        "despedida": [
            "¡Hasta luego! Que tengas un buen día.",
            "¡Adiós! Ha sido un placer ayudarte.",
            "¡Que tengas un excelente día!"
        ],
        "soporte": [
            "Te ayudo con el soporte técnico. ¿Cuál es tu problema?",
            "Estoy aquí para ayudarte. ¿Qué necesitas?",
            "Cuéntame más sobre el problema que tienes."
        ],
        "cita": [
            "Perfecto, te ayudo a programar una cita. ¿Qué día prefieres?",
            "Para agendar tu cita, necesito saber tu disponibilidad.",
            "Te ayudo con la reserva. ¿Qué servicio necesitas?"
        ],
        "venta": [
            "Te ayudo con información sobre nuestros productos.",
            "Tenemos excelentes ofertas. ¿Qué te interesa?",
            "Te muestro nuestro catálogo de productos."
        ],
        "general": [
            "Entiendo. ¿Puedes ser más específico?",
            "Interesante. ¿En qué más puedo ayudarte?",
            "Gracias por tu mensaje. ¿Hay algo más en lo que pueda asistirte?"
        ]
    }
    
    import random
    return random.choice(responses.get(intent, responses["general"]))

# Endpoints
@app.get("/")
async def root():
    """Página principal"""
    return {
        "message": "🤖 Chatbot Inteligente - Servidor de Prueba",
        "version": "1.0.0",
        "status": "funcionando",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "stats": "/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Verificar estado del servidor"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Servidor funcionando correctamente"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Procesar mensaje del chat"""
    try:
        # Procesar mensaje
        intent = understand_intent(request.message)
        response = get_response(intent, request.message)
        
        # Guardar en base de datos
        db.save_conversation(
            request.user_id,
            request.message,
            response,
            intent
        )
        
        return ChatResponse(
            response=response,
            intent=intent,
            status="success",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error en chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {e}")

@app.get("/stats")
async def get_stats():
    """Obtener estadísticas"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT intent, COUNT(*) as count 
                FROM conversations 
                GROUP BY intent
            """)
            intent_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
        return {
            "total_conversations": total_conversations,
            "intent_stats": intent_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor de prueba...")
    logger.info("📡 Servidor disponible en http://localhost:8000")
    logger.info("🛑 Presiona Ctrl+C para detener")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    ) 