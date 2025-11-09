"""
app/rag/models.py
Sistema de modelos múltiples para el chatbot.
Soporta Gemini y LLaMA3 (Groq).
"""

import logging
from typing import Dict, Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

class ModelProvider:
    """Clase base para proveedores de modelos."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_response(self, prompt: str, response_mode: str = "extended") -> str:
        """
        Genera respuesta basada en el prompt.
        
        Args:
            prompt: El prompt para generar la respuesta
            response_mode: 'brief' o 'extended' (usado por LLaMA3, ignorado por Gemini)
        """
        raise NotImplementedError

class GeminiProvider(ModelProvider):
    """Proveedor para modelos Gemini."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✅ Gemini provider inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando Gemini: {e}")
            raise
    
    def generate_response(self, prompt: str, response_mode: str = "extended") -> str:
        """
        Genera respuesta usando Gemini.
        
        NOTA: Gemini controla la longitud via instrucciones en el prompt,
        NO usa generation_config para evitar bloqueos de safety.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generando respuesta con Gemini: {e}")
            raise

class GroqProvider(ModelProvider):
    """Proveedor para modelos LLaMA3 via Groq."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            logger.info("✅ Groq provider inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando Groq: {e}")
            raise
    
    def generate_response(self, prompt: str, response_mode: str = "extended") -> str:
        """
        Genera respuesta usando LLaMA3 via Groq.
        
        Args:
            prompt: El prompt para generar la respuesta
            response_mode: 'brief' (200 tokens) o 'extended' (800 tokens)
        """
        try:
            # Configurar tokens según el modo
            max_tokens = 200 if response_mode == "brief" else 800
            
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente académico de la Universidad de Caldas especializado en normativas de Inteligencia Artificial. Responde de manera precisa y académica basándote únicamente en el contexto proporcionado."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generando respuesta con Groq: {e}")
            raise

class ModelManager:
    """Gestor de modelos múltiples."""
    
    def __init__(self):
        self.providers: Dict[str, ModelProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Inicializa los proveedores disponibles."""
        
        # Gemini
        if settings.GEMINI_API_KEY:
            try:
                self.providers["gemini"] = GeminiProvider(settings.GEMINI_API_KEY)
                logger.info("✅ Gemini disponible")
            except Exception as e:
                logger.warning(f"⚠️ Gemini no disponible: {e}")
        
        # Groq/LLaMA3
        if settings.GROQ_API_KEY:
            try:
                self.providers["llama3"] = GroqProvider(settings.GROQ_API_KEY)
                logger.info("✅ LLaMA3 (Groq) disponible")
            except Exception as e:
                logger.warning(f"⚠️ LLaMA3 no disponible: {e}")
        
        if not self.providers:
            raise RuntimeError("❌ No hay modelos disponibles. Verifica las API keys.")
        
        logger.info(f"Modelos disponibles: {list(self.providers.keys())}")
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Retorna lista de modelos disponibles."""
        models = []
        
        if "gemini" in self.providers:
            models.append({
                "id": "gemini",
                "name": "Gemini 2.5 Flash",
                "provider": "Google",
                "description": "Modelo de Google para generación de texto"
            })
        
        if "llama3" in self.providers:
            models.append({
                "id": "llama3", 
                "name": "LLaMA 3 8B",
                "provider": "Groq",
                "description": "Modelo open source de Meta via Groq"
            })
        
        return models
    
    def generate_response(self, prompt: str, model_id: str = "gemini", response_mode: str = "extended") -> str:
        """
        Genera respuesta usando el modelo especificado.
        
        Args:
            prompt: El prompt para generar la respuesta
            model_id: ID del modelo a usar ('gemini', 'llama3')
            response_mode: 'brief' o 'extended'
        """
        if model_id not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(f"Modelo '{model_id}' no disponible. Disponibles: {available}")
        
        provider = self.providers[model_id]
        return provider.generate_response(prompt, response_mode)
    
    def get_default_model(self) -> str:
        """Retorna el modelo por defecto."""
        # Prioridad: Gemini primero, luego LLaMA3
        if "gemini" in self.providers:
            return "gemini"
        elif "llama3" in self.providers:
            return "llama3"
        else:
            return list(self.providers.keys())[0]

# Instancia global del gestor de modelos
model_manager = ModelManager()
