"""
Sistema de Logging Anonimizado
Registra interacciones del chatbot sin datos sensibles del usuario
"""

import logging
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import re

# Configuración de directorios
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configurar formato de logs
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class AnonymizedLogger:
    """Logger que anonimiza datos sensibles antes de registrar"""
    
    def __init__(self, name: str = "chatbot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Handler para archivo de logs generales
        general_handler = logging.FileHandler(
            LOGS_DIR / f"chatbot_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        general_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        
        # Handler para archivo de interacciones (JSON)
        self.interactions_file = LOGS_DIR / f"interactions_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        self.logger.addHandler(general_handler)
        
        # Patrones de datos sensibles a anonimizar
        self.sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'cc': r'\b\d{6,19}\b',  # Número de cédula/tarjeta
            'name': r'\b(mi nombre es|me llamo|soy)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        }
    
    def _anonymize_text(self, text: str) -> str:
        """Anonimiza datos sensibles en el texto"""
        anonymized = text
        
        # Reemplazar emails
        anonymized = re.sub(self.sensitive_patterns['email'], '[EMAIL_ANONIMIZADO]', anonymized)
        
        # Reemplazar teléfonos
        anonymized = re.sub(self.sensitive_patterns['phone'], '[TELEFONO_ANONIMIZADO]', anonymized)
        
        # Reemplazar números largos (posibles cédulas/tarjetas)
        anonymized = re.sub(self.sensitive_patterns['cc'], '[NUMERO_ANONIMIZADO]', anonymized)
        
        # Reemplazar nombres propios después de frases de presentación
        anonymized = re.sub(
            self.sensitive_patterns['name'],
            r'\1 [NOMBRE_ANONIMIZADO]',
            anonymized,
            flags=re.IGNORECASE
        )
        
        return anonymized
    
    def _generate_session_id(self, identifier: Optional[str] = None) -> str:
        """Genera ID de sesión anonimizado usando hash"""
        if identifier:
            return hashlib.sha256(identifier.encode()).hexdigest()[:16]
        return hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:16]
    
    def log_interaction(
        self,
        question: str,
        answer: str,
        model: str,
        response_mode: str,
        sources_count: int,
        response_time: float,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Registra una interacción de forma anonimizada
        
        Args:
            question: Pregunta del usuario (será anonimizada)
            answer: Respuesta del chatbot (será anonimizada)
            model: Modelo usado (gemini/llama3)
            response_mode: Modo de respuesta (brief/extended)
            sources_count: Número de fuentes consultadas
            response_time: Tiempo de respuesta en segundos
            session_id: ID de sesión opcional (será hasheado)
            metadata: Metadata adicional
        """
        # Anonimizar textos
        anon_question = self._anonymize_text(question)
        anon_answer = self._anonymize_text(answer)
        anon_session = self._generate_session_id(session_id)
        
        # Crear registro de interacción
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "session_id": anon_session,
            "question": anon_question,
            "answer": anon_answer,
            "question_length": len(question),
            "answer_length": len(answer),
            "model": model,
            "response_mode": response_mode,
            "sources_count": sources_count,
            "response_time_seconds": round(response_time, 3),
            "metadata": metadata or {}
        }
        
        # Guardar en archivo JSONL (JSON Lines)
        with open(self.interactions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(interaction, ensure_ascii=False) + '\n')
        
        # Log general
        self.logger.info(
            f"Interacción registrada | Session: {anon_session} | "
            f"Model: {model} | Mode: {response_mode} | "
            f"Time: {response_time:.2f}s | Sources: {sources_count}"
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Registra errores de forma estructurada"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": self._anonymize_text(error_message),
            "context": context or {}
        }
        
        error_file = LOGS_DIR / f"errors_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(error_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_data, ensure_ascii=False) + '\n')
        
        self.logger.error(f"{error_type}: {error_message}")
    
    def log_system_event(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Registra eventos del sistema (startup, shutdown, etc.)"""
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "details": details or {}
        }
        
        system_file = LOGS_DIR / f"system_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(system_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + '\n')
        
        self.logger.info(f"System event: {event}")


# Instancia global del logger
anonymized_logger = AnonymizedLogger()


def get_logger() -> AnonymizedLogger:
    """Obtiene la instancia del logger anonimizado"""
    return anonymized_logger
