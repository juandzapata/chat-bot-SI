from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from config.settings import settings
from rag.chroma_manager import add_document
from utils.logger import get_logger
import logging
from pathlib import Path
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logger anonimizado
anon_logger = get_logger()

app = FastAPI(
    title="ChatBot IA - Universidad de Caldas",
    description="Backend con FastAPI + Docker + ChromaDB + Gemini",
    version="0.1.0",
)

# Configurar CORS para permitir requests del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica el dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio: registrar startup
@app.on_event("startup")
async def startup_event():
    """Registra el inicio del sistema"""
    anon_logger.log_system_event(
        event="system_startup",
        details={
            "mode": settings.MODE,
            "version": "0.1.0"
        }
    )
    logger.info("Sistema iniciado correctamente")

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
        "top_k": 3,  // opcional, número de documentos a recuperar
        "model": "gemini",  // opcional, modelo a usar: "gemini" o "llama3"
        "mode": "extended"  // opcional, modo de respuesta: "brief" o "extended"
    }
    """
    start_time = time.time()
    
    try:
        question = query.get("question", "")
        top_k = query.get("top_k", 3)
        model_id = query.get("model", "gemini")  # Default a Gemini
        response_mode = query.get("mode", "extended")  # Default a extendido
        
        # Validar modo de respuesta
        if response_mode not in ["brief", "extended"]:
            raise HTTPException(
                status_code=400, 
                detail="El modo debe ser 'brief' o 'extended'"
            )
        
        if not question or len(question.strip()) == 0:
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")
        
        # Importar componentes necesarios
        from rag.chroma_manager import get_or_create_collection
        from rag.models import model_manager
        
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
        
        # Instrucción adicional según el modo (para Gemini)
        mode_instruction = ""
        if response_mode == "brief":
            mode_instruction = "\n\nIMPORTANTE: Proporciona una respuesta BREVE y CONCISA (máximo 150 palabras)."
        else:
            mode_instruction = "\n\nIMPORTANTE: Proporciona una respuesta DETALLADA y COMPLETA (entre 400-600 palabras)."
        
        # Generar prompt según el modelo
        if model_id == "gemini":
            prompt = f"""Eres un asistente académico de la Universidad de Caldas especializado en normativas de Inteligencia Artificial.

