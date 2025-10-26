from rag.chroma_client import get_chroma_client
from rag.embeddings import embedding_function  # ✅ ahora importamos la instancia de la clase

def get_or_create_collection(collection_name="documentos_ucaldas"):
    client = get_chroma_client()

    # Buscar si ya existe
    for col in client.list_collections():
        if col.name == collection_name:
            return col

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
