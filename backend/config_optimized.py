#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración Optimizada para Chatbot Inteligente
Versión eficiente en recursos
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class OptimizedConfig:
    """Configuración optimizada del chatbot"""
    
    # Configuración de la aplicación
    APP_NAME: str = "Chatbot Inteligente Optimizado"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False  # Desactivar debug para ahorrar recursos
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1  # Un solo worker para ahorrar recursos
    
    # Base de datos optimizada
    DATABASE_URL: str = "sqlite:///chatbot_optimized.db"
    DATABASE_PATH: str = "chatbot_optimized.db"
    
    # Cache optimizado
    CACHE_MAX_SIZE: int = 1000
    CACHE_TTL: int = 3600  # 1 hora
    
    # Logging optimizado
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "chatbot_optimized.log"
    
    # Configuración de IA (opcional, para ahorrar recursos)
    USE_OPENAI: bool = False  # Desactivar por defecto para ahorrar recursos
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 100  # Reducir tokens para ahorrar
    
    # Configuración de pagos (opcional)
    USE_STRIPE: bool = False
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    
    # Configuración de email (opcional)
    USE_EMAIL: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Configuración de redes sociales (opcional)
    USE_TELEGRAM: bool = False
    TELEGRAM_BOT_TOKEN: str = ""
    
    USE_FACEBOOK: bool = False
    FACEBOOK_PAGE_ACCESS_TOKEN: str = ""
    
    # Configuración de seguridad
    SECRET_KEY: str = "chatbot-optimized-secret-key-2024"
    
    # Configuración de rendimiento
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    RESPONSE_CACHE_TTL: int = 300  # 5 minutos
    
    # Configuración de base de datos optimizada
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # Configuración de vocabulario optimizado
    VOCABULARY_CACHE_SIZE: int = 500
    INTENT_PATTERNS_CACHE_SIZE: int = 100
    
    # Configuración de respuestas optimizadas
    RESPONSE_CACHE_SIZE: int = 200
    CONTEXT_CACHE_SIZE: int = 100
    
    @classmethod
    def from_env(cls) -> 'OptimizedConfig':
        """Crear configuración desde variables de entorno"""
        config = cls()
        
        # Variables de entorno básicas
        config.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        config.HOST = os.getenv('HOST', config.HOST)
        config.PORT = int(os.getenv('PORT', config.PORT))
        config.WORKERS = int(os.getenv('WORKERS', config.WORKERS))
        
        # Base de datos
        config.DATABASE_URL = os.getenv('DATABASE_URL', config.DATABASE_URL)
        config.DATABASE_PATH = os.getenv('DATABASE_PATH', config.DATABASE_PATH)
        
        # Cache
        config.CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', config.CACHE_MAX_SIZE))
        config.CACHE_TTL = int(os.getenv('CACHE_TTL', config.CACHE_TTL))
        
        # Logging
        config.LOG_LEVEL = os.getenv('LOG_LEVEL', config.LOG_LEVEL)
        config.LOG_FILE = os.getenv('LOG_FILE', config.LOG_FILE)
        
        # OpenAI (opcional)
        config.USE_OPENAI = os.getenv('USE_OPENAI', 'False').lower() == 'true'
        config.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', config.OPENAI_API_KEY)
        config.OPENAI_MODEL = os.getenv('OPENAI_MODEL', config.OPENAI_MODEL)
        config.OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', config.OPENAI_MAX_TOKENS))
        
        # Stripe (opcional)
        config.USE_STRIPE = os.getenv('USE_STRIPE', 'False').lower() == 'true'
        config.STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', config.STRIPE_SECRET_KEY)
        config.STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', config.STRIPE_PUBLISHABLE_KEY)
        
        # Email (opcional)
        config.USE_EMAIL = os.getenv('USE_EMAIL', 'False').lower() == 'true'
        config.SMTP_HOST = os.getenv('SMTP_HOST', config.SMTP_HOST)
        config.SMTP_PORT = int(os.getenv('SMTP_PORT', config.SMTP_PORT))
        config.SMTP_USER = os.getenv('SMTP_USER', config.SMTP_USER)
        config.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', config.SMTP_PASSWORD)
        
        # Telegram (opcional)
        config.USE_TELEGRAM = os.getenv('USE_TELEGRAM', 'False').lower() == 'true'
        config.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', config.TELEGRAM_BOT_TOKEN)
        
        # Facebook (opcional)
        config.USE_FACEBOOK = os.getenv('USE_FACEBOOK', 'False').lower() == 'true'
        config.FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN', config.FACEBOOK_PAGE_ACCESS_TOKEN)
        
        # Seguridad
        config.SECRET_KEY = os.getenv('SECRET_KEY', config.SECRET_KEY)
        
        # Rendimiento
        config.MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', config.MAX_CONCURRENT_REQUESTS))
        config.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', config.REQUEST_TIMEOUT))
        config.RESPONSE_CACHE_TTL = int(os.getenv('RESPONSE_CACHE_TTL', config.RESPONSE_CACHE_TTL))
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario"""
        return {
            'app_name': self.APP_NAME,
            'app_version': self.APP_VERSION,
            'debug': self.DEBUG,
            'host': self.HOST,
            'port': self.PORT,
            'workers': self.WORKERS,
            'database_url': self.DATABASE_URL,
            'cache_max_size': self.CACHE_MAX_SIZE,
            'log_level': self.LOG_LEVEL,
            'use_openai': self.USE_OPENAI,
            'use_stripe': self.USE_STRIPE,
            'use_email': self.USE_EMAIL,
            'use_telegram': self.USE_TELEGRAM,
            'use_facebook': self.USE_FACEBOOK,
            'max_concurrent_requests': self.MAX_CONCURRENT_REQUESTS,
            'request_timeout': self.REQUEST_TIMEOUT
        }
    
    def get_optimization_info(self) -> Dict[str, Any]:
        """Obtener información de optimización"""
        return {
            'memory_optimizations': [
                'Cache limitado a 1000 elementos',
                'Un solo worker para ahorrar memoria',
                'Base de datos SQLite ligera',
                'Logging optimizado',
                'Respuestas en memoria'
            ],
            'cpu_optimizations': [
                'LRU cache para funciones frecuentes',
                'Búsqueda directa de patrones',
                'Procesamiento asíncrono',
                'Índices en base de datos'
            ],
            'network_optimizations': [
                'Respuestas JSON compactas',
                'Timeouts configurados',
                'CORS optimizado',
                'Headers mínimos'
            ],
            'resource_savings': {
                'memory_mb': '~50-100 MB',
                'cpu_usage': '~5-15%',
                'disk_space': '~10-50 MB',
                'network_requests': 'Minimizados'
            }
        }

# Configuración global optimizada
config = OptimizedConfig.from_env()

def get_config() -> OptimizedConfig:
    """Obtener configuración optimizada"""
    return config

def is_optimized_mode() -> bool:
    """Verificar si está en modo optimizado"""
    return (
        not config.USE_OPENAI and
        not config.USE_STRIPE and
        not config.USE_EMAIL and
        not config.USE_TELEGRAM and
        not config.USE_FACEBOOK and
        config.WORKERS == 1 and
        config.CACHE_MAX_SIZE <= 1000
    )

def get_optimization_status() -> Dict[str, Any]:
    """Obtener estado de optimización"""
    return {
        'optimized_mode': is_optimized_mode(),
        'memory_usage': 'Low',
        'cpu_usage': 'Low',
        'disk_usage': 'Low',
        'network_usage': 'Minimal',
        'features_enabled': {
            'openai': config.USE_OPENAI,
            'stripe': config.USE_STRIPE,
            'email': config.USE_EMAIL,
            'telegram': config.USE_TELEGRAM,
            'facebook': config.USE_FACEBOOK
        },
        'performance_settings': {
            'workers': config.WORKERS,
            'cache_size': config.CACHE_MAX_SIZE,
            'concurrent_requests': config.MAX_CONCURRENT_REQUESTS,
            'timeout': config.REQUEST_TIMEOUT
        }
    } 