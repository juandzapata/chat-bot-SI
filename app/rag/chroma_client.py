import time
import chromadb
from chromadb.config import Settings
from config.settings import settings

def get_chroma_client(retries=5, delay=2):
    """
    Inicializa y retorna un cliente conectado a ChromaDB.
    Incluye reintentos para esperar a que Chroma esté disponible.
    """
    for attempt in range(1, retries + 1):
        try:
            client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=Settings(
                    chroma_api_impl="rest",
                    anonymized_telemetry=False
                )
            )
            # Validar conexión
            client.list_collections()
            print(f"✅ Conexión exitosa a ChromaDB en el intento {attempt}")
            return client
        except Exception as e:
            print(f"⚠️ Intento {attempt} fallido al conectar a ChromaDB: {e}")
            time.sleep(delay)
    raise ConnectionError("❌ No se pudo conectar a ChromaDB después de varios intentos.")
