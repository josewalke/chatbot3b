"""
Sistema de corrección ortográfica y manejo de variaciones
Para hacer el chatbot más robusto con errores de escritura
"""

import re
import difflib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import sqlite3
import logging

logger = logging.getLogger(__name__)

@dataclass
class SpellCheckConfig:
    """Configuración del corrector ortográfico"""
    # Umbrales de similitud
    min_similarity: float = 0.7
    max_edit_distance: int = 3
    
    # Configuración de variaciones
    enable_fuzzy_matching: bool = True
    enable_soundex: bool = True
    enable_common_errors: bool = True
    
    # Errores comunes en español
    common_errors: Dict[str, str] = None
    
    def __post_init__(self):
        if self.common_errors is None:
            self.common_errors = {
                # Errores de acentuación
                'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
                'n': 'ñ',
                # Errores comunes
                'b': 'v', 'v': 'b',
                'c': 's', 's': 'c',
                'g': 'j', 'j': 'g',
                'll': 'y', 'y': 'll',
                'h': '',  # H muda
                'x': 's', 's': 'x',
                'z': 's', 's': 'z'
            }

class SpellChecker:
    """Sistema de corrección ortográfica y manejo de variaciones"""
    
    def __init__(self, db_path: str = "optimized_learning.db", config: Optional[SpellCheckConfig] = None):
        self.db_path = db_path
        self.config = config or SpellCheckConfig()
        self._init_database()
        self._load_vocabulary_cache()
    
    def _init_database(self):
        """Inicializar tabla para variaciones ortográficas"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS spelling_variations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correct_word TEXT NOT NULL,
                    variation TEXT NOT NULL,
                    similarity REAL DEFAULT 0.0,
                    error_type TEXT DEFAULT 'unknown',
                    frequency INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(correct_word, variation)
                )
            """)
            conn.commit()
    
    def _load_vocabulary_cache(self):
        """Cargar vocabulario en caché para búsquedas rápidas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT word FROM vocabulary")
                self.vocabulary_cache = {row[0].lower() for row in cursor.fetchall()}
        except Exception as e:
            logger.warning(f"No se pudo cargar vocabulario: {e}")
            self.vocabulary_cache = set()
    
    def check_spelling(self, word: str) -> Dict:
        """Verificar ortografía y sugerir correcciones"""
        word_lower = word.lower()
        
        # Si la palabra está en el vocabulario, está correcta
        if word_lower in self.vocabulary_cache:
            return {
                'is_correct': True,
                'original': word,
                'suggestions': [],
                'confidence': 1.0
            }
        
        # Buscar variaciones conocidas
        known_variation = self._find_known_variation(word_lower)
        if known_variation:
            return {
                'is_correct': False,
                'original': word,
                'corrected': known_variation,
                'suggestions': [known_variation],
                'confidence': 0.9,
                'error_type': 'known_variation'
            }
        
        # Buscar sugerencias usando diferentes métodos
        suggestions = []
        
        # 1. Búsqueda por similitud
        if self.config.enable_fuzzy_matching:
            fuzzy_suggestions = self._fuzzy_search(word_lower)
            suggestions.extend(fuzzy_suggestions)
        
        # 2. Corrección de errores comunes
        if self.config.enable_common_errors:
            common_error_suggestions = self._fix_common_errors(word_lower)
            suggestions.extend(common_error_suggestions)
        
        # 3. Búsqueda por similitud de sonido
        if self.config.enable_soundex:
            soundex_suggestions = self._soundex_search(word_lower)
            suggestions.extend(soundex_suggestions)
        
        # Eliminar duplicados y ordenar por similitud
        unique_suggestions = list(set(suggestions))
        scored_suggestions = self._score_suggestions(word_lower, unique_suggestions)
        
        return {
            'is_correct': False,
            'original': word,
            'suggestions': [s for s, _ in scored_suggestions[:5]],
            'confidence': scored_suggestions[0][1] if scored_suggestions else 0.0,
            'error_type': 'spelling_error'
        }
    
    def _find_known_variation(self, word: str) -> Optional[str]:
        """Buscar si la palabra es una variación conocida"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT correct_word FROM spelling_variations WHERE variation = ?",
                (word,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def _fuzzy_search(self, word: str) -> List[str]:
        """Búsqueda difusa por similitud"""
        suggestions = []
        
        for vocab_word in self.vocabulary_cache:
            similarity = difflib.SequenceMatcher(None, word, vocab_word).ratio()
            if similarity >= self.config.min_similarity:
                suggestions.append(vocab_word)
        
        return suggestions
    
    def _fix_common_errors(self, word: str) -> List[str]:
        """Corregir errores comunes en español"""
        suggestions = []
        
        # Aplicar correcciones de errores comunes
        for error, correction in self.config.common_errors.items():
            if error in word:
                corrected = word.replace(error, correction)
                if corrected in self.vocabulary_cache:
                    suggestions.append(corrected)
        
        return suggestions
    
    def _soundex_search(self, word: str) -> List[str]:
        """Búsqueda por similitud de sonido usando Soundex"""
        word_soundex = self._soundex(word)
        suggestions = []
        
        for vocab_word in self.vocabulary_cache:
            vocab_soundex = self._soundex(vocab_word)
            if word_soundex == vocab_soundex:
                suggestions.append(vocab_word)
        
        return suggestions
    
    def _soundex(self, word: str) -> str:
        """Implementación simple de Soundex para español"""
        # Mapeo de sonidos para español
        soundex_map = {
            'b': '1', 'f': '1', 'p': '1', 'v': '1',
            'c': '2', 'g': '2', 'j': '2', 'k': '2', 'q': '2', 's': '2', 'x': '2', 'z': '2',
            'd': '3', 't': '3',
            'l': '4',
            'm': '5', 'n': '5', 'ñ': '5',
            'r': '6'
        }
        
        if not word:
            return "0000"
        
        # Primera letra
        result = word[0].upper()
        
        # Convertir resto a códigos
        for char in word[1:]:
            char_lower = char.lower()
            if char_lower in soundex_map:
                code = soundex_map[char_lower]
                if code != result[-1]:  # No repetir códigos consecutivos
                    result += code
        
        # Rellenar con ceros si es necesario
        result = result.ljust(4, '0')
        
        return result[:4]
    
    def _score_suggestions(self, original: str, suggestions: List[str]) -> List[Tuple[str, float]]:
        """Puntuar sugerencias por relevancia"""
        scored = []
        
        for suggestion in suggestions:
            # Similitud de secuencia
            sequence_similarity = difflib.SequenceMatcher(None, original, suggestion).ratio()
            
            # Similitud de longitud
            length_similarity = 1 - abs(len(original) - len(suggestion)) / max(len(original), len(suggestion))
            
            # Puntuación combinada
            score = (sequence_similarity * 0.7) + (length_similarity * 0.3)
            scored.append((suggestion, score))
        
        # Ordenar por puntuación descendente
        return sorted(scored, key=lambda x: x[1], reverse=True)
    
    def learn_variation(self, correct_word: str, variation: str, error_type: str = "user_input"):
        """Aprender una nueva variación ortográfica"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insertar o actualizar variación
                conn.execute("""
                    INSERT OR REPLACE INTO spelling_variations 
                    (correct_word, variation, error_type, frequency)
                    VALUES (?, ?, ?, 
                        COALESCE((SELECT frequency + 1 FROM spelling_variations 
                                 WHERE correct_word = ? AND variation = ?), 1))
                """, (correct_word.lower(), variation.lower(), error_type, correct_word.lower(), variation.lower()))
                conn.commit()
                
                logger.info(f"Aprendida variación: '{variation}' -> '{correct_word}' ({error_type})")
                
        except Exception as e:
            logger.error(f"Error aprendiendo variación: {e}")
    
    def get_variations_stats(self) -> Dict:
        """Obtener estadísticas de variaciones aprendidas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_variations,
                        COUNT(DISTINCT correct_word) as unique_words,
                        AVG(similarity) as avg_similarity,
                        SUM(frequency) as total_frequency
                    FROM spelling_variations
                """)
                result = cursor.fetchone()
                
                return {
                    'total_variations': result[0],
                    'unique_words': result[1],
                    'avg_similarity': result[2] or 0.0,
                    'total_frequency': result[3] or 0
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

# Instancia global
spell_checker = SpellChecker() 