Basándote ÚNICAMENTE en el siguiente contexto de los documentos oficiales, responde la pregunta del usuario de manera precisa y académica.{mode_instruction}

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA:"""
        else:  # LLaMA3
            prompt = f"""Basándote ÚNICAMENTE en el siguiente contexto de los documentos oficiales, responde la pregunta del usuario de manera precisa y académica.{mode_instruction}

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA:"""
        
        # Generar respuesta con el modelo seleccionado
        logger.info(f"Generando respuesta con {model_id} en modo {response_mode}...")
        answer = model_manager.generate_response(prompt, model_id, response_mode)
        
        # Preparar metadatos de los documentos citados
        cited_docs = []
        if results['metadatas'] and results['metadatas'][0]:
            for i, metadata in enumerate(results['metadatas'][0]):
                cited_docs.append({
                    "title": metadata.get('titulo', 'Sin título'),
                    "source": metadata.get('organismo', 'Fuente desconocida'),
                    "category": metadata.get('categoria', ''),
                    "year": metadata.get('anio', 'N/A'),
                    "file_path": metadata.get('ruta_archivo', '')
                })
        
        # Calcular tiempo de respuesta
        response_time = time.time() - start_time
        
        # Registrar interacción de forma anonimizada
        anon_logger.log_interaction(
            question=question,
            answer=answer,
            model=model_id,
            response_mode=response_mode,
            sources_count=len(cited_docs),
            response_time=response_time,
            session_id=query.get("session_id", None),
            metadata={
                "top_k": top_k,
                "context_length": len(context)
            }
        )
        
        return {
            "status": "ok",
            "answer": answer,
            "question": question,
            "model_used": model_id,
            "response_mode": response_mode,
            "sources": cited_docs,
            "context_used": len(cited_docs)
        }
        
    except Exception as e:
        # Registrar error de forma anonimizada
        anon_logger.log_error(
            error_type="ChatEndpointError",
            error_message=str(e),
            context={
                "model": query.get("model", "unknown"),
                "response_mode": query.get("mode", "unknown")
            }
        )
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


# 🤖 Endpoint para listar modelos disponibles
@app.get("/models")
def get_available_models():
    """Retorna lista de modelos disponibles y modos de respuesta."""
    try:
        from rag.models import model_manager
        
        models = model_manager.get_available_models()
        default_model = model_manager.get_default_model()
        
        return {
            "status": "ok",
            "available_models": models,
            "default_model": default_model,
            "total_models": len(models),
            "response_modes": [
                {
                    "id": "brief",
                    "name": "Breve",
                    "description": "Respuesta concisa (~200 tokens, ~150 palabras)",
                    "max_tokens": 200
                },
                {
                    "id": "extended",
                    "name": "Extendido",
                    "description": "Respuesta detallada (~800 tokens, ~600 palabras)",
                    "max_tokens": 800
                }
            ],
            "default_mode": "extended"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo modelos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 📚 Endpoint para obtener todas las fuentes disponibles
@app.get("/sources")
def get_sources():
    """
    Retorna todas las fuentes documentales disponibles en la base de datos,
    agrupadas por categoría y deduplicadas por título.
    """
    try:
        from rag.chroma_manager import get_all_sources
        from collections import defaultdict
        
        # Obtener todas las fuentes
        all_sources = get_all_sources()
        
        # Agrupar por categoría y deduplicar por título
        sources_by_category = defaultdict(dict)  # Cambio: dict en lugar de list
        for source in all_sources:
            category = source.get("category", "sin_categoria")
            title = source["title"]
            
            # Solo agregar si no existe (deduplicación por título)
            if title not in sources_by_category[category]:
                sources_by_category[category][title] = {
                    "title": title,
                    "source": source["source"],
                    "year": source["year"]
                }
        
        # Convertir a formato de respuesta
        categories = []
        category_names = {
            "colombia": "Colombia",
            "internacional": "Internacional",
            "universidad": "Universidad de Caldas",
            "sin_categoria": "Sin Categoría"
        }
        
        total_unique_sources = 0
        for category, sources_dict in sources_by_category.items():
            sources_list = list(sources_dict.values())
            total_unique_sources += len(sources_list)
            
            categories.append({
                "category": category,
                "category_name": category_names.get(category, category.capitalize()),
                "sources": sources_list,
                "count": len(sources_list)
            })
        
        # Ordenar categorías (colombia, internacional, universidad, otros)
        category_order = ["colombia", "internacional", "universidad"]
        categories.sort(key=lambda x: category_order.index(x["category"]) if x["category"] in category_order else 999)
        
        return {
            "status": "ok",
            "total_sources": total_unique_sources,  # Ahora muestra documentos únicos
            "total_categories": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo fuentes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 📜 Endpoint para obtener política de uso y privacidad
@app.get("/policy", response_class=PlainTextResponse)
def get_policy():
    """
    Retorna la política de uso, privacidad y términos del servicio del chatbot.
    """
    try:
        policy_path = Path(__file__).parent.parent / "data" / "POLICY.md"
        
        if not policy_path.exists():
            logger.error(f"Archivo de política no encontrado: {policy_path}")
            raise HTTPException(status_code=404, detail="Política no disponible")
        
        with open(policy_path, "r", encoding="utf-8") as f:
            policy_content = f.read()
        
        logger.info("Política de uso servida exitosamente")
        return policy_content
        
    except FileNotFoundError:
        logger.error("Archivo POLICY.md no encontrado")
        raise HTTPException(status_code=404, detail="Política no disponible")
    except Exception as e:
        logger.error(f"Error obteniendo política: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 🧪 Endpoint de prueba para Gemini sin RAG
@app.post("/test_gemini")
def test_gemini(query: dict):
    """Endpoint de prueba para Gemini sin contexto RAG."""
    try:
        from rag.models import model_manager
        
        question = query.get("question", "¿Qué es la inteligencia artificial?")
        mode = query.get("mode", "brief")
        
        # Prompt simple sin contexto
        simple_prompt = f"Responde brevemente: {question}"
        
        answer = model_manager.generate_response(simple_prompt, "gemini", mode)
        
        return {
            "status": "ok",
            "answer": answer,
            "mode": mode
        }
    except Exception as e:
        logger.error(f"Error en test_gemini: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
