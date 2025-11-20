#!/usr/bin/env python3
"""
Script para recrear la colección de ChromaDB con Gemini embeddings correctos
y reingestar todos los documentos del corpus.
"""

import sys
import logging
from pathlib import Path

# Añadir el directorio app al path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def recreate_collection():
    """Recrea la colección con Gemini embeddings"""
    from rag.chroma_client import get_chroma_client
    from rag.embeddings import embedding_function
    
    client = get_chroma_client()
    collection_name = "documentos_ucaldas"
    
    # 1. Verificar colección existente
    logger.info("🔍 Verificando colección existente...")
    existing_collections = [col.name for col in client.list_collections()]
    
    if collection_name in existing_collections:
        logger.info(f"📦 Colección '{collection_name}' encontrada")
        
        # Mostrar estadísticas actuales
        old_collection = client.get_collection(collection_name)
        old_count = old_collection.count()
        logger.info(f"   Chunks actuales: {old_count}")
        logger.info(f"   Embedding function: {type(old_collection._embedding_function).__name__}")
        
        # Borrar colección
        logger.info("🗑️  Borrando colección antigua...")
        client.delete_collection(collection_name)
        logger.info("✅ Colección borrada")
    else:
        logger.info(f"📦 No existe colección '{collection_name}'")
    
    # 2. Crear nueva colección con Gemini embeddings
    logger.info("🆕 Creando nueva colección con Gemini embeddings...")
    new_collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )
    logger.info(f"✅ Colección creada: {new_collection.name}")
    logger.info(f"   Embedding function: {type(new_collection._embedding_function).__name__}")
    
    return True

def reingest_documents():
    """Reingesta todos los documentos del corpus"""
    from rag.ingest_all import ingest_all_documents
    
    logger.info("\n" + "="*70)
    logger.info("📚 INICIANDO REINGESTA DE DOCUMENTOS")
    logger.info("="*70 + "\n")
    
    # Ejecutar ingesta completa
    result = ingest_all_documents()
    
    logger.info("\n" + "="*70)
    logger.info("📊 RESUMEN DE REINGESTA")
    logger.info("="*70)
    logger.info(f"Total documentos: {result['summary']['total_documents']}")
    logger.info(f"Exitosos: {result['summary']['successful']}")
    logger.info(f"Fallidos: {result['summary']['failed']}")
    
    if result['summary']['failed'] > 0:
        logger.warning("\n⚠️  Documentos fallidos:")
        for detail in result['details']:
            if not detail['success']:
                logger.warning(f"   - {detail['document_id']}: {detail.get('message', 'Error desconocido')}")
    
    logger.info("="*70 + "\n")
    
    return result

def verify_embeddings():
    """Verifica que la colección esté usando Gemini embeddings"""
    from rag.chroma_manager import get_or_create_collection
    
    logger.info("🔍 Verificando configuración final...")
    collection = get_or_create_collection("documentos_ucaldas")
    
    logger.info(f"✅ Colección: {collection.name}")
    logger.info(f"✅ Total chunks: {collection.count()}")
    logger.info(f"✅ Embedding function: {type(collection._embedding_function).__name__}")
    
    # Hacer una prueba de búsqueda
    logger.info("\n🧪 Prueba de búsqueda con Gemini embeddings...")
    test_query = "¿Qué aplicaciones tiene la IA en agricultura?"
    results = collection.query(
        query_texts=[test_query],
        n_results=3
    )
    
    logger.info(f"Pregunta: {test_query}")
    logger.info("Top 3 documentos recuperados:")
    for i, metadata in enumerate(results['metadatas'][0], 1):
        file_path = metadata.get('ruta_archivo', 'sin ruta')
        doc_name = file_path.split('/')[-1] if '/' in file_path else file_path
        logger.info(f"   {i}. {doc_name}")
        logger.info(f"      Título: {metadata.get('titulo', 'sin título')[:60]}...")
    
    return True

def main():
    try:
        print("\n" + "="*70)
        print("🔄 RECREACIÓN DE COLECCIÓN CON GEMINI EMBEDDINGS")
        print("="*70 + "\n")
        
        # Paso 1: Recrear colección
        print("PASO 1: Recrear colección")
        print("-" * 70)
        if not recreate_collection():
            logger.error("❌ Error recreando colección")
            return False
        
        print("\n")
        
        # Paso 2: Reingestar documentos
        print("PASO 2: Reingestar documentos")
        print("-" * 70)
        result = reingest_documents()
        
        if result['summary']['failed'] >= result['summary']['total_documents'] / 2:
            logger.error("❌ Demasiados documentos fallidos")
            return False
        
        print("\n")
        
        # Paso 3: Verificar
        print("PASO 3: Verificación final")
        print("-" * 70)
        verify_embeddings()
        
        print("\n" + "="*70)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("="*70 + "\n")
        
        logger.info("🎉 La colección ahora usa Gemini embeddings correctamente")
        logger.info("🎉 Las búsquedas deberían recuperar documentos más relevantes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante el proceso: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
