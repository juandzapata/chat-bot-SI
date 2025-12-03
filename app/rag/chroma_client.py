import time
import chromadb
from chromadb.config import Settings
from config.settings import settings
from pathlib import Path

def get_chroma_client(retries=5, delay=2):
    """
    Inicializa y retorna un cliente conectado a ChromaDB.
    Usa modo embebido en producción o HTTP en desarrollo.
    """
    # Modo embebido (producción): ChromaDB como librería
    if settings.USE_EMBEDDED_CHROMA:
        try:
            persist_dir = Path(settings.CHROMA_PERSIST_DIR)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            print(f"✅ ChromaDB embebido inicializado en {persist_dir}")
            return client
        except Exception as e:
            raise ConnectionError(f"❌ Error al inicializar ChromaDB embebido: {e}")
    
    # Modo HTTP (desarrollo): ChromaDB como servicio separado
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
            print(f"✅ Conexión exitosa a ChromaDB HTTP en el intento {attempt}")
            return client
        except Exception as e:
            print(f"⚠️ Intento {attempt} fallido al conectar a ChromaDB: {e}")
            time.sleep(delay)
    raise ConnectionError("❌ No se pudo conectar a ChromaDB después de varios intentos.")
