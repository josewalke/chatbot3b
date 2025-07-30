import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import User, Conversation, Message
import json
import openai

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self):
        # Configurar OpenAI para atención al cliente
        self.openai_client = openai.OpenAI(
            api_key="your-openai-api-key",  # Configurar en .env
            base_url="https://api.openai.com/v1"
        )
        
        # Categorías de soporte
        self.support_categories = {
            "technical": "Problemas técnicos",
            "billing": "Facturación y pagos", 
            "appointment": "Citas y reservas",
            "product": "Productos y servicios",
            "general": "Consultas generales"
        }
        
        # Respuestas automáticas por categoría
        self.auto_responses = {
            "technical": "Entiendo que tienes un problema técnico. Te ayudo a resolverlo paso a paso.",
            "billing": "Te ayudo con tu consulta de facturación. ¿Cuál es el problema específico?",
            "appointment": "Te ayudo con tu cita. ¿Qué necesitas modificar o consultar?",
            "product": "Te ayudo con información sobre nuestros productos. ¿Qué te interesa?",
            "general": "Estoy aquí para ayudarte. ¿En qué puedo asistirte?"
        }

    async def handle_customer_query(self, user_id: str, message: str, platform: str = "web") -> Dict:
        """Manejar consulta de atención al cliente"""
        try:
            # Categorizar consulta
            category = await self._categorize_query(message)
            
            # Generar respuesta automática
            response = await self._generate_support_response(message, category)
            
            # Verificar si necesita escalación
            needs_escalation = await self._check_escalation_needed(message, category)
            
            if needs_escalation:
                response["escalation"] = True
                response["message"] += "\n\nUn agente humano te contactará pronto para ayudarte mejor."
            
            return response
            
        except Exception as e:
            logger.error(f"Error manejando consulta de cliente: {e}")
            return {
                "success": False,
                "message": "Lo siento, tuve un problema procesando tu consulta. Un agente te contactará pronto.",
                "category": "general",
                "escalation": True
            }

    async def create_support_ticket(self, user_id: str, category: str, description: str, priority: str = "medium") -> Dict:
        """Crear ticket de soporte"""
        try:
            # Validar categoría
            if category not in self.support_categories:
                return {
                    "success": False,
                    "message": "Categoría de soporte no válida"
                }
            
            # Crear ticket
            ticket_id = await self._save_ticket(user_id, category, description, priority)
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "message": f"Ticket de soporte creado exitosamente. Número: {ticket_id}",
                "priority": priority,
                "estimated_response": "24 horas"
            }
            
        except Exception as e:
            logger.error(f"Error creando ticket de soporte: {e}")
            return {
                "success": False,
                "message": "Error interno creando el ticket"
            }

    async def get_user_tickets(self, user_id: str) -> List[Dict]:
        """Obtener tickets del usuario"""
        try:
            # Aquí implementarías la consulta a la base de datos
            # Por ahora retornamos datos mock
            tickets = [
                {
                    "id": "TKT001",
                    "category": "technical",
                    "description": "Problema con el acceso a la plataforma",
                    "status": "open",
                    "priority": "high",
                    "created_at": "2024-01-10 15:30:00",
                    "updated_at": "2024-01-10 16:00:00"
                },
                {
                    "id": "TKT002",
                    "category": "billing", 
                    "description": "Consulta sobre facturación",
                    "status": "resolved",
                    "priority": "medium",
                    "created_at": "2024-01-08 10:15:00",
                    "updated_at": "2024-01-09 14:30:00"
                }
            ]
            
            return tickets
            
        except Exception as e:
            logger.error(f"Error obteniendo tickets: {e}")
            return []

    async def update_ticket_status(self, ticket_id: str, status: str, response: str = None) -> Dict:
        """Actualizar estado de ticket"""
        try:
            # Validar estado
            valid_statuses = ["open", "in_progress", "resolved", "closed"]
            if status not in valid_statuses:
                return {
                    "success": False,
                    "message": "Estado no válido"
                }
            
            # Actualizar ticket
            await self._update_ticket(ticket_id, status, response)
            
            return {
                "success": True,
                "message": f"Ticket {ticket_id} actualizado a {status}"
            }
            
        except Exception as e:
            logger.error(f"Error actualizando ticket: {e}")
            return {
                "success": False,
                "message": "Error interno actualizando el ticket"
            }

    async def _categorize_query(self, message: str) -> str:
        """Categorizar consulta del cliente"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Categoriza la siguiente consulta de soporte en una de estas categorías: technical, billing, appointment, product, general. Responde solo con la categoría."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            category = response.choices[0].message.content.strip().lower()
            return category if category in self.support_categories else "general"
            
        except Exception as e:
            logger.error(f"Error categorizando consulta: {e}")
            return "general"

    async def _generate_support_response(self, message: str, category: str) -> Dict:
        """Generar respuesta de soporte"""
        try:
            # Usar IA para generar respuesta personalizada
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Eres un agente de soporte al cliente especializado en {self.support_categories[category]}. Responde de manera amigable, profesional y útil. Mantén las respuestas concisas pero informativas."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return {
                "success": True,
                "message": response.choices[0].message.content,
                "category": category,
                "escalation": False
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta de soporte: {e}")
            return {
                "success": True,
                "message": self.auto_responses.get(category, "Entiendo tu consulta. ¿En qué puedo ayudarte?"),
                "category": category,
                "escalation": False
            }

    async def _check_escalation_needed(self, message: str, category: str) -> bool:
        """Verificar si la consulta necesita escalación a humano"""
        try:
            # Palabras clave que indican necesidad de escalación
            escalation_keywords = [
                "urgente", "emergencia", "problema grave", "no funciona",
                "error crítico", "reembolso", "demanda", "queja formal"
            ]
            
            # Verificar palabras clave
            message_lower = message.lower()
            for keyword in escalation_keywords:
                if keyword in message_lower:
                    return True
            
            # Verificar longitud del mensaje (muy largo puede indicar problema complejo)
            if len(message) > 500:
                return True
            
            # Verificar categorías que suelen necesitar escalación
            high_escalation_categories = ["billing", "technical"]
            if category in high_escalation_categories:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando escalación: {e}")
            return False

    async def _save_ticket(self, user_id: str, category: str, description: str, priority: str) -> str:
        """Guardar ticket en base de datos"""
        # Aquí implementarías la lógica de base de datos
        # Por ahora retornamos un ID mock
        ticket_id = f"TKT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Ticket creado: {ticket_id} - Categoría: {category} - Prioridad: {priority}")
        return ticket_id

    async def _update_ticket(self, ticket_id: str, status: str, response: str = None):
        """Actualizar ticket en base de datos"""
        # Aquí implementarías la lógica de base de datos
        logger.info(f"Ticket actualizado: {ticket_id} - Estado: {status}")

    async def get_faq(self, category: str = None) -> List[Dict]:
        """Obtener preguntas frecuentes"""
        try:
            faqs = {
                "general": [
                    {
                        "question": "¿Cómo puedo contactar soporte?",
                        "answer": "Puedes contactarnos a través del chat, email o teléfono."
                    },
                    {
                        "question": "¿Cuáles son los horarios de atención?",
                        "answer": "Estamos disponibles 24/7 a través del chat automático."
                    }
                ],
                "technical": [
                    {
                        "question": "¿Qué hago si no puedo acceder a mi cuenta?",
                        "answer": "Verifica tu conexión a internet y tus credenciales. Si persiste, contacta soporte."
                    },
                    {
                        "question": "¿Cómo cambio mi contraseña?",
                        "answer": "Ve a Configuración > Seguridad > Cambiar contraseña."
                    }
                ],
                "billing": [
                    {
                        "question": "¿Cómo solicito un reembolso?",
                        "answer": "Contacta soporte con tu número de factura y motivo del reembolso."
                    },
                    {
                        "question": "¿Qué métodos de pago aceptan?",
                        "answer": "Aceptamos tarjetas de crédito, PayPal y transferencias bancarias."
                    }
                ]
            }
            
            if category:
                return faqs.get(category, [])
            else:
                return faqs
                
        except Exception as e:
            logger.error(f"Error obteniendo FAQ: {e}")
            return []

    async def send_notification(self, user_id: str, message: str, notification_type: str = "info") -> Dict:
        """Enviar notificación al usuario"""
        try:
            # Aquí implementarías la lógica de envío de notificaciones
            # (email, SMS, push notification, etc.)
            logger.info(f"Notificación enviada a {user_id}: {message}")
            
            return {
                "success": True,
                "message": "Notificación enviada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return {
                "success": False,
                "message": "Error enviando notificación"
            }