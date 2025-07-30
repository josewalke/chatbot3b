#!/usr/bin/env python3
"""
Sistema de Aprendizaje Continuo
Ejecuta el entrenamiento automático en segundo plano de forma continua
"""
import asyncio
import threading
import time
import logging
import sqlite3
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from auto_learning import AutoVocabularyLearner, AutoLearningConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContinuousLearningConfig:
    """Configuración del aprendizaje continuo"""
    # Intervalos de entrenamiento
    training_interval_minutes: int = 30  # Cada 30 minutos
    max_training_time_minutes: int = 10  # Máximo 10 minutos por sesión
    
    # Fuentes de aprendizaje
    enable_text_files: bool = True
    enable_api_learning: bool = True
    enable_synthetic_data: bool = True
    enable_spanish_corpus: bool = True
    
    # Límites de recursos
    max_words_per_session: int = 1000
    max_expressions_per_session: int = 500
    
    # Configuración de API
    api_timeout_seconds: int = 30
    max_retries: int = 3
    
    # Configuración de base de datos
    db_path: str = "optimized_learning.db"
    
    # URLs de corpus español
    spanish_corpus_urls: List[str] = None
    
    def __post_init__(self):
        if self.spanish_corpus_urls is None:
            self.spanish_corpus_urls = [
                "https://raw.githubusercontent.com/JorgeDuenasLerin/diccionario-espanol-txt/master/diccionario.txt",
                "https://raw.githubusercontent.com/words/es/master/words.txt",
                "https://raw.githubusercontent.com/words/es/master/words-common.txt"
            ]

