"""
app/rag/ingest_all.py
Script para ingestar automáticamente todo el corpus en ChromaDB.
Lee corpus_metadata.json y carga todos los documentos.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from rag.chroma_manager import get_or_create_collection
from rag.file_loader import FileLoader

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
CORPUS_PATH = Path("/data/corpus")  # Ruta absoluta para Docker
METADATA_FILE = CORPUS_PATH / "corpus_metadata.json"
COLLECTION_NAME = "documentos_ucaldas"

# Configuración de chunks
CHUNK_SIZE = 1000  # Caracteres por chunk
CHUNK_OVERLAP = 200  # Solapamiento entre chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Divide texto en chunks con solapamiento.
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño de cada chunk
        overlap: Caracteres de solapamiento entre chunks
        
    Returns:
        Lista de chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Intentar cortar en un espacio o salto de línea
        if end < len(text):
            last_space = chunk.rfind('\n\n')
            if last_space == -1:
                last_space = chunk.rfind('\n')
            if last_space == -1:
                last_space = chunk.rfind(' ')
            
            if last_space > chunk_size // 2:  # Asegurar que no sea muy corto
                chunk = chunk[:last_space]
                end = start + last_space
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [chunk for chunk in chunks if chunk]  # Filtrar chunks vacíos


def load_corpus_metadata() -> List[Dict]:
    """Carga el archivo JSON de metadatos del corpus."""
    if not METADATA_FILE.exists():
        logger.error(f"Archivo de metadatos no encontrado: {METADATA_FILE}")
        return []
    
    try:
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # El JSON tiene una lista bajo "documentos_regulacion_ia"
            documents = data.get("documentos_regulacion_ia", [])
            logger.info(f"✓ Metadatos cargados: {len(documents)} documentos")
            return documents
    except Exception as e:
        logger.error(f"Error cargando metadatos: {e}")
        return []


def build_file_path(metadata: Dict) -> Optional[Path]:
    """
    Construye la ruta completa del archivo basándose en el metadata.
    Maneja diferentes formatos y nombres de archivo.
    """
    # Obtener nombre base del archivo del metadata
    ruta_archivo = metadata.get("ruta_archivo", "")
    
    # Si la ruta termina en .pdf pero no tiene nombre, construimos uno
    if ruta_archivo.endswith("/.pdf") or ruta_archivo.endswith("\\.pdf"):
        # Extraer categoría del metadata
        categoria = metadata.get("categoria", "")
        doc_id = metadata.get("id", "")
        
        # Patrón esperado: data/corpus/{categoria}/document_{categoria}_{id}.pdf
        nombre_archivo = f"document_{categoria}_{doc_id.split('_')[-1]}.pdf"
        file_path = CORPUS_PATH / categoria / nombre_archivo
    else:
        # Ruta completa proporcionada - puede ser data/corpus/... o ruta absoluta
        file_path = Path(ruta_archivo)
        
        # Si la ruta empieza con "data/corpus", quitar ese prefijo y usar CORPUS_PATH
        if ruta_archivo.startswith("data/corpus/"):
            # Extraer la parte después de "data/corpus/"
            relative_path = ruta_archivo.replace("data/corpus/", "")
            file_path = CORPUS_PATH / relative_path
        elif not file_path.is_absolute():
            # Si es relativa pero no empieza con data/corpus, asumir relativa desde corpus
            file_path = CORPUS_PATH.parent / ruta_archivo
    
    return file_path


def ingest_single_document(metadata: Dict, collection, loader: FileLoader) -> Dict:
    """
    Ingesta un solo documento con su metadata.
    
    Returns:
        Dict con resultado de la operación
    """
    doc_id = metadata.get("id", "unknown")
    titulo = metadata.get("titulo", "Sin título")
    
    logger.info(f"📄 Procesando: {titulo} ({doc_id})")
    
    # Construir ruta del archivo
    file_path = build_file_path(metadata)
    
    if not file_path or not file_path.exists():
        logger.warning(f"⚠️  Archivo no encontrado: {file_path}")
        return {
            "success": False,
            "document_id": doc_id,
            "message": f"Archivo no encontrado: {file_path}"
        }
    
    # Cargar archivo
    result = loader.load_file(str(file_path))
    
    if not result.get('success'):
        logger.error(f"❌ Error cargando archivo {file_path}: {result.get('error')}")
        return {
            "success": False,
            "document_id": doc_id,
            "message": result.get('error', 'Unknown error')
        }
    
    text = result.get('text', '')
    
    if len(text.strip()) < 50:  # Validar que haya contenido suficiente
        logger.warning(f"⚠️  Texto demasiado corto para {doc_id}")
        return {
            "success": False,
            "document_id": doc_id,
            "message": "Texto extraído muy corto o vacío"
        }
    
    # Dividir en chunks
    chunks = chunk_text(text)
    logger.info(f"  → Dividido en {len(chunks)} chunks")
    
    # Preparar metadatos base
    # ChromaDB solo acepta tipos primitivos: str, int, float, bool, None
    # Convertir listas y otros tipos complejos a string
    base_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, list):
            # Convertir listas a string JSON
            base_metadata[key] = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, dict):
            # Convertir diccionarios a string JSON
            base_metadata[key] = json.dumps(value, ensure_ascii=False)
        elif value is None:
            base_metadata[key] = None
        elif isinstance(value, (str, int, float, bool)):
            base_metadata[key] = value
        else:
            # Cualquier otro tipo a string
            base_metadata[key] = str(value)
    
    # Agregar metadatos adicionales
    base_metadata['filename'] = result['metadata'].get('filename', file_path.name)
    base_metadata['size_bytes'] = result['metadata'].get('size_bytes', 0)
    base_metadata['chunks_total'] = len(chunks)
    
    # Agregar cada chunk a ChromaDB
    ids_to_add = []
    documents_to_add = []
    metadatas_to_add = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{i}"
        chunk_metadata = {
            **base_metadata,
            'chunk_index': i,
            'chunk_text_length': len(chunk)
        }
        
        ids_to_add.append(chunk_id)
        documents_to_add.append(chunk)
        metadatas_to_add.append(chunk_metadata)
    
    # Agregar todos los chunks de una vez (más eficiente)
    try:
        collection.add(
            ids=ids_to_add,
            documents=documents_to_add,
            metadatas=metadatas_to_add
        )
        logger.info(f"✓ {len(chunks)} chunks agregados exitosamente")
        return {
            "success": True,
            "document_id": doc_id,
            "chunks_count": len(chunks),
            "message": f"Documento ingerido exitosamente"
        }
    except Exception as e:
        logger.error(f"❌ Error agregando a ChromaDB: {e}")
        return {
            "success": False,
            "document_id": doc_id,
            "message": str(e)
        }


def ingest_all_documents() -> Dict:
    """
    Función principal para ingerir todos los documentos del corpus.
    
    Returns:
        Dict con resumen de la ingesta
    """
    logger.info("🚀 Iniciando ingesta del corpus completo...")
    
    # Cargar metadatos
    metadata_list = load_corpus_metadata()
    
    if not metadata_list:
        return {
            "success": False,
            "message": "No se encontraron documentos para ingerir"
        }
    
    # Inicializar componentes
    loader = FileLoader()
    collection = get_or_create_collection(COLLECTION_NAME)
    
    # Estadísticas
    results = []
    successful = 0
    failed = 0
    
    # Procesar cada documento
    for metadata in metadata_list:
        result = ingest_single_document(metadata, collection, loader)
        results.append(result)
        
        if result.get('success'):
            successful += 1
        else:
            failed += 1
    
    # Resumen
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Ingesta completada")
    logger.info(f"   Exitosos: {successful}/{len(metadata_list)}")
    logger.info(f"   Fallidos: {failed}/{len(metadata_list)}")
    logger.info(f"{'='*60}\n")
    
    return {
        "success": True,
        "total_documents": len(metadata_list),
        "successful": successful,
        "failed": failed,
        "results": results,
        "collection": COLLECTION_NAME
    }


# Ejecutar directamente si se llama como script
if __name__ == "__main__":
    try:
        result = ingest_all_documents()
        print(f"\n{'='*60}")
        print(f"Resultado final: {result.get('message', 'Completado')}")
        print(f"{'='*60}\n")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
