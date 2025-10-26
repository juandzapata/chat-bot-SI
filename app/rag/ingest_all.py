import os
import json
from chroma_manager import get_or_create_collection
from embeddings import embedding_function
from config.settings import settings
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader

# ===== Configuración del corpus =====
CORPUS_PATH = "data/corpus"
METADATA_FILE = os.path.join(CORPUS_PATH, "corpus_metadata.json")
COLLECTION_NAME = "documentos_ucaldas"

# ===== Función para extraer texto de PDF =====
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error leyendo el PDF '{pdf_path}': {e}")

# ===== Función para dividir texto en chunks =====
def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # Retrocede un poco para mantener contexto
    return chunks

# ===== Ingestar documentos =====
def ingest_all_documents():
    print("🚀 Iniciando ingesta del corpus...")
    
    # Cargar metadatos
    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata_list = json.load(file)
    
    collection = get_or_create_collection(COLLECTION_NAME)
    
    for meta in metadata_list:
        doc_path = meta["ruta_archivo"]
        full_path = os.path.join(".", doc_path)  # Ruta relativa desde la raíz
        
        if not os.path.exists(full_path):
            print(f"⚠️ Archivo no encontrado: {full_path}, se omite.")
            continue
        
        print(f"📄 Procesando documento: {meta['titulo']} ({meta['id']})")
        text = extract_text_from_pdf(full_path)
        chunks = chunk_text(text)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{meta['id']}_chunk_{i}"
            chunk_metadata = {**meta, "chunk_index": i}
            
            collection.add(
                ids=[chunk_id],
                documents=[chunk],
                metadatas=[chunk_metadata]
            )
    
    print("✅ Ingesta completada exitosamente.")

# ===== Ejecutar directamente =====
if __name__ == "__main__":
    ingest_all_documents()
