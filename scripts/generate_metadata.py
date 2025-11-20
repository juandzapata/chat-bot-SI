#!/usr/bin/env python3
"""
Script para generar automáticamente corpus_metadata.json
Lee todos los archivos del corpus y extrae información básica.
"""

import os
import json
from pathlib import Path

# Intentar importar PyPDF2, si no está disponible usar pypdf
try:
    from PyPDF2 import PdfReader
except ImportError:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("⚠️  PyPDF2 o pypdf no están instalados. Instalando...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'pypdf'])
        from pypdf import PdfReader

# Rutas
BASE_DIR = Path(__file__).parent.parent
CORPUS_DIR = BASE_DIR / "data" / "corpus"
OUTPUT_FILE = CORPUS_DIR / "corpus_metadata.json"

def extract_pdf_info(pdf_path):
    """Extrae título y primeras líneas de un PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            
            # Intentar obtener metadata
            metadata = pdf_reader.metadata
            title = metadata.get('/Title', '') if metadata else ''
            
            # Obtener primeras líneas del texto
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            
            # Limpiar y obtener primeras líneas
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            first_lines = lines[:5] if len(lines) >= 5 else lines
            
            return {
                'title': title,
                'first_lines': first_lines,
                'total_pages': len(pdf_reader.pages),
                'text_preview': ' '.join(first_lines[:2])[:200]
            }
    except Exception as e:
        print(f"Error leyendo {pdf_path}: {e}")
        return None

def extract_image_info(image_path):
    """Extrae información básica de una imagen"""
    try:
        return {
            'first_lines': [],
            'text_preview': f'Imagen: {image_path.name}'
        }
    except Exception as e:
        print(f"Error leyendo imagen {image_path}: {e}")
        return None

def scan_corpus():
    """Escanea todas las carpetas del corpus"""
    categories = {
        'colombia': [],
        'international': [],
        'university': []
    }
    
    for category_en, category_es in [
        ('colombia', 'colombia'),
        ('international', 'internacional'),
        ('university', 'universidad')
    ]:
        category_path = CORPUS_DIR / category_en
        
        if not category_path.exists():
            continue
        
        # Listar archivos
        files = sorted(category_path.glob('*'))
        
        for idx, file_path in enumerate(files, 1):
            if file_path.name.startswith('.'):
                continue
            
            # Determinar tipo de archivo
            ext = file_path.suffix.lower()
            
            if ext == '.pdf':
                info = extract_pdf_info(file_path)
            elif ext in ['.png', '.jpg', '.jpeg']:
                info = extract_image_info(file_path)
            else:
                continue
            
            if not info:
                continue
            
            # Generar ID basado en el nombre del archivo
            file_number = ''.join(filter(str.isdigit, file_path.stem))
            doc_id = f"doc_{category_es}_{file_number if file_number else idx}"
            
            # Crear entrada
            entry = {
                "id": doc_id,
                "titulo": info.get('title', '') or f"[COMPLETAR] Documento {category_es.capitalize()} {file_number or idx}",
                "organismo": "[COMPLETAR] Nombre del organismo",
                "anio": "[COMPLETAR] Año",
                "categoria": category_es,
                "ruta_archivo": f"data/corpus/{category_en}/{file_path.name}",
                "justificacion_breve": f"[COMPLETAR] Descripción breve. Preview: {info.get('text_preview', '')}",
                "fuentes_citadas": [
                    "[COMPLETAR] Fuente 1"
                ],
                "tema_clave": "[COMPLETAR] Tema principal"
            }
            
            # Agregar información adicional como comentario
            if info.get('first_lines'):
                entry['_primeras_lineas'] = info['first_lines']
            if info.get('total_pages'):
                entry['_total_paginas'] = info['total_pages']
            
            categories[category_en].append(entry)
            
            print(f"✓ {category_es}: {file_path.name} - {entry['id']}")
            if info.get('first_lines'):
                print(f"  Primeras líneas: {info['first_lines'][0][:100]}...")
    
    return categories

def generate_metadata():
    """Genera el archivo corpus_metadata.json"""
    print("🔍 Escaneando corpus...\n")
    
    categories = scan_corpus()
    
    # Combinar todas las categorías
    all_docs = []
    all_docs.extend(categories['colombia'])
    all_docs.extend(categories['international'])
    all_docs.extend(categories['university'])
    
    # Crear estructura final
    metadata = {
        "documentos_regulacion_ia": all_docs
    }
    
    # Guardar
    print(f"\n💾 Guardando en {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Completado!")
    print(f"   Total documentos: {len(all_docs)}")
    print(f"   - Colombia: {len(categories['colombia'])}")
    print(f"   - Internacional: {len(categories['international'])}")
    print(f"   - Universidad: {len(categories['university'])}")
    print(f"\n📝 Ahora edita {OUTPUT_FILE} y completa los campos marcados con [COMPLETAR]")

if __name__ == "__main__":
    generate_metadata()
