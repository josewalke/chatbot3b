from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import os
from datetime import datetime, timedelta
import json
import logging
from typing import Optional, List

# Importar módulos del chatbot
from models.database import engine, Base
from models.models import *
from services.chatbot_service import ChatbotService
from services.appointment_service import AppointmentService
from services.sales_service import SalesService
from services.customer_service import CustomerService
from api.routes import router as api_router
from config.settings import Settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Chatbot Inteligente",
    description="Chatbot gratuito para WordPress y redes sociales",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Incluir rutas de API
app.include_router(api_router, prefix="/api/v1")

# Instanciar servicios
chatbot_service = ChatbotService()
appointment_service = AppointmentService()
sales_service = SalesService()
customer_service = CustomerService()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal del chatbot"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """Interfaz de chat"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/webhook/chat")
async def chat_webhook(request: Request):
    """Webhook para recibir mensajes de chat"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")
        platform = data.get("platform", "web")
        
        # Procesar mensaje con el chatbot
        response = await chatbot_service.process_message(user_id, message, platform)
        
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en webhook de chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/appointment")
async def appointment_webhook(request: Request):
    """Webhook para gestión de citas"""
    try:
        data = await request.json()
        action = data.get("action")
        user_id = data.get("user_id")
        
        if action == "create":
            appointment_data = data.get("appointment")
            result = await appointment_service.create_appointment(user_id, appointment_data)
        elif action == "cancel":
            appointment_id = data.get("appointment_id")
            result = await appointment_service.cancel_appointment(user_id, appointment_id)
        elif action == "reschedule":
            appointment_id = data.get("appointment_id")
            new_datetime = data.get("new_datetime")
            result = await appointment_service.reschedule_appointment(user_id, appointment_id, new_datetime)
        elif action == "confirm":
            appointment_id = data.get("appointment_id")
            result = await appointment_service.confirm_appointment(user_id, appointment_id)
        else:
            raise HTTPException(status_code=400, detail="Acción no válida")
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en webhook de citas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/sales")
async def sales_webhook(request: Request):
    """Webhook para ventas"""
    try:
        data = await request.json()
        action = data.get("action")
        user_id = data.get("user_id")
        
        if action == "show_products":
            products = await sales_service.get_products()
            return {"success": True, "products": products}
        elif action == "purchase":
            product_id = data.get("product_id")
            quantity = data.get("quantity", 1)
            result = await sales_service.process_purchase(user_id, product_id, quantity)
            return {"success": True, "result": result}
        else:
            raise HTTPException(status_code=400, detail="Acción no válida")
    except Exception as e:
        logger.error(f"Error en webhook de ventas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/status")
async def api_status():
    """Estado de las APIs"""
    return {
        "chatbot": "active",
        "appointments": "active", 
        "sales": "active",
        "customer_service": "active"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )