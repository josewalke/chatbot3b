from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from typing import Dict, Any, List, Optional

# Crear la aplicación FastAPI
app = FastAPI(title="Chatbot Inteligente", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str
    user_id: str

class AppointmentRequest(BaseModel):
    user_id: str
    service_id: int
    date: str
    time: str
    notes: Optional[str] = None

class SupportQuery(BaseModel):
    query: str
    user_id: str

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

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "Chatbot Inteligente API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-api"}

@app.get("/status")
async def api_status():
    return {
        "status": "online",
        "version": "1.0.0",
        "features": ["chat", "appointments", "sales", "support"]
    }

# Chat endpoints
@app.post("/chat/send")
async def send_message(chat_message: ChatMessage):
    """Procesar mensaje del chat"""
    message = chat_message.message.lower()
    
    # Detección simple de intenciones
    if any(word in message for word in ["cita", "agendar", "reservar", "appointment"]):
        response = {
            "message": "Perfecto, te ayudo a agendar una cita. ¿Qué servicio te interesa?",
            "intent": "appointment",
            "metadata": {
                "action": "show_services",
                "services": SERVICES
            }
        }
    elif any(word in message for word in ["producto", "comprar", "venta", "precio"]):
        response = {
            "message": "Te muestro nuestros productos disponibles:",
            "intent": "sales",
            "metadata": {
                "action": "show_products",
                "products": PRODUCTS
            }
        }
    elif any(word in message for word in ["ayuda", "soporte", "problema", "consulta"]):
        response = {
            "message": "Te ayudo con tu consulta. ¿En qué puedo asistirte?",
            "intent": "support",
            "metadata": {
                "action": "show_support_options"
            }
        }
    else:
        response = {
            "message": "Hola! Soy tu asistente virtual. Puedo ayudarte con:\n- Agendar citas\n- Información de productos\n- Atención al cliente\n¿En qué te puedo ayudar?",
            "intent": "greeting",
            "metadata": {
                "action": "show_options"
            }
        }
    
    return response

# Appointment endpoints
@app.get("/appointments/available-slots")
async def get_available_slots():
    """Obtener horarios disponibles"""
    slots = []
    for hour in range(9, 18):  # 9 AM a 6 PM
        slots.append(f"{hour:02d}:00")
        slots.append(f"{hour:02d}:30")
    
    return {
        "available_slots": slots,
        "services": SERVICES
    }

@app.post("/appointments/create")
async def create_appointment(appointment: AppointmentRequest):
    """Crear una nueva cita"""
    # Simular creación exitosa
    appointment_id = len(appointment.dict()) + 1000  # ID simulado
    
    return {
        "success": True,
        "appointment_id": appointment_id,
        "message": f"Cita creada exitosamente para el {appointment.date} a las {appointment.time}",
        "appointment": appointment.dict()
    }

@app.get("/appointments/user/{user_id}")
async def get_user_appointments(user_id: str):
    """Obtener citas del usuario"""
    # Simular citas existentes
    appointments = [
        {
            "id": 1,
            "service": "Consulta General",
            "date": "2024-01-15",
            "time": "10:00",
            "status": "confirmed"
        }
    ]
    
    return {"appointments": appointments}

# Sales endpoints
@app.get("/sales/products")
async def get_products():
    """Obtener catálogo de productos"""
    return {"products": PRODUCTS}

@app.get("/sales/products/{product_id}")
async def get_product(product_id: int):
    """Obtener producto específico"""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@app.post("/sales/purchase")
async def process_purchase(purchase_data: Dict[str, Any]):
    """Procesar una compra"""
    return {
        "success": True,
        "order_id": f"ORD-{len(purchase_data)}",
        "message": "Compra procesada exitosamente",
        "total": purchase_data.get("total", 0)
    }

# Support endpoints
@app.post("/support/query")
async def handle_support_query(query: SupportQuery):
    """Manejar consulta de soporte"""
    query_text = query.query.lower()
    
    if any(word in query_text for word in ["devolución", "reembolso"]):
        response = "Nuestra política de devoluciones permite reembolsos dentro de los 30 días de la compra."
    elif any(word in query_text for word in ["garantía", "garantia"]):
        response = "Todos nuestros productos tienen garantía de 1 año."
    elif any(word in query_text for word in ["envío", "envio", "entrega"]):
        response = "Los envíos se realizan en 2-3 días hábiles."
    else:
        response = "Gracias por tu consulta. Un agente te contactará pronto."
    
    return {
        "response": response,
        "escalated": False,
        "ticket_id": f"TKT-{len(query.query)}"
    }

# Webhook endpoints
@app.post("/webhook/chat")
async def webhook_chat(data: Dict[str, Any]):
    """Webhook para integración con redes sociales"""
    return {"status": "received", "platform": data.get("platform", "unknown")}

@app.post("/webhook/appointment")
async def webhook_appointment(data: Dict[str, Any]):
    """Webhook para citas desde redes sociales"""
    return {"status": "appointment_processed", "data": data}

@app.post("/webhook/sales")
async def webhook_sales(data: Dict[str, Any]):
    """Webhook para ventas desde redes sociales"""
    return {"status": "sale_processed", "data": data}

if __name__ == "__main__":
    print("🚀 Iniciando Chatbot API...")
    print("📡 Servidor disponible en: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)