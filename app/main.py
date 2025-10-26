from fastapi import FastAPI
from config.settings import settings
from rag.chroma_manager import add_document

app = FastAPI(
    title="ChatBot IA - Universidad de Caldas",
    description="Backend con FastAPI + Docker + ChromaDB + Gemini",
    version="0.1.0",
)

@app.get("/")
def read_root():
    # Conexión rápida para probar que Chroma funciona
    try:
        from rag.chroma_client import get_chroma_client
        client = get_chroma_client()
        client.list_collections()
        status = "Conexión exitosa a ChromaDB"
    except Exception as e:
        status = f"Error conectando a ChromaDB: {e}"

    return {
        "status": "ChatBot IA funcionando correctamente",
        "mode": settings.MODE,
        "chroma_status": status
    }

# 🚀 Nuevo endpoint de prueba
@app.post("/ingest_test")
def ingest_test():
    try:
        texto = "La Universidad de Caldas es una institución pública ubicada en Manizales, Colombia, reconocida por su excelencia académica."
        resultado = add_document(
            collection_name="documentos_ucaldas",
            document_id="doc_test_1",
            text=texto,
            metadata={"origen": "prueba_inicial"}
        )
        return {"status": "ok", "message": resultado}
    except Exception as e:
        return {"status": "error", "message": str(e)}
