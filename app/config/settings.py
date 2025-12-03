import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Settings:
    def __init__(self):
        # Modo del proyecto
        self.MODE = os.getenv("MODE", "development")

        # Configuración de ChromaDB
        self.CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma_db")
        self.CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
        self.CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/data/vector_store")
        
        # Usar ChromaDB embebido en producción, HTTP en desarrollo
        self.USE_EMBEDDED_CHROMA = os.getenv("USE_EMBEDDED_CHROMA", "false").lower() == "true"

        # Configuración del backend
        self.APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
        self.APP_PORT = int(os.getenv("APP_PORT", 9000))

        # Clave para modelo Gemini (si aplica)
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
        
        # Clave para modelo Groq/LLaMA3
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", None)

# Crear instancia global de Settings
settings = Settings()
