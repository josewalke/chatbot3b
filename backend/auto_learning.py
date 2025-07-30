"""
Sistema de Aprendizaje Automático para el Chatbot
Permite que el chatbot aprenda vocabulario automáticamente sin interacción manual
"""

import asyncio
import json
import logging
import random
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AutoLearningConfig:
    """Configuración del aprendizaje automático"""
    # Fuentes de aprendizaje
    enable_text_files: bool = True
    enable_api_learning: bool = True
    enable_synthetic_data: bool = True
    enable_spanish_corpus: bool = True
    
    # Configuración de archivos
    text_files_path: str = "learning_data/"
    vocabulary_file: str = "spanish_vocabulary.txt"
    expressions_file: str = "spanish_expressions.txt"
    
    # Configuración de API
    api_endpoints: List[str] = field(default_factory=lambda: [
        "https://api.github.com/search/repositories?q=language:python",
        "https://jsonplaceholder.typicode.com/posts",
        "https://api.publicapis.org/entries"
    ])
    
    # Configuración de datos sintéticos
    synthetic_messages: List[str] = field(default_factory=lambda: [
        "Hola, ¿cómo estás?",
        "Necesito ayuda con mi pedido",
        "¿Puedes ayudarme con una consulta?",
        "Quisiera agendar una cita",
        "Tengo un problema con mi factura",
        "¿Cuál es el precio del servicio?",
        "Necesito información sobre garantías",
        "¿Pueden hacer un descuento?",
        "Quiero devolver un producto",
        "Necesito soporte técnico",
        "El sistema está funcionando correctamente",
        "Hay un error en la aplicación",
        "La página web no carga",
        "Necesito actualizar mi información",
        "¿Cuándo llega mi pedido?",
        "El servicio es excelente",
        "Tengo una queja sobre el producto",
        "¿Pueden mejorar el servicio?",
        "Necesito hablar con un supervisor",
        "El chatbot es muy útil"
    ])
    
    # Configuración de corpus español
    spanish_corpus_urls: List[str] = field(default_factory=lambda: [
        "https://raw.githubusercontent.com/JorgeDuenasLerin/diccionario-espanol-txt/master/0_palabras_todas.txt",
        "https://raw.githubusercontent.com/JorgeDuenasLerin/diccionario-espanol-txt/master/0_palabras_todas_no_conjugaciones.txt",
        "https://raw.githubusercontent.com/david-levy/spanish-words/master/words.txt",
        "https://raw.githubusercontent.com/words/an-array-of-spanish-words/master/words.json"
    ])
    
    # Configuración de aprendizaje
    learning_interval: int = 3600  # 1 hora
    max_words_per_session: int = 1000
    enable_background_learning: bool = True

class AutoVocabularyLearner:
    """Sistema de aprendizaje automático de vocabulario"""
    
    def __init__(self, db_path: str = "optimized_learning.db", config: Optional[AutoLearningConfig] = None):
        self.db_path = db_path
        self.config = config or AutoLearningConfig()
        self._init_database()
        self._create_learning_data_dir()
    
    def _init_database(self):
        """Inicializar base de datos para aprendizaje automático"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Tabla para tracking de aprendizaje automático
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS auto_learning_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT NOT NULL,
                        words_learned INTEGER DEFAULT 0,
                        expressions_learned INTEGER DEFAULT 0,
                        learning_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'success'
                    )
                """)
                
                # Índices para optimización
                conn.execute("CREATE INDEX IF NOT EXISTS idx_auto_learning_date ON auto_learning_log(learning_date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_auto_learning_source ON auto_learning_log(source)")
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
    
    def _create_learning_data_dir(self):
        """Crear directorio para datos de aprendizaje"""
        try:
            Path(self.config.text_files_path).mkdir(exist_ok=True)
        except Exception as e:
            logger.error(f"Error creando directorio de datos: {e}")
    
    async def learn_from_text_files(self) -> Dict:
        """Aprender desde archivos de texto"""
        if not self.config.enable_text_files:
            return {"status": "disabled", "words_learned": 0}
        
        try:
            words_learned = 0
            expressions_learned = 0
            
            # Aprender desde archivo de vocabulario
            vocab_file = Path(self.config.text_files_path) / self.config.vocabulary_file
            if vocab_file.exists():
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    words = f.read().splitlines()
                    for word in words[:self.config.max_words_per_session]:
                        if self._learn_word(word, "text_file"):
                            words_learned += 1
            
            # Aprender desde archivo de expresiones
            expr_file = Path(self.config.text_files_path) / self.config.expressions_file
            if expr_file.exists():
                with open(expr_file, 'r', encoding='utf-8') as f:
                    expressions = f.read().splitlines()
                    for expr in expressions[:self.config.max_words_per_session//2]:
                        if self._learn_expression(expr, "text_file"):
                            expressions_learned += 1
            
            self._log_learning_session("text_files", words_learned, expressions_learned)
            return {
                "status": "success",
                "words_learned": words_learned,
                "expressions_learned": expressions_learned
            }
            
        except Exception as e:
            logger.error(f"Error aprendiendo desde archivos: {e}")
            return {"status": "error", "error": str(e)}
    
    async def learn_from_api_data(self) -> Dict:
        """Aprender desde datos de APIs"""
        if not self.config.enable_api_learning:
            return {"status": "disabled", "words_learned": 0}
        
        try:
            words_learned = 0
            
            for endpoint in self.config.api_endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        words = self._extract_words_from_json(data)
                        for word in words[:100]:  # Límite por API
                            if self._learn_word(word, "api_data"):
                                words_learned += 1
                except Exception as e:
                    logger.warning(f"Error con API {endpoint}: {e}")
                    continue
            
            self._log_learning_session("api_data", words_learned, 0)
            return {"status": "success", "words_learned": words_learned}
            
        except Exception as e:
            logger.error(f"Error aprendiendo desde APIs: {e}")
            return {"status": "error", "error": str(e)}
    
    async def learn_from_synthetic_data(self) -> Dict:
        """Aprender desde datos sintéticos"""
        if not self.config.enable_synthetic_data:
            return {"status": "disabled", "words_learned": 0}
        
        try:
            words_learned = 0
            expressions_learned = 0
            
            # Mensajes sintéticos predefinidos
            for message in self.config.synthetic_messages:
                words = message.lower().split()
                for word in words:
                    if self._learn_word(word, "synthetic_data"):
                        words_learned += 1
                
                if self._learn_expression(message, "synthetic_data"):
                    expressions_learned += 1
            
            # Generar más mensajes sintéticos
            additional_messages = self._generate_synthetic_messages()
            for message in additional_messages:
                words = message.lower().split()
                for word in words:
                    if self._learn_word(word, "synthetic_data"):
                        words_learned += 1
            
            self._log_learning_session("synthetic_data", words_learned, expressions_learned)
            return {
                "status": "success",
                "words_learned": words_learned,
                "expressions_learned": expressions_learned
            }
            
        except Exception as e:
            logger.error(f"Error aprendiendo desde datos sintéticos: {e}")
            return {"status": "error", "error": str(e)}
    
    async def learn_from_spanish_corpus(self) -> Dict:
        """Aprender desde corpus de español"""
        if not self.config.enable_spanish_corpus:
            return {"status": "disabled", "words_learned": 0}
        
        try:
            words_learned = 0
            
            for url in self.config.spanish_corpus_urls:
                try:
                    response = requests.get(url, timeout=15)
                    if response.status_code == 200:
                        content = response.text
                        words = content.split('\n')
                        for word in words[:500]:  # Límite por corpus
                            if word.strip() and self._learn_word(word.strip(), "spanish_corpus"):
                                words_learned += 1
                except Exception as e:
                    logger.warning(f"Error con corpus {url}: {e}")
                    continue
            
            self._log_learning_session("spanish_corpus", words_learned, 0)
            return {"status": "success", "words_learned": words_learned}
            
        except Exception as e:
            logger.error(f"Error aprendiendo desde corpus español: {e}")
            return {"status": "error", "error": str(e)}
    
    def _learn_word(self, word: str, source: str) -> bool:
        """Aprender una palabra"""
        try:
            word = word.strip().lower()
            if len(word) < 3:
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                # Verificar si ya existe
                existing = conn.execute(
                    "SELECT frequency FROM vocabulary WHERE word = ?", 
                    (word,)
                ).fetchone()
                
                if existing:
                    # Actualizar frecuencia
                    conn.execute(
                        "UPDATE vocabulary SET frequency = frequency + 1, last_used = ? WHERE word = ?",
                        (datetime.now().isoformat(), word)
                    )
                else:
                    # Insertar nueva palabra
                    conn.execute("""
                        INSERT INTO vocabulary (word, frequency, contexts, learned_date, last_used, category, source)
                        VALUES (?, 1, ?, ?, ?, ?, ?)
                    """, (word, json.dumps([source]), datetime.now().isoformat(),
                          datetime.now().isoformat(), self._categorize_word(word), source))
                
                return True
                
        except Exception as e:
            logger.error(f"Error aprendiendo palabra '{word}': {e}")
            return False
    
    def _learn_expression(self, expression: str, source: str) -> bool:
        """Aprender una expresión"""
        try:
            expression = expression.strip()
            if len(expression) < 5:
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                # Verificar si ya existe
                existing = conn.execute(
                    "SELECT frequency FROM expressions WHERE expression = ?", 
                    (expression,)
                ).fetchone()
                
                if existing:
                    # Actualizar frecuencia
                    conn.execute(
                        "UPDATE expressions SET frequency = frequency + 1, last_used = ? WHERE expression = ?",
                        (datetime.now().isoformat(), expression)
                    )
                else:
                    # Insertar nueva expresión
                    conn.execute("""
                        INSERT INTO expressions (expression, frequency, contexts, learned_date, last_used, source)
                        VALUES (?, 1, ?, ?, ?, ?)
                    """, (expression, json.dumps([source]), datetime.now().isoformat(),
                          datetime.now().isoformat(), source))
                
                return True
                
        except Exception as e:
            logger.error(f"Error aprendiendo expresión '{expression}': {e}")
            return False
    
    def _categorize_word(self, word: str) -> str:
        """Categorizar una palabra"""
        business_keywords = [
            "consulta", "cita", "pedido", "factura", "pago", "servicio",
            "producto", "precio", "descuento", "garantía", "devolución",
            "cliente", "atención", "soporte", "problema", "solución",
            "urgente", "importante", "especial", "personalizado"
        ]
        
        if word in business_keywords:
            return "business"
        elif any(keyword in word for keyword in ["ayuda", "soporte", "atención"]):
            return "customer_service"
        elif any(keyword in word for keyword in ["hora", "día", "semana", "mes"]):
            return "time"
        elif any(keyword in word for keyword in ["gracias", "por favor", "disculpa"]):
            return "emotion"
        elif any(keyword in word for keyword in ["sistema", "error", "problema", "funcionar"]):
            return "technical"
        else:
            return "general"
    
    def _extract_words_from_json(self, data) -> List[str]:
        """Extraer palabras de datos JSON"""
        words = []
        
        def extract_from_obj(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    words.extend(str(key).lower().split())
                    extract_from_obj(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_from_obj(item)
            elif isinstance(obj, str):
                words.extend(obj.lower().split())
        
        extract_from_obj(data)
        return list(set(words))  # Eliminar duplicados
    
    def _generate_synthetic_messages(self) -> List[str]:
        """Generar mensajes sintéticos adicionales"""
        templates = [
            "Necesito {action} con mi {item}",
            "¿Puedes ayudarme con {problem}?",
            "Quisiera {action} para {purpose}",
            "Tengo un {issue} con {item}",
            "¿Cuál es el {attribute} del {item}?",
            "Necesito {service} para {purpose}",
            "El {system} no está {status}",
            "¿Pueden {action} mi {item}?",
            "Tengo una {type} sobre {topic}",
            "Necesito {help} con {problem}"
        ]
        
        actions = ["ayuda", "soporte", "información", "asistencia", "consulta"]
        items = ["pedido", "factura", "producto", "servicio", "cuenta", "sistema"]
        problems = ["problema", "error", "duda", "consulta", "situación"]
        purposes = ["mañana", "hoy", "urgente", "importante", "especial"]
        attributes = ["precio", "estado", "fecha", "garantía", "disponibilidad"]
        systems = ["sistema", "aplicación", "página", "servicio", "plataforma"]
        statuses = ["funcionando", "disponible", "accesible", "operativo"]
        types = ["queja", "sugerencia", "consulta", "solicitud", "reclamo"]
        topics = ["servicio", "producto", "atención", "facturación", "soporte"]
        
        messages = []
        for template in templates:
            try:
                message = template.format(
                    action=random.choice(actions),
                    item=random.choice(items),
                    problem=random.choice(problems),
                    purpose=random.choice(purposes),
                    attribute=random.choice(attributes),
                    service=random.choice(actions),
                    system=random.choice(systems),
                    status=random.choice(statuses),
                    help=random.choice(actions),
                    type=random.choice(types),
                    topic=random.choice(topics)
                )
                messages.append(message)
            except:
                continue
        
        return messages
    
    def _log_learning_session(self, source: str, words_learned: int, expressions_learned: int):
        """Registrar sesión de aprendizaje"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO auto_learning_log (source, words_learned, expressions_learned, learning_date)
                    VALUES (?, ?, ?, ?)
                """, (source, words_learned, expressions_learned, datetime.now().isoformat()))
        except Exception as e:
            logger.error(f"Error registrando sesión de aprendizaje: {e}")
    
    async def run_full_learning_session(self) -> Dict:
        """Ejecutar sesión completa de aprendizaje automático"""
        logger.info("Iniciando sesión de aprendizaje automático...")
        
        results = {
            "total_words_learned": 0,
            "total_expressions_learned": 0,
            "sources": {}
        }
        
        # Aprender desde todas las fuentes
        sources = [
            ("text_files", self.learn_from_text_files()),
            ("api_data", self.learn_from_api_data()),
            ("synthetic_data", self.learn_from_synthetic_data()),
            ("spanish_corpus", self.learn_from_spanish_corpus())
        ]
        
        for source_name, coro in sources:
            try:
                result = await coro
                results["sources"][source_name] = result
                results["total_words_learned"] += result.get("words_learned", 0)
                results["total_expressions_learned"] += result.get("expressions_learned", 0)
            except Exception as e:
                logger.error(f"Error en fuente {source_name}: {e}")
                results["sources"][source_name] = {"status": "error", "error": str(e)}
        
        logger.info(f"Sesión de aprendizaje completada. Palabras aprendidas: {results['total_words_learned']}")
        return results
    
    def get_learning_stats(self) -> Dict:
        """Obtener estadísticas de aprendizaje automático"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estadísticas generales
                total_sessions = conn.execute("SELECT COUNT(*) FROM auto_learning_log").fetchone()[0]
                total_words = conn.execute("SELECT SUM(words_learned) FROM auto_learning_log").fetchone()[0] or 0
                total_expressions = conn.execute("SELECT SUM(expressions_learned) FROM auto_learning_log").fetchone()[0] or 0
                
                # Última sesión
                last_session = conn.execute("""
                    SELECT source, words_learned, expressions_learned, learning_date 
                    FROM auto_learning_log 
                    ORDER BY learning_date DESC 
                    LIMIT 1
                """).fetchone()
                
                # Estadísticas por fuente
                source_stats = conn.execute("""
                    SELECT source, 
                           COUNT(*) as sessions,
                           SUM(words_learned) as total_words,
                           SUM(expressions_learned) as total_expressions
                    FROM auto_learning_log 
                    GROUP BY source
                """).fetchall()
                
                return {
                    "total_sessions": total_sessions,
                    "total_words_learned": total_words,
                    "total_expressions_learned": total_expressions,
                    "last_session": {
                        "source": last_session[0] if last_session else None,
                        "words_learned": last_session[1] if last_session else 0,
                        "expressions_learned": last_session[2] if last_session else 0,
                        "date": last_session[3] if last_session else None
                    },
                    "sources": {
                        source: {
                            "sessions": sessions,
                            "total_words": total_words,
                            "total_expressions": total_expressions
                        }
                        for source, sessions, total_words, total_expressions in source_stats
                    }
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}

# Instancia global para uso en el servidor
auto_learner = AutoVocabularyLearner() 