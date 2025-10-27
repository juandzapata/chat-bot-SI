"""
app/rag/file_loader.py
Utilidad para cargar y extraer texto de diferentes formatos de archivo.
Prioridad: PDF, con soporte extensible para TXT, DOCX, MD.
"""

import os
from typing import Dict, List, Optional
from pathlib import Path
import logging

# PDF processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Alternative PDF library (more robust)
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# DOCX processing
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)


class FileLoader:
    """
    Clase para cargar documentos de diferentes formatos.
    Retorna diccionario con texto y metadatos.
    """
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.md', '.docx', '.png', '.jpg', '.jpeg'}
    
    def __init__(self):
        """Inicializa el loader y verifica dependencias disponibles."""
        self.available_loaders = {
            'pdf': PDF_AVAILABLE or PDFPLUMBER_AVAILABLE,
            'txt': True,  # Siempre disponible
            'md': True,   # Siempre disponible
            'docx': DOCX_AVAILABLE
        }
        logger.info(f"FileLoader inicializado. Loaders disponibles: {self.available_loaders}")
    
    def load_file(self, file_path: str) -> Optional[Dict[str, any]]:
        """
        Carga un archivo y extrae su contenido.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Dict con:
                - text: Contenido extraído
                - metadata: Información del archivo
                - success: Boolean indicando éxito
                - error: Mensaje de error si falla
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"Archivo no encontrado: {file_path}")
            return {
                'text': '',
                'metadata': {},
                'success': False,
                'error': 'Archivo no encontrado'
            }
        
        extension = path.suffix.lower()
        
        if extension not in self.SUPPORTED_EXTENSIONS:
            logger.warning(f"Extensión no soportada: {extension}")
            return {
                'text': '',
                'metadata': {'filename': path.name, 'extension': extension},
                'success': False,
                'error': f'Extensión no soportada: {extension}'
            }
        
        # Metadata básica
        metadata = {
            'filename': path.name,
            'extension': extension,
            'size_bytes': path.stat().st_size,
            'path': str(path.absolute())
        }
        
        # Despachar según extensión
        try:
            if extension == '.pdf':
                text = self._load_pdf(path)
            elif extension in ['.txt', '.md']:
                text = self._load_text(path)
            elif extension == '.docx':
                text = self._load_docx(path)
            elif extension in ['.png', '.jpg', '.jpeg']:
                # Para imágenes, simplemente retornar que no se puede procesar
                # sin OCR (para evitar dependencias adicionales por ahora)
                logger.warning(f"No se puede procesar imagen {path.name} sin OCR configurado")
                text = f"[Archivo de imagen: {path.name}]"
            else:
                text = ''
            
            if not text or len(text.strip()) == 0:
                logger.warning(f"No se extrajo texto del archivo: {file_path}")
                return {
                    'text': '',
                    'metadata': metadata,
                    'success': False,
                    'error': 'No se pudo extraer texto'
                }
            
            logger.info(f"✓ Archivo cargado exitosamente: {path.name} ({len(text)} chars)")
            return {
                'text': text,
                'metadata': metadata,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error procesando {file_path}: {str(e)}")
            return {
                'text': '',
                'metadata': metadata,
                'success': False,
                'error': str(e)
            }
    
    def _load_pdf(self, path: Path) -> str:
        """Extrae texto de PDF usando pdfplumber (preferido) o PyPDF2."""
        
        # Intentar con pdfplumber primero (más robusto)
        if PDFPLUMBER_AVAILABLE:
            try:
                import pdfplumber
                text_parts = []
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                return '\n\n'.join(text_parts)
            except Exception as e:
                logger.warning(f"pdfplumber falló para {path.name}, intentando PyPDF2: {e}")
        
        # Fallback a PyPDF2
        if PDF_AVAILABLE:
            try:
                text_parts = []
                with open(path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                return '\n\n'.join(text_parts)
            except Exception as e:
                logger.error(f"PyPDF2 también falló: {e}")
                raise
        
        raise ImportError("No hay biblioteca PDF disponible. Instalar: pip install pdfplumber PyPDF2")
    
    def _load_text(self, path: Path) -> str:
        """Carga archivos de texto plano."""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise UnicodeDecodeError(f"No se pudo decodificar {path.name} con encodings: {encodings}")
    
    def _load_docx(self, path: Path) -> str:
        """Extrae texto de archivos DOCX."""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx no está instalado. Instalar: pip install python-docx")
        
        doc = Document(path)
        text_parts = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
        return '\n\n'.join(text_parts)
    
    def load_directory(self, directory_path: str, recursive: bool = True) -> List[Dict]:
        """
        Carga todos los archivos soportados de un directorio.
        
        Args:
            directory_path: Ruta al directorio
            recursive: Si buscar recursivamente en subdirectorios
            
        Returns:
            Lista de diccionarios con resultados de carga
        """
        results = []
        path = Path(directory_path)
        
        if not path.exists() or not path.is_dir():
            logger.error(f"Directorio no válido: {directory_path}")
            return results
        
        # Patrón de búsqueda
        pattern = '**/*' if recursive else '*'
        
        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                result = self.load_file(str(file_path))
                results.append(result)
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"Directorio procesado: {successful}/{len(results)} archivos exitosos")
        
        return results


# Función helper para uso directo
def load_file(file_path: str) -> Optional[Dict]:
    """Helper function para cargar un archivo directamente."""
    loader = FileLoader()
    return loader.load_file(file_path)


def load_directory(directory_path: str, recursive: bool = True) -> List[Dict]:
    """Helper function para cargar un directorio completo."""
    loader = FileLoader()
    return loader.load_directory(directory_path, recursive)
