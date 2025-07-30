import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Configuración de la aplicación
    APP_NAME: str = "Chatbot Inteligente"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    
    # Configuración de OpenAI
    OPENAI_API_KEY: str = "your-openai-api-key"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 150
    OPENAI_TEMPERATURE: float = 0.7
    
    # Configuración de Stripe (pagos)
    STRIPE_SECRET_KEY: str = "your-stripe-secret-key"
    STRIPE_PUBLISHABLE_KEY: str = "your-stripe-publishable-key"
    STRIPE_WEBHOOK_SECRET: str = "your-stripe-webhook-secret"
    
    # Configuración de PayPal
    PAYPAL_CLIENT_ID: str = "your-paypal-client-id"
    PAYPAL_CLIENT_SECRET: str = "your-paypal-client-secret"
    PAYPAL_MODE: str = "sandbox"  # sandbox o live
    
    # Configuración de redes sociales
    TELEGRAM_BOT_TOKEN: str = "your-telegram-bot-token"
    FACEBOOK_PAGE_ACCESS_TOKEN: str = "your-facebook-page-access-token"
    WHATSAPP_BUSINESS_TOKEN: str = "your-whatsapp-business-token"
    
    # Configuración de email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-email-password"
    
    # Configuración de seguridad
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "chatbot.log"
    
    # Configuración de horarios
    BUSINESS_HOURS = {
        0: [{"start": "09:00", "end": "17:00"}],  # Lunes
        1: [{"start": "09:00", "end": "17:00"}],  # Martes
        2: [{"start": "09:00", "end": "17:00"}],  # Miércoles
        3: [{"start": "09:00", "end": "17:00"}],  # Jueves
        4: [{"start": "09:00", "end": "17:00"}],  # Viernes
        5: [{"start": "09:00", "end": "13:00"}],  # Sábado
        6: []  # Domingo cerrado
    }
    
    # Configuración de servicios disponibles
    SERVICES = {
        "consulta": {"name": "Consulta General", "duration": 30, "price": 50},
        "revisión": {"name": "Revisión Médica", "duration": 60, "price": 80},
        "tratamiento": {"name": "Tratamiento", "duration": 90, "price": 120},
        "examen": {"name": "Examen", "duration": 45, "price": 60},
        "limpieza": {"name": "Limpieza", "duration": 30, "price": 40}
    }
    
    # Configuración de productos
    PRODUCTS = {
        "1": {
            "id": "1",
            "name": "Producto Premium",
            "description": "Producto de alta calidad con garantía",
            "price": 99.99,
            "stock": 50,
            "category": "premium"
        },
        "2": {
            "id": "2",
            "name": "Servicio Básico", 
            "description": "Servicio esencial para tus necesidades",
            "price": 29.99,
            "stock": 100,
            "category": "basic"
        },
        "3": {
            "id": "3",
            "name": "Paquete Completo",
            "description": "Todo lo que necesitas en un solo paquete",
            "price": 149.99,
            "stock": 25,
            "category": "package"
        }
    }
    
    # Configuración de respuestas automáticas
    AUTO_RESPONSES = {
        "greeting": "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?",
        "appointment": "Perfecto, te ayudo a agendar una cita. ¿Qué tipo de servicio necesitas?",
        "cancel_appointment": "Entiendo que quieres cancelar una cita. ¿Cuál es tu número de cita?",
        "reschedule": "Te ayudo a reprogramar tu cita. ¿Cuál es tu número de cita actual?",
        "sales": "¡Genial! Te muestro nuestro catálogo de productos. ¿Qué te interesa?",
        "customer_service": "Estoy aquí para ayudarte. ¿Cuál es tu consulta?",
        "goodbye": "¡Hasta luego! Ha sido un placer ayudarte. ¡Que tengas un buen día!"
    }
    
    # Configuración de intents
    INTENTS = {
        "greeting": ["hola", "buenos días", "buenas", "saludos"],
        "appointment": ["cita", "agendar", "reservar", "consulta", "visita"],
        "cancel_appointment": ["cancelar", "cancelar cita", "anular"],
        "reschedule": ["cambiar", "mover", "reprogramar", "otro día"],
        "sales": ["comprar", "producto", "precio", "catalogo", "venta"],
        "customer_service": ["ayuda", "soporte", "problema", "queja"],
        "goodbye": ["adiós", "hasta luego", "chao", "nos vemos"]
    }
    
    # Configuración de categorías de soporte
    SUPPORT_CATEGORIES = {
        "technical": "Problemas técnicos",
        "billing": "Facturación y pagos",
        "appointment": "Citas y reservas", 
        "product": "Productos y servicios",
        "general": "Consultas generales"
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

def get_settings() -> Settings:
    """Obtener configuración"""
    return settings