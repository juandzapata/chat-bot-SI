from fastapi import FastAPI, HTTPException
from config.settings import settings
from rag.chroma_manager import add_document
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


# 🚀 Endpoint para ingerir todo el corpus
@app.post("/ingest_all")
def ingest_all():
    """
    Endpoint para ingerir todos los documentos del corpus en ChromaDB.
    Lee corpus_metadata.json y procesa todos los archivos.
    """
    try:
        from rag.ingest_all import ingest_all_documents
        result = ingest_all_documents()
        
        if result.get("success"):
            return {
                "status": "ok",
                "message": "Ingesta completada exitosamente",
                "summary": {
                    "total_documents": result.get("total_documents", 0),
                    "successful": result.get("successful", 0),
                    "failed": result.get("failed", 0)
                },
                "details": result.get("results", [])
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Error desconocido"))
            
    except Exception as e:
        logger.error(f"Error en /ingest_all: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 🚀 Endpoint de chat con RAG
@app.post("/chat")
def chat(query: dict):
    """
    Endpoint para realizar consultas al chatbot con RAG.
    
    Body esperado:
    {
        "question": "¿Cuál es la normativa sobre IA en Colombia?",
        "top_k": 3  // opcional, número de documentos a recuperar
    }
    """
    try:
        question = query.get("question", "")
        top_k = query.get("top_k", 3)
        
        if not question or len(question.strip()) == 0:
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")
        
        # Importar componentes necesarios
        from rag.chroma_manager import get_or_create_collection
        from rag.embeddings import embedding_function
        import google.generativeai as genai
        from config.settings import settings
        
        # Configurar Gemini para generación
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Obtener colección
        collection = get_or_create_collection("documentos_ucaldas")
        
        # Buscar documentos relevantes
        logger.info(f"Buscando contexto relevante para: {question}")
        results = collection.query(
            query_texts=[question],
            n_results=top_k
        )
        
        # Construir contexto
        context_parts = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                context_parts.append(f"[Documento {i+1}]: {doc}")
        
        context = "\n\n".join(context_parts) if context_parts else "No se encontró contexto relevante."
        
        # Generar respuesta con Gemini
        prompt = f"""Eres un asistente académico de la Universidad de Caldas especializado en normativas de Inteligencia Artificial.

Basándote ÚNICAMENTE en el siguiente contexto de los documentos oficiales, responde la pregunta del usuario de manera precisa y académica.

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA:"""
        
        logger.info("Generando respuesta con Gemini...")
        response = model.generate_content(prompt)
        answer = response.text
        
        # Preparar metadatos de los documentos citados
        cited_docs = []
        if results['metadatas'] and results['metadatas'][0]:
            for i, metadata in enumerate(results['metadatas'][0]):
                cited_docs.append({
                    "title": metadata.get('titulo', 'Sin título'),
                    "source": metadata.get('organismo', 'Fuente desconocida'),
                    "category": metadata.get('categoria', ''),
                    "year": metadata.get('anio', 'N/A')
                })
        
        return {
            "status": "ok",
            "answer": answer,
            "question": question,
            "sources": cited_docs,
            "context_used": len(cited_docs)
        }
        
    except Exception as e:
        logger.error(f"Error en /chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 🔍 Endpoint para ver estadísticas de la colección
@app.get("/collection_stats")
def get_collection_stats():
    """Retorna estadísticas de la colección de documentos."""
    try:
        from rag.chroma_manager import get_or_create_collection
        
        collection = get_or_create_collection("documentos_ucaldas")
        
        # Obtener conteo de documentos
        count = collection.count()
        
        return {
            "status": "ok",
            "collection": "documentos_ucaldas",
            "total_chunks": count,
            "message": f"Colección contiene {count} chunks de documentos"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
