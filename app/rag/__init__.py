"""
app/rag
Módulo RAG para el chatbot de Universidad de Caldas
"""

from .chroma_client import get_chroma_client
from .chroma_manager import get_or_create_collection, add_document
from .embeddings import embedding_function, GeminiEmbeddingFunction
from .file_loader import FileLoader, load_file, load_directory
from .ingest_all import ingest_all_documents
from .models import model_manager, ModelManager

__all__ = [
    'get_chroma_client',
    'get_or_create_collection',
    'add_document',
    'embedding_function',
    'GeminiEmbeddingFunction',
    'FileLoader',
    'load_file',
    'load_directory',
    'ingest_all_documents',
    'model_manager',
    'ModelManager'
]
