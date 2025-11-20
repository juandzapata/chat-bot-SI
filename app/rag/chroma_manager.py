from rag.chroma_client import get_chroma_client
from rag.embeddings import embedding_function  # ✅ ahora importamos la instancia de la clase

def get_or_create_collection(collection_name="documentos_ucaldas"):
    client = get_chroma_client()

    # Buscar si ya existe
    collection_names = [col.name for col in client.list_collections()]
    if collection_name in collection_names:
        # CRITICAL: Usar get_collection con embedding_function explícito
        # para que ChromaDB use Gemini embeddings en las queries
        return client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )

    # Crear la colección usando Gemini como función de embeddings
    return client.create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

def add_document(collection_name: str, document_id: str, text: str, metadata=None):
    collection = get_or_create_collection(collection_name)
    collection.add(
        ids=[document_id],
        documents=[text],
        metadatas=[metadata or {}]
        # No pasamos embedding manualmente porque Chroma usará embedding_function automáticamente
    )
    return f"Documento {document_id} agregado correctamente a la colección '{collection_name}'."

def get_all_sources(collection_name="documentos_ucaldas"):
    """
    Obtiene todos los documentos de la colección y extrae sus metadatos.
    Retorna una lista de diccionarios con la información de cada fuente.
    """
    collection = get_or_create_collection(collection_name)
    
    # Obtener todos los documentos (sin límite)
    results = collection.get(
        include=["metadatas"]  # Solo necesitamos los metadatos
    )
    
    sources = []
    if results and results.get("metadatas"):
        for metadata in results["metadatas"]:
            # Extraer campos relevantes
            source_info = {
                "title": metadata.get("titulo", "Sin título"),
                "source": metadata.get("organismo", "Sin fuente"),
                "category": metadata.get("categoria", "sin_categoria"),
                "year": metadata.get("anio", "N/A"),
                "file_path": metadata.get("ruta_archivo", "")
            }
            sources.append(source_info)
    
    return sources
