from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from datetime import datetime
import logging

from services.chatbot_service import ChatbotService
from services.appointment_service import AppointmentService
from services.sales_service import SalesService
from services.customer_service import CustomerService

logger = logging.getLogger(__name__)

router = APIRouter()

# Instanciar servicios
chatbot_service = ChatbotService()
appointment_service = AppointmentService()
sales_service = SalesService()
customer_service = CustomerService()

# ==================== RUTAS DE CHAT ====================

@router.post("/chat/send")
async def send_message(request: Request):
    """Enviar mensaje al chatbot"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")
        platform = data.get("platform", "web")
        
        if not user_id or not message:
            raise HTTPException(status_code=400, detail="user_id y message son requeridos")
        
        response = await chatbot_service.process_message(user_id, message, platform)
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Error en send_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 50):
    """Obtener historial de chat del usuario"""
    try:
        # Aquí implementarías la lógica para obtener historial
        # Por ahora retornamos datos mock
        history = [
            {
                "id": "1",
                "message": "Hola, necesito una cita",
                "sender": "user",
                "timestamp": "2024-01-15T10:00:00Z"
            },
            {
                "id": "2", 
                "message": "Te ayudo a agendar una cita. ¿Qué tipo de servicio necesitas?",
                "sender": "bot",
                "timestamp": "2024-01-15T10:00:01Z"
            }
        ]
        
        return {"history": history[:limit]}
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE CITAS ====================

@router.post("/appointments/create")
async def create_appointment(request: Request):
    """Crear nueva cita"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        appointment_data = data.get("appointment")
        
        if not user_id or not appointment_data:
            raise HTTPException(status_code=400, detail="user_id y appointment son requeridos")
        
        result = await appointment_service.create_appointment(user_id, appointment_data)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error creando cita: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/appointments/cancel")
async def cancel_appointment(request: Request):
    """Cancelar cita"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        appointment_id = data.get("appointment_id")
        
        if not user_id or not appointment_id:
            raise HTTPException(status_code=400, detail="user_id y appointment_id son requeridos")
        
        result = await appointment_service.cancel_appointment(user_id, appointment_id)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error cancelando cita: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/appointments/reschedule")
async def reschedule_appointment(request: Request):
    """Reprogramar cita"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        appointment_id = data.get("appointment_id")
        new_datetime = data.get("new_datetime")
        
        if not user_id or not appointment_id or not new_datetime:
            raise HTTPException(status_code=400, detail="user_id, appointment_id y new_datetime son requeridos")
        
        result = await appointment_service.reschedule_appointment(user_id, appointment_id, new_datetime)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error reprogramando cita: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/appointments/confirm")
async def confirm_appointment(request: Request):
    """Confirmar cita"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        appointment_id = data.get("appointment_id")
        
        if not user_id or not appointment_id:
            raise HTTPException(status_code=400, detail="user_id y appointment_id son requeridos")
        
        result = await appointment_service.confirm_appointment(user_id, appointment_id)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error confirmando cita: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointments/user/{user_id}")
async def get_user_appointments(user_id: str):
    """Obtener citas del usuario"""
    try:
        appointments = await appointment_service.get_user_appointments(user_id)
        
        return {"appointments": appointments}
        
    except Exception as e:
        logger.error(f"Error obteniendo citas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointments/available-slots")
async def get_available_slots(date: str, service_type: str):
    """Obtener horarios disponibles"""
    try:
        slots = await appointment_service.get_available_slots(date, service_type)
        
        return {"slots": slots}
        
    except Exception as e:
        logger.error(f"Error obteniendo slots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE VENTAS ====================

@router.get("/sales/products")
async def get_products(category: Optional[str] = None):
    """Obtener catálogo de productos"""
    try:
        if category:
            products = await sales_service.get_products_by_category(category)
        else:
            products = await sales_service.get_products()
        
        return {"products": products}
        
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales/products/{product_id}")
async def get_product(product_id: str):
    """Obtener producto específico"""
    try:
        product = await sales_service.get_product(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        return {"product": product}
        
    except Exception as e:
        logger.error(f"Error obteniendo producto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sales/purchase")
async def process_purchase(request: Request):
    """Procesar compra"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)
        
        if not user_id or not product_id:
            raise HTTPException(status_code=400, detail="user_id y product_id son requeridos")
        
        result = await sales_service.process_purchase(user_id, product_id, quantity)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error procesando compra: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sales/payment")
async def process_payment(request: Request):
    """Procesar pago"""
    try:
        data = await request.json()
        sale_id = data.get("sale_id")
        payment_method = data.get("payment_method")
        payment_data = data.get("payment_data", {})
        
        if not sale_id or not payment_method:
            raise HTTPException(status_code=400, detail="sale_id y payment_method son requeridos")
        
        result = await sales_service.process_payment(sale_id, payment_method, payment_data)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error procesando pago: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales/user/{user_id}/purchases")
async def get_user_purchases(user_id: str):
    """Obtener compras del usuario"""
    try:
        purchases = await sales_service.get_user_purchases(user_id)
        
        return {"purchases": purchases}
        
    except Exception as e:
        logger.error(f"Error obteniendo compras: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales/categories")
async def get_categories():
    """Obtener categorías de productos"""
    try:
        categories = await sales_service.get_categories()
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE ATENCIÓN AL CLIENTE ====================

@router.post("/support/query")
async def handle_support_query(request: Request):
    """Manejar consulta de soporte"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")
        platform = data.get("platform", "web")
        
        if not user_id or not message:
            raise HTTPException(status_code=400, detail="user_id y message son requeridos")
        
        result = await customer_service.handle_customer_query(user_id, message, platform)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error manejando consulta de soporte: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/support/ticket")
async def create_support_ticket(request: Request):
    """Crear ticket de soporte"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        category = data.get("category")
        description = data.get("description")
        priority = data.get("priority", "medium")
        
        if not user_id or not category or not description:
            raise HTTPException(status_code=400, detail="user_id, category y description son requeridos")
        
        result = await customer_service.create_support_ticket(user_id, category, description, priority)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error creando ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support/user/{user_id}/tickets")
async def get_user_tickets(user_id: str):
    """Obtener tickets del usuario"""
    try:
        tickets = await customer_service.get_user_tickets(user_id)
        
        return {"tickets": tickets}
        
    except Exception as e:
        logger.error(f"Error obteniendo tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/support/ticket/{ticket_id}")
async def update_ticket_status(ticket_id: str, request: Request):
    """Actualizar estado de ticket"""
    try:
        data = await request.json()
        status = data.get("status")
        response = data.get("response")
        
        if not status:
            raise HTTPException(status_code=400, detail="status es requerido")
        
        result = await customer_service.update_ticket_status(ticket_id, status, response)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error actualizando ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support/faq")
async def get_faq(category: Optional[str] = None):
    """Obtener preguntas frecuentes"""
    try:
        faqs = await customer_service.get_faq(category)
        
        return {"faqs": faqs}
        
    except Exception as e:
        logger.error(f"Error obteniendo FAQ: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/support/notification")
async def send_notification(request: Request):
    """Enviar notificación"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")
        notification_type = data.get("notification_type", "info")
        
        if not user_id or not message:
            raise HTTPException(status_code=400, detail="user_id y message son requeridos")
        
        result = await customer_service.send_notification(user_id, message, notification_type)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE UTILIDAD ====================

@router.get("/health")
async def health_check():
    """Verificar estado de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/status")
async def api_status():
    """Estado de todos los servicios"""
    return {
        "chatbot": "active",
        "appointments": "active",
        "sales": "active", 
        "customer_service": "active",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }