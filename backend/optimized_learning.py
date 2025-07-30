"""
Sistema de Aprendizaje Optimizado para Chatbot Inteligente
Permite que el chatbot aprenda nuevas palabras y expresiones de forma eficiente
"""

import json
import sqlite3
import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from functools import lru_cache
import hashlib
from datetime import datetime, timedelta
import logging

# Configurar logging optimizado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LearningConfig:
    """Configuración optimizada del sistema de aprendizaje"""
    # Configuración de vocabulario
    max_vocabulary_size: int = 0  # 0 = Sin límite (ilimitado)
    min_word_length: int = 3
    learning_threshold: int = 2  # Mínimo de apariciones para aprender
    
    # Configuración de cache
    cache_size: int = 500  # Aumentado de 100 a 500
    similarity_cache_size: int = 200
    
    # Configuración de base de datos
    db_path: str = "optimized_learning.db"
    backup_interval: int = 3600  # 1 hora
    
    # Configuración de limpieza
    cleanup_frequency: int = 100  # Limpiar cada 100 palabras nuevas
    min_frequency_keep: int = 3   # Mantener palabras con al menos 3 usos
    
    # Configuración de categorías
    business_keywords: List[str] = field(default_factory=lambda: [
        "consulta", "cita", "pedido", "factura", "pago", "servicio",
        "producto", "precio", "descuento", "garantía", "devolución",
        "cliente", "atención", "soporte", "problema", "solución",
        "urgente", "importante", "especial", "personalizado"
    ])
    
    # Configuración de expresiones
    max_expression_length: int = 50
    min_expression_words: int = 2

class OptimizedVocabularyLearner:
    """
    Sistema de aprendizaje de vocabulario optimizado para bajo consumo de recursos
    """
    
    def __init__(self, config: LearningConfig = None):
        self.config = config or LearningConfig()
        self.db_path = self.config.db_path
        self.vocabulary_cache = {}
        self.context_cache = {}
        self.similarity_cache = {}
        self.last_backup = datetime.now()
        
        # Inicializar base de datos
        self._init_database()
        self._load_vocabulary_cache()
    
    def _init_database(self):
        """Inicializar base de datos optimizada"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS vocabulary (
                        word TEXT PRIMARY KEY,
                        frequency INTEGER DEFAULT 1,
                        contexts TEXT,
                        learned_date TEXT,
                        last_used TEXT,
                        category TEXT DEFAULT 'general'
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS expressions (
                        expression TEXT PRIMARY KEY,
                        frequency INTEGER DEFAULT 1,
                        contexts TEXT,
                        learned_date TEXT,
                        last_used TEXT,
                        category TEXT DEFAULT 'general'
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS learning_stats (
                        date TEXT PRIMARY KEY,
                        new_words INTEGER DEFAULT 0,
                        new_expressions INTEGER DEFAULT 0,
                        total_learned INTEGER DEFAULT 0
                    )
                """)
                
                # Crear índices para optimizar consultas
                conn.execute("CREATE INDEX IF NOT EXISTS idx_vocabulary_frequency ON vocabulary(frequency)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_vocabulary_category ON vocabulary(category)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_expressions_frequency ON expressions(frequency)")
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
    
    def _load_vocabulary_cache(self):
        """Cargar vocabulario en cache de forma optimizada"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Cargar solo las palabras más frecuentes para optimizar memoria
                cursor = conn.execute("""
                    SELECT word, frequency, contexts, category 
                    FROM vocabulary 
                    ORDER BY frequency DESC 
                    LIMIT 1000
                """)
                
                for row in cursor:
                    word, frequency, contexts, category = row
                    self.vocabulary_cache[word] = {
                        'frequency': frequency,
                        'contexts': json.loads(contexts) if contexts else [],
                        'category': category
                    }
                    
        except Exception as e:
            logger.error(f"Error cargando vocabulario: {e}")
    
    @lru_cache(maxsize=200)
    def normalize_word(self, word: str) -> str:
        """Normalizar palabra de forma optimizada"""
        if not word:
            return ""
        
        # Limpiar y normalizar
        normalized = re.sub(r'[^\w\s]', '', word.lower().strip())
        
        # Validar longitud
        if len(normalized) < self.config.min_word_length or len(normalized) > self.config.max_word_length:
            return ""
        
        return normalized
    
    def extract_words(self, text: str) -> List[str]:
        """Extraer palabras del texto de forma optimizada"""
        if not text:
            return []
        
        # Usar regex optimizado para extraer palabras
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtrar y normalizar
        normalized_words = []
        for word in words:
            normalized = self.normalize_word(word)
            if normalized:
                normalized_words.append(normalized)
        
        return normalized_words
    
    def extract_expressions(self, text: str) -> List[str]:
        """Extraer expresiones comunes del texto"""
        if not text:
            return []
        
        # Expresiones comunes a buscar
        common_expressions = [
            r'\b(hola|buenos días|buenas tardes|buenas noches)\b',
            r'\b(gracias|por favor|disculpa|perdón)\b',
            r'\b(qué tal|cómo estás|cómo va)\b',
            r'\b(me gustaría|quisiera|necesito)\b',
            r'\b(por supuesto|claro|excelente)\b',
            r'\b(no entiendo|no sé|ayuda)\b'
        ]
        
        expressions = []
        for pattern in common_expressions:
            matches = re.findall(pattern, text.lower())
            expressions.extend(matches)
        
        return expressions
    
    def learn_from_text(self, text: str, context: str = "general") -> Dict[str, int]:
        """Aprender nuevas palabras y expresiones del texto"""
        if not text:
            return {"words": 0, "expressions": 0}
        
        # Extraer palabras y expresiones
        words = self.extract_words(text)
        expressions = self.extract_expressions(text)
        
        learned_words = 0
        learned_expressions = 0
        
        # Aprender palabras
        for word in words:
            if self._learn_word(word, context):
                learned_words += 1
        
        # Aprender expresiones
        for expression in expressions:
            if self._learn_expression(expression, context):
                learned_expressions += 1
        
        # Actualizar estadísticas
        self._update_learning_stats(learned_words, learned_expressions)
        
        # Backup periódico
        self._check_backup()
        
        return {
            "words": learned_words,
            "expressions": learned_expressions,
            "total_vocabulary": len(self.vocabulary_cache)
        }
    
    def _learn_word(self, word: str, context: str) -> bool:
        """Aprender una nueva palabra con categorización inteligente"""
        if not word or len(word) < self.config.min_word_length:
            return False
            
        # Determinar categoría de la palabra
        category = self._categorize_word(word)
        
        # Verificar si ya está en cache
        if word in self.vocabulary_cache:
            # Actualizar frecuencia en cache
            self.vocabulary_cache[word]['frequency'] += 1
            self.vocabulary_cache[word]['last_used'] = datetime.now().isoformat()
            return True
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT frequency, contexts, category FROM vocabulary WHERE word = ?", (word,))
                row = cursor.fetchone()
                
                if row:
                    frequency, contexts, existing_category = row
                    contexts_list = json.loads(contexts) if contexts else []
                    contexts_list.append(context)
                    contexts_list = contexts_list[-10:]  # Mantener solo los últimos 10 contextos
                    
                    # Actualizar en base de datos
                    conn.execute("""
                        UPDATE vocabulary
                        SET frequency = ?, contexts = ?, last_used = ?, category = ?
                        WHERE word = ?
                    """, (frequency + 1, json.dumps(contexts_list), datetime.now().isoformat(), category, word))
                    
                    # Actualizar cache
                    self.vocabulary_cache[word] = {
                        'frequency': frequency + 1,
                        'contexts': contexts_list,
                        'category': category,
                        'last_used': datetime.now().isoformat()
                    }
                else:
                    # Insertar nueva palabra (sin límite)
                    # Solo limpiar si hay demasiadas palabras en cache para optimizar memoria
                    if len(self.vocabulary_cache) >= 10000:  # Límite de cache para memoria
                        self._cleanup_old_words()
                    
                    # Insertar nueva palabra
                    conn.execute("""
                        INSERT INTO vocabulary (word, frequency, contexts, learned_date, last_used, category)
                        VALUES (?, 1, ?, ?, ?, ?)
                    """, (word, json.dumps([context]), datetime.now().isoformat(),
                          datetime.now().isoformat(), category))
                    
                    # Agregar al cache
                    self.vocabulary_cache[word] = {
                        'frequency': 1,
                        'contexts': [context],
                        'category': category,
                        'learned_date': datetime.now().isoformat(),
                        'last_used': datetime.now().isoformat()
                    }
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error aprendiendo palabra '{word}': {e}")
            return False
    
    def _categorize_word(self, word: str) -> str:
        """Categorizar palabra según su relevancia"""
        word_lower = word.lower()
        
        # Palabras de negocio (alta prioridad)
        if word_lower in self.config.business_keywords:
            return 'business'
        
        # Palabras comunes de servicio al cliente
        service_words = ['ayuda', 'problema', 'solución', 'soporte', 'atención', 'cliente']
        if word_lower in service_words:
            return 'customer_service'
        
        # Palabras de tiempo
        time_words = ['hoy', 'mañana', 'ayer', 'semana', 'mes', 'año', 'hora', 'minuto']
        if word_lower in time_words:
            return 'time'
        
        # Palabras de emoción/sentimiento
        emotion_words = ['gracias', 'por favor', 'excelente', 'malo', 'bueno', 'mejor', 'peor']
        if word_lower in emotion_words:
            return 'emotion'
        
        # Palabras técnicas (si contienen caracteres especiales o son largas)
        if len(word) > 8 or any(c.isdigit() for c in word):
            return 'technical'
        
        return 'general'
    
    def _learn_expression(self, expression: str, context: str) -> bool:
        """Aprender una nueva expresión"""
        if not expression:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Verificar si ya existe
                cursor = conn.execute("SELECT frequency, contexts FROM expressions WHERE expression = ?", (expression,))
                row = cursor.fetchone()
                
                if row:
                    # Actualizar frecuencia y contexto
                    frequency, contexts = row
                    contexts_list = json.loads(contexts) if contexts else []
                    contexts_list.append(context)
                    contexts_list = contexts_list[-10:]  # Mantener solo los últimos
                    
                    conn.execute("""
                        UPDATE expressions 
                        SET frequency = ?, contexts = ?, last_used = ? 
                        WHERE expression = ?
                    """, (frequency + 1, json.dumps(contexts_list), datetime.now().isoformat(), expression))
                else:
                    # Nueva expresión
                    conn.execute("""
                        INSERT INTO expressions (expression, frequency, contexts, learned_date, last_used, category)
                        VALUES (?, 1, ?, ?, ?, ?)
                    """, (expression, json.dumps([context]), datetime.now().isoformat(), 
                          datetime.now().isoformat(), context))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error aprendiendo expresión '{expression}': {e}")
            return False
    
    def _update_learning_stats(self, new_words: int, new_expressions: int):
        """Actualizar estadísticas de aprendizaje"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT new_words, new_expressions, total_learned FROM learning_stats WHERE date = ?", (today,))
                row = cursor.fetchone()
                
                if row:
                    # Actualizar estadísticas existentes
                    current_words, current_expressions, total_learned = row
                    conn.execute("""
                        UPDATE learning_stats 
                        SET new_words = ?, new_expressions = ?, total_learned = ?
                        WHERE date = ?
                    """, (current_words + new_words, current_expressions + new_expressions, 
                          total_learned + new_words + new_expressions, today))
                else:
                    # Crear nueva entrada
                    conn.execute("""
                        INSERT INTO learning_stats (date, new_words, new_expressions, total_learned)
                        VALUES (?, ?, ?, ?)
                    """, (today, new_words, new_expressions, new_words + new_expressions))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
    
    def _check_backup(self):
        """Verificar si es necesario hacer backup"""
        if datetime.now() - self.last_backup > timedelta(seconds=self.config.backup_interval):
            self._backup_vocabulary()
            self.last_backup = datetime.now()
    
    def _backup_vocabulary(self):
        """Backup del vocabulario aprendido"""
        try:
            backup_path = f"{self.db_path}.backup"
            with sqlite3.connect(self.db_path) as source_conn:
                with sqlite3.connect(backup_path) as backup_conn:
                    source_conn.backup(backup_conn)
            logger.info("Backup del vocabulario completado")
        except Exception as e:
            logger.error(f"Error en backup: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Obtener estadísticas de aprendizaje"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estadísticas generales
                total_words = conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0]
                total_expressions = conn.execute("SELECT COUNT(*) FROM expressions").fetchone()[0]
                
                # Estadísticas de hoy
                today = datetime.now().strftime('%Y-%m-%d')
                today_stats = conn.execute("""
                    SELECT new_words, new_expressions, total_learned 
                    FROM learning_stats 
                    WHERE date = ?
                """, (today,)).fetchone()
                
                # Palabras más frecuentes
                top_words = conn.execute("""
                    SELECT word, frequency 
                    FROM vocabulary 
                    ORDER BY frequency DESC 
                    LIMIT 10
                """).fetchall()
                
                # Expresiones más frecuentes
                top_expressions = conn.execute("""
                    SELECT expression, frequency 
                    FROM expressions 
                    ORDER BY frequency DESC 
                    LIMIT 10
                """).fetchall()
                
                return {
                    "total_words": total_words,
                    "total_expressions": total_expressions,
                    "today_words": today_stats[0] if today_stats else 0,
                    "today_expressions": today_stats[1] if today_stats else 0,
                    "total_learned_today": today_stats[2] if today_stats else 0,
                    "top_words": [{"word": w, "frequency": f} for w, f in top_words],
                    "top_expressions": [{"expression": e, "frequency": f} for e, f in top_expressions],
                    "cache_size": len(self.vocabulary_cache)
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def search_similar_words(self, word: str, limit: int = 5) -> List[str]:
        """Buscar palabras similares de forma optimizada"""
        if not word or len(word) < 3:
            return []
        
        similar_words = []
        word_lower = word.lower()
        
        # Búsqueda simple por similitud de caracteres
        for vocab_word in self.vocabulary_cache.keys():
            if vocab_word != word_lower:
                # Calcular similitud simple
                similarity = self._calculate_similarity(word_lower, vocab_word)
                if similarity > 0.6:  # Umbral de similitud
                    similar_words.append(vocab_word)
        
        # Ordenar por frecuencia y similitud
        similar_words.sort(key=lambda w: (
            self.vocabulary_cache.get(w, {}).get('frequency', 0),
            self._calculate_similarity(word_lower, w)
        ), reverse=True)
        
        return similar_words[:limit]
    
    @lru_cache(maxsize=100)
    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """Calcular similitud entre palabras de forma optimizada"""
        if not word1 or not word2:
            return 0.0
        
        # Similitud simple basada en caracteres comunes
        common_chars = set(word1) & set(word2)
        total_chars = set(word1) | set(word2)
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)
    
    def get_vocabulary_summary(self) -> Dict:
        """Obtener resumen del vocabulario aprendido"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                total_words_db = conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0]
                total_expressions_db = conn.execute("SELECT COUNT(*) FROM expressions").fetchone()[0]
                
                return {
                    "total_words": total_words_db,  # Total en base de datos
                    "cache_size": len(self.vocabulary_cache),  # Palabras en cache
                    "total_expressions": total_expressions_db,
                    "config": {
                        "max_vocabulary_size": "ilimitado" if self.config.max_vocabulary_size == 0 else self.config.max_vocabulary_size,
                        "cache_size": self.config.cache_size,
                        "min_word_length": self.config.min_word_length,
                        "learning_threshold": self.config.learning_threshold
                    }
                }
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {
                "total_words": len(self.vocabulary_cache),
                "cache_size": len(self.vocabulary_cache),
                "config": {
                    "max_vocabulary_size": "ilimitado" if self.config.max_vocabulary_size == 0 else self.config.max_vocabulary_size,
                    "cache_size": self.config.cache_size,
                    "min_word_length": self.config.min_word_length
                }
            }
    
    def _cleanup_old_words(self):
        """Limpieza inteligente de palabras antiguas y poco relevantes (solo para optimizar memoria)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Obtener estadísticas actuales
                cursor = conn.execute("SELECT COUNT(*) FROM vocabulary")
                total_words = cursor.fetchone()[0]
                
                # Solo limpiar si hay demasiadas palabras en cache para optimizar memoria
                # NO eliminar palabras de la base de datos, solo del cache
                if len(self.vocabulary_cache) > 8000:  # Reducir cache si es muy grande
                    # Mantener solo las palabras más frecuentes en cache
                    top_words = conn.execute("""
                        SELECT word, frequency, contexts, category 
                        FROM vocabulary 
                        ORDER BY frequency DESC 
                        LIMIT 5000
                    """).fetchall()
                    
                    # Limpiar cache y recargar solo las más frecuentes
                    self.vocabulary_cache.clear()
                    for word, frequency, contexts, category in top_words:
                        self.vocabulary_cache[word] = {
                            'frequency': frequency,
                            'contexts': json.loads(contexts) if contexts else [],
                            'category': category
                        }
                    
                    logger.info(f"Cache optimizado. Palabras en cache: {len(self.vocabulary_cache)}")
                
        except Exception as e:
            logger.error(f"Error en limpieza de cache: {e}")
    
    def cleanup_old_words(self, days: int = 30):
        """Limpiar palabras antiguas y poco usadas (método manual)"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Eliminar palabras antiguas y poco usadas
                conn.execute("""
                    DELETE FROM vocabulary 
                    WHERE last_used < ? AND frequency < ?
                """, (cutoff_date, self.config.min_frequency_keep))
                
                # Eliminar expresiones antiguas
                conn.execute("""
                    DELETE FROM expressions 
                    WHERE last_used < ? AND frequency < ?
                """, (cutoff_date, self.config.min_frequency_keep))
                
                conn.commit()
                
                # Limpiar cache
                self._load_vocabulary_cache()
                
        except Exception as e:
            logger.error(f"Error limpiando palabras antiguas: {e}")

# Instancia global optimizada
vocabulary_learner = OptimizedVocabularyLearner() 