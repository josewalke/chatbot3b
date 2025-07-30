import openai
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import User, Conversation, Message, BotResponse
import re

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        # Configurar OpenAI (gratuito con límites)
        self.openai_client = openai.OpenAI(
            api_key="your-openai-api-key",  # Configurar en .env
            base_url="https://api.openai.com/v1"
        )
        
        # Intents predefinidos
        self.intents = {
            "greeting": ["hola", "buenos días", "buenas", "saludos"],
            "appointment": ["cita", "agendar", "reservar", "consulta", "visita"],
            "cancel_appointment": ["cancelar", "cancelar cita", "anular"],
            "reschedule": ["cambiar", "mover", "reprogramar", "otro día"],
            "sales": ["comprar", "producto", "precio", "catalogo", "venta"],
            "customer_service": ["ayuda", "soporte", "problema", "queja"],
            "goodbye": ["adiós", "hasta luego", "chao", "nos vemos"]
        }
        
        # Respuestas predefinidas
        self.responses = {
            "greeting": "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?",
            "appointment": "Perfecto, te ayudo a agendar una cita. ¿Qué tipo de servicio necesitas?",
            "cancel_appointment": "Entiendo que quieres cancelar una cita. ¿Cuál es tu número de cita?",
            "reschedule": "Te ayudo a reprogramar tu cita. ¿Cuál es tu número de cita actual?",
            "sales": "¡Genial! Te muestro nuestro catálogo de productos. ¿Qué te interesa?",
            "customer_service": "Estoy aquí para ayudarte. ¿Cuál es tu consulta?",
            "goodbye": "¡Hasta luego! Ha sido un placer ayudarte. ¡Que tengas un buen día!"
        }

    async def process_message(self, user_id: str, message: str, platform: str = "web") -> Dict:
        """Procesar mensaje del usuario y generar respuesta"""
        try:
            # Obtener o crear usuario
            user = await self._get_or_create_user(user_id, platform)
            
            # Obtener o crear conversación
            conversation = await self._get_or_create_conversation(user.id, platform)
            
            # Guardar mensaje del usuario
            await self._save_message(conversation.id, message, "user")
            
            # Detectar intent
            intent = self._detect_intent(message.lower())
            
            # Generar respuesta
            response = await self._generate_response(intent, message, user)
            
            # Guardar respuesta del bot
            await self._save_message(conversation.id, response["text"], "bot", response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return {
                "text": "Lo siento, tuve un problema procesando tu mensaje. ¿Puedes intentar de nuevo?",
                "type": "text",
                "intent": "error"
            }

    def _detect_intent(self, message: str) -> str:
        """Detectar intent del mensaje"""
        # Buscar en intents predefinidos
        for intent, keywords in self.intents.items():
            for keyword in keywords:
                if keyword in message:
                    return intent
        
        # Si no se encuentra, usar IA para clasificar
        return self._classify_with_ai(message)

    def _classify_with_ai(self, message: str) -> str:
        """Clasificar mensaje usando IA"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Clasifica el siguiente mensaje en una de estas categorías: greeting, appointment, cancel_appointment, reschedule, sales, customer_service, goodbye. Responde solo con la categoría."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            intent = response.choices[0].message.content.strip().lower()
            return intent if intent in self.intents else "customer_service"
            
        except Exception as e:
            logger.error(f"Error clasificando con IA: {e}")
            return "customer_service"

    async def _generate_response(self, intent: str, original_message: str, user) -> Dict:
        """Generar respuesta basada en el intent"""
        try:
            if intent == "appointment":
                return await self._handle_appointment_intent(original_message, user)
            elif intent == "cancel_appointment":
                return await self._handle_cancel_appointment_intent(original_message, user)
            elif intent == "reschedule":
                return await self._handle_reschedule_intent(original_message, user)
            elif intent == "sales":
                return await self._handle_sales_intent(original_message, user)
            elif intent == "customer_service":
                return await self._handle_customer_service_intent(original_message, user)
            else:
                # Respuesta predefinida
                return {
                    "text": self.responses.get(intent, "Entiendo tu mensaje. ¿En qué más puedo ayudarte?"),
                    "type": "text",
                    "intent": intent
                }
                
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return {
                "text": "Lo siento, tuve un problema generando la respuesta. ¿Puedes intentar de nuevo?",
                "type": "text",
                "intent": "error"
            }

    async def _handle_appointment_intent(self, message: str, user) -> Dict:
        """Manejar intent de agendar cita"""
        # Extraer información de la cita del mensaje
        service_type = self._extract_service_type(message)
        date_time = self._extract_datetime(message)
        
        if service_type and date_time:
            # Crear cita directamente
            return {
                "text": f"Perfecto, he agendado tu cita de {service_type} para el {date_time}. ¿Confirmas?",
                "type": "text",
                "intent": "appointment",
                "metadata": {
                    "service_type": service_type,
                    "datetime": date_time,
                    "action": "confirm_appointment"
                }
            }
        else:
            # Solicitar más información
            return {
                "text": "Te ayudo a agendar tu cita. ¿Qué tipo de servicio necesitas y para qué fecha?",
                "type": "text",
                "intent": "appointment",
                "metadata": {
                    "action": "request_appointment_info"
                }
            }

    async def _handle_cancel_appointment_intent(self, message: str, user) -> Dict:
        """Manejar intent de cancelar cita"""
        appointment_id = self._extract_appointment_id(message)
        
        if appointment_id:
            return {
                "text": f"He cancelado tu cita #{appointment_id}. ¿Necesitas algo más?",
                "type": "text",
                "intent": "cancel_appointment",
                "metadata": {
                    "appointment_id": appointment_id,
                    "action": "appointment_cancelled"
                }
            }
        else:
            return {
                "text": "Para cancelar tu cita, necesito el número de cita. ¿Cuál es?",
                "type": "text",
                "intent": "cancel_appointment",
                "metadata": {
                    "action": "request_appointment_id"
                }
            }

    async def _handle_reschedule_intent(self, message: str, user) -> Dict:
        """Manejar intent de reprogramar cita"""
        appointment_id = self._extract_appointment_id(message)
        new_datetime = self._extract_datetime(message)
        
        if appointment_id and new_datetime:
            return {
                "text": f"He reprogramado tu cita #{appointment_id} para el {new_datetime}. ¿Confirmas?",
                "type": "text",
                "intent": "reschedule",
                "metadata": {
                    "appointment_id": appointment_id,
                    "new_datetime": new_datetime,
                    "action": "appointment_rescheduled"
                }
            }
        else:
            return {
                "text": "Para reprogramar tu cita, necesito el número de cita y la nueva fecha. ¿Cuáles son?",
                "type": "text",
                "intent": "reschedule",
                "metadata": {
                    "action": "request_reschedule_info"
                }
            }

    async def _handle_sales_intent(self, message: str, user) -> Dict:
        """Manejar intent de ventas"""
        return {
            "text": "¡Perfecto! Te muestro nuestro catálogo de productos. ¿Qué te interesa?",
            "type": "text",
            "intent": "sales",
            "metadata": {
                "action": "show_products"
            }
        }

    async def _handle_customer_service_intent(self, message: str, user) -> Dict:
        """Manejar intent de atención al cliente"""
        # Usar IA para generar respuesta personalizada
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente de atención al cliente amigable y profesional. Responde de manera útil y concisa."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return {
                "text": response.choices[0].message.content,
                "type": "text",
                "intent": "customer_service"
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta de atención al cliente: {e}")
            return {
                "text": "Entiendo tu consulta. Un agente humano te contactará pronto para ayudarte mejor.",
                "type": "text",
                "intent": "customer_service"
            }

    def _extract_service_type(self, message: str) -> Optional[str]:
        """Extraer tipo de servicio del mensaje"""
        services = ["consulta", "revisión", "tratamiento", "examen", "limpieza"]
        for service in services:
            if service in message.lower():
                return service
        return None

    def _extract_datetime(self, message: str) -> Optional[str]:
        """Extraer fecha y hora del mensaje"""
        # Patrones básicos para fechas
        patterns = [
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{1,2}-\d{1,2}-\d{4})",
            r"mañana",
            r"hoy",
            r"pasado mañana"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1) if match.group(1) else match.group(0)
        
        return None

    def _extract_appointment_id(self, message: str) -> Optional[str]:
        """Extraer ID de cita del mensaje"""
        match = re.search(r"#(\d+)", message)
        if match:
            return match.group(1)
        return None

    async def _get_or_create_user(self, user_id: str, platform: str):
        """Obtener o crear usuario"""
        # Aquí implementarías la lógica de base de datos
        # Por ahora retornamos un objeto mock
        return {"id": 1, "user_id": user_id, "platform": platform}

    async def _get_or_create_conversation(self, user_id: int, platform: str):
        """Obtener o crear conversación"""
        # Aquí implementarías la lógica de base de datos
        # Por ahora retornamos un objeto mock
        return {"id": 1, "user_id": user_id, "platform": platform}

    async def _save_message(self, conversation_id: int, content: str, sender: str, metadata: Dict = None):
        """Guardar mensaje en base de datos"""
        # Aquí implementarías la lógica de base de datos
        logger.info(f"Mensaje guardado: {sender} - {content}")
        pass