class ContinuousLearningSystem:
    """Sistema de aprendizaje continuo en segundo plano"""
    
    def __init__(self, config: Optional[ContinuousLearningConfig] = None):
        self.config = config or ContinuousLearningConfig()
        self.auto_learner = AutoVocabularyLearner(self.config.db_path)
        self.is_running = False
        self.last_training = None
        self.training_stats = {
            'total_sessions': 0,
            'total_words_learned': 0,
            'total_expressions_learned': 0,
            'last_session_time': None,
            'errors': 0
        }
        self._init_database()
    
    def _init_database(self):
        """Inicializar tabla para seguimiento del aprendizaje continuo"""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS continuous_learning_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_end TIMESTAMP,
                        words_learned INTEGER DEFAULT 0,
                        expressions_learned INTEGER DEFAULT 0,
                        source_type TEXT,
                        duration_seconds REAL,
                        status TEXT DEFAULT 'completed',
                        error_message TEXT
                    )
                """)
                conn.commit()
                logger.info("Base de datos de aprendizaje continuo inicializada")
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
    
    def start_continuous_learning(self):
        """Iniciar el aprendizaje continuo en segundo plano"""
        if self.is_running:
            logger.warning("El aprendizaje continuo ya está ejecutándose")
            return
        
        self.is_running = True
        logger.info("🚀 Iniciando sistema de aprendizaje continuo...")
        
        # Ejecutar en un hilo separado
        self.learning_thread = threading.Thread(
            target=self._continuous_learning_loop,
            daemon=True
        )
        self.learning_thread.start()
        
        logger.info(f"✅ Aprendizaje continuo iniciado (intervalo: {self.config.training_interval_minutes} minutos)")
    
    def stop_continuous_learning(self):
        """Detener el aprendizaje continuo"""
        self.is_running = False
        logger.info("🛑 Deteniendo sistema de aprendizaje continuo...")
    
    def _continuous_learning_loop(self):
        """Bucle principal del aprendizaje continuo"""
        while self.is_running:
            try:
                # Ejecutar sesión de entrenamiento
                self._run_training_session()
                
                # Esperar hasta la próxima sesión
                logger.info(f"⏰ Esperando {self.config.training_interval_minutes} minutos hasta la próxima sesión...")
                time.sleep(self.config.training_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error en bucle de aprendizaje continuo: {e}")
                self.training_stats['errors'] += 1
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def _run_training_session(self):
        """Ejecutar una sesión de entrenamiento"""
        session_start = datetime.now()
        session_id = None
        
        try:
            logger.info("🎯 Iniciando sesión de entrenamiento automático...")
            
            # Registrar inicio de sesión
            session_id = self._log_session_start(session_start)
            
            # Ejecutar diferentes fuentes de aprendizaje
            total_words = 0
            total_expressions = 0
            
            # 1. Aprendizaje de archivos de texto
            if self.config.enable_text_files:
                words, expressions = self._learn_from_text_files()
                total_words += words
                total_expressions += expressions
            
            # 2. Aprendizaje de APIs
            if self.config.enable_api_learning:
                words, expressions = self._learn_from_apis()
                total_words += words
                total_expressions += expressions
            
            # 3. Aprendizaje de datos sintéticos
            if self.config.enable_synthetic_data:
                words, expressions = self._learn_from_synthetic_data()
                total_words += words
                total_expressions += expressions
            
            # 4. Aprendizaje de corpus español
            if self.config.enable_spanish_corpus:
                words, expressions = self._learn_from_spanish_corpus()
                total_words += words
                total_expressions += expressions
            
            # Actualizar estadísticas
            self.training_stats['total_sessions'] += 1
            self.training_stats['total_words_learned'] += total_words
            self.training_stats['total_expressions_learned'] += total_expressions
            self.training_stats['last_session_time'] = datetime.now()
            self.last_training = datetime.now()
            
            # Registrar fin de sesión
            session_duration = (datetime.now() - session_start).total_seconds()
            self._log_session_end(session_id, total_words, total_expressions, session_duration)
            
            logger.info(f"✅ Sesión completada: {total_words} palabras, {total_expressions} expresiones")
            
        except Exception as e:
            logger.error(f"❌ Error en sesión de entrenamiento: {e}")
            if session_id:
                self._log_session_error(session_id, str(e))
            self.training_stats['errors'] += 1
    
    def _learn_from_text_files(self) -> tuple:
        """Aprender de archivos de texto locales"""
        words_learned = 0
        expressions_learned = 0
        
        try:
            # Archivos de vocabulario local
            text_files = [
                "learning_data/spanish_vocabulary.txt",
                "learning_data/spanish_expressions.txt",
                "learning_data/business_terms.txt",
                "learning_data/customer_service.txt"
            ]
            
            for file_path in text_files:
                try:
                    result = self.auto_learner.learn_from_text_file(file_path)
                    words_learned += result.get('words', 0)
                    expressions_learned += result.get('expressions', 0)
                    logger.info(f"📄 Aprendido de {file_path}: {result.get('words', 0)} palabras")
                except FileNotFoundError:
                    logger.debug(f"Archivo no encontrado: {file_path}")
                except Exception as e:
                    logger.warning(f"Error leyendo {file_path}: {e}")
            
        except Exception as e:
            logger.error(f"Error en aprendizaje de archivos: {e}")
        
        return words_learned, expressions_learned
    
    def _learn_from_apis(self) -> tuple:
        """Aprender de APIs públicas"""
        words_learned = 0
        expressions_learned = 0
        
        try:
            # APIs para obtener datos
            api_sources = [
                "https://jsonplaceholder.typicode.com/posts",
                "https://jsonplaceholder.typicode.com/comments",
                "https://api.github.com/repos/octocat/Hello-World/contents",
                "https://httpbin.org/json"
            ]
            
            for api_url in api_sources:
                try:
                    response = requests.get(api_url, timeout=self.config.api_timeout_seconds)
                    if response.status_code == 200:
                        result = self.auto_learner.learn_from_api_data(response.text)
                        words_learned += result.get('words', 0)
                        expressions_learned += result.get('expressions', 0)
                        logger.info(f"🌐 Aprendido de API {api_url}: {result.get('words', 0)} palabras")
                except Exception as e:
                    logger.warning(f"Error con API {api_url}: {e}")
            
        except Exception as e:
            logger.error(f"Error en aprendizaje de APIs: {e}")
        
        return words_learned, expressions_learned
    
    def _learn_from_synthetic_data(self) -> tuple:
        """Aprender de datos sintéticos generados"""
        words_learned = 0
        expressions_learned = 0
        
        try:
            # Generar datos sintéticos
            synthetic_data = self._generate_synthetic_data()
            result = self.auto_learner.learn_from_synthetic_data(synthetic_data)
            words_learned += result.get('words', 0)
            expressions_learned += result.get('expressions', 0)
            logger.info(f"🤖 Aprendido de datos sintéticos: {result.get('words', 0)} palabras")
            
        except Exception as e:
            logger.error(f"Error en aprendizaje sintético: {e}")
        
        return words_learned, expressions_learned
    
    def _learn_from_spanish_corpus(self) -> tuple:
        """Aprender de corpus español en línea"""
        words_learned = 0
        expressions_learned = 0
        
        try:
            for corpus_url in self.config.spanish_corpus_urls:
                try:
                    response = requests.get(corpus_url, timeout=self.config.api_timeout_seconds)
                    if response.status_code == 200:
                        result = self.auto_learner.learn_from_spanish_corpus(response.text)
                        words_learned += result.get('words', 0)
                        expressions_learned += result.get('expressions', 0)
                        logger.info(f"📚 Aprendido de corpus {corpus_url}: {result.get('words', 0)} palabras")
                except Exception as e:
                    logger.warning(f"Error con corpus {corpus_url}: {e}")
            
        except Exception as e:
            logger.error(f"Error en aprendizaje de corpus: {e}")
        
        return words_learned, expressions_learned
    
    def _generate_synthetic_data(self) -> List[str]:
        """Generar datos sintéticos para entrenamiento"""
        synthetic_messages = [
            # Saludos y conversación
            "Hola, ¿cómo estás hoy?",
            "Buenos días, espero que tengas un excelente día",
            "¿Qué tal va todo?",
            "Me alegra verte por aquí",
            
            # Negocios y atención al cliente
            "Necesito información sobre nuestros servicios",
            "¿Cuál es el precio de este producto?",
            "Quisiera hacer una consulta sobre mi cuenta",
            "¿Pueden ayudarme con un problema técnico?",
            
            # Citas y programación
            "Me gustaría agendar una cita para mañana",
            "¿Tienen disponibilidad el viernes?",
            "Necesito cambiar mi cita programada",
            "¿A qué hora es mi próxima reunión?",
            
            # Ventas y productos
            "¿Tienen este producto en stock?",
            "¿Cuál es la garantía de este artículo?",
            "Me interesa comprar varios productos",
            "¿Ofrecen descuentos para clientes frecuentes?",
            
            # Soporte técnico
            "Tengo un problema con mi cuenta",
            "¿Cómo puedo restablecer mi contraseña?",
            "La aplicación no funciona correctamente",
            "Necesito ayuda con la configuración",
            
            # Expresiones comunes
            "Muchas gracias por tu ayuda",
            "Te agradezco mucho la información",
            "Ha sido un placer hablar contigo",
            "Espero verte pronto",
            
            # Preguntas frecuentes
            "¿Cuáles son los horarios de atención?",
            "¿Aceptan pagos con tarjeta?",
            "¿Tienen envío a domicilio?",
            "¿Cuál es la política de devoluciones?"
        ]
        
        return synthetic_messages
    
    def _log_session_start(self, start_time: datetime) -> int:
        """Registrar inicio de sesión"""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO continuous_learning_log 
                    (session_start, status) VALUES (?, 'running')
                """, (start_time,))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error registrando inicio de sesión: {e}")
            return None
    
    def _log_session_end(self, session_id: int, words: int, expressions: int, duration: float):
        """Registrar fin de sesión"""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                conn.execute("""
                    UPDATE continuous_learning_log 
                    SET session_end = CURRENT_TIMESTAMP,
                        words_learned = ?,
                        expressions_learned = ?,
                        duration_seconds = ?,
                        status = 'completed'
                    WHERE id = ?
                """, (words, expressions, duration, session_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error registrando fin de sesión: {e}")
    
    def _log_session_error(self, session_id: int, error_message: str):
        """Registrar error de sesión"""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                conn.execute("""
                    UPDATE continuous_learning_log 
                    SET session_end = CURRENT_TIMESTAMP,
                        status = 'error',
                        error_message = ?
                    WHERE id = ?
                """, (error_message, session_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error registrando error de sesión: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Obtener estadísticas del aprendizaje continuo"""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(words_learned) as total_words,
                        SUM(expressions_learned) as total_expressions,
                        AVG(duration_seconds) as avg_duration,
                        COUNT(CASE WHEN status = 'error' THEN 1 END) as error_sessions
                    FROM continuous_learning_log
                    WHERE session_end IS NOT NULL
                """)
                row = cursor.fetchone()
                
                return {
                    'total_sessions': row[0] or 0,
                    'total_words_learned': row[1] or 0,
                    'total_expressions_learned': row[2] or 0,
                    'avg_duration_seconds': row[3] or 0,
                    'error_sessions': row[4] or 0,
                    'is_running': self.is_running,
                    'last_training': self.last_training.isoformat() if self.last_training else None,
                    'next_training_in_minutes': self._get_next_training_time()
                }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def _get_next_training_time(self) -> Optional[int]:
        """Calcular minutos hasta la próxima sesión"""
        if not self.last_training:
            return 0
        
        next_training = self.last_training + timedelta(minutes=self.config.training_interval_minutes)
        minutes_until_next = (next_training - datetime.now()).total_seconds() / 60
        
        return max(0, int(minutes_until_next))

# Instancia global del sistema
continuous_learner = ContinuousLearningSystem() 