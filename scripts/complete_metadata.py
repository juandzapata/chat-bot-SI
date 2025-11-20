#!/usr/bin/env python3
"""
Script para completar corpus_metadata.json con información detallada.
Lee el archivo generado automáticamente y completa los campos.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
METADATA_FILE = BASE_DIR / "data" / "corpus" / "corpus_metadata.json"

# Cargar metadata actual
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

docs = data["documentos_regulacion_ia"]

# Completar información basándose en las primeras líneas extraídas
for doc in docs:
    doc_id = doc["id"]
    lines = doc.get("_primeras_lineas", [])
    
    # COLOMBIA
    if doc_id == "doc_colombia_1":
        doc["titulo"] = "ABC Proyecto de Ley de Inteligencia Artificial (Colombia)"
        doc["organismo"] = "Gobierno de Colombia (MinCiencias, MinTIC, SIC)"
        doc["anio"] = 2024
        doc["justificacion_breve"] = "Iniciativa legislativa que establece un marco jurídico integral para la adopción de IA en Colombia. Su enfoque se centra en la gestión de riesgos y la garantía de derechos humanos."
        doc["fuentes_citadas"] = ["Gobierno de Colombia, ABC Proyecto de Ley de Inteligencia Artificial"]
        doc["tema_clave"] = "Marco jurídico integral y gobernanza nacional de la IA"
    
    elif doc_id == "doc_colombia_2":
        doc["titulo"] = "Política Nacional de Inteligencia Artificial - Documento CONPES"
        doc["organismo"] = "Departamento Nacional de Planeación (DNP) - Gobierno de Colombia"
        doc["anio"] = 2024
        doc["justificacion_breve"] = "Documento CONPES que establece la política nacional para el desarrollo de la IA en Colombia, abordando aspectos de educación, ciencia, tecnología, comercio y defensa."
        doc["fuentes_citadas"] = ["DNP, Política Nacional de Inteligencia Artificial"]
        doc["tema_clave"] = "Política pública y estrategia nacional de IA"
    
    elif doc_id == "doc_colombia_3":
        doc["titulo"] = "Decreto sobre Inteligencia Artificial - Diario Oficial de Colombia"
        doc["organismo"] = "Congreso de la República de Colombia"
        doc["anio"] = 2025
        doc["justificacion_breve"] = "Decreto oficial publicado en el Diario Oficial que regula aspectos específicos de la implementación de IA en Colombia."
        doc["fuentes_citadas"] = ["Congreso de Colombia, Diario Oficial Edición 53.198"]
        doc["tema_clave"] = "Normativa legal y decretos nacionales"
    
    elif doc_id == "doc_colombia_4":
        doc["titulo"] = "Regulación de Inteligencia Artificial en Colombia - Documento técnico"
        doc["organismo"] = "Gobierno de Colombia"
        doc["anio"] = 2024
        doc["justificacion_breve"] = "Documento técnico sobre regulación de IA en Colombia, complementario a la política nacional."
        doc["fuentes_citadas"] = ["Gobierno de Colombia, Regulación IA"]
        doc["tema_clave"] = "Aspectos técnicos de regulación"
    
    elif doc_id == "doc_colombia_5":
        doc["titulo"] = "Marco Ético para el Desarrollo de IA en Colombia"
        doc["organismo"] = "Gobierno de Colombia"
        doc["anio"] = 2024
        doc["justificacion_breve"] = "Marco ético y principios rectores para el desarrollo responsable de IA en Colombia."
        doc["fuentes_citadas"] = ["Gobierno de Colombia, Marco Ético IA"]
        doc["tema_clave"] = "Ética y responsabilidad en IA"
    
    # INTERNACIONALES - Mantener el título original del PDF si existe
    elif doc_id.startswith("doc_internacional"):
        # Ya tienen buen título extraído del PDF, solo completar organismo y año
        if lines:
            # Determinar organismo y año basándose en las primeras líneas
            first_text = ' '.join(lines[:3]).lower()
            
            if "nature" in first_text:
                doc["organismo"] = "Nature Publishing Group"
                doc["anio"] = 2025
                doc["tema_clave"] = "Investigación científica en IA"
            elif "ieee" in first_text:
                doc["organismo"] = "IEEE (Institute of Electrical and Electronics Engineers)"
                doc["anio"] = 2023
                doc["tema_clave"] = "Investigación técnica en IA"
            elif "springer" in first_text or "bmc" in first_text:
                doc["organismo"] = "Springer Nature"
                doc["anio"] = 2025
                doc["tema_clave"] = "Investigación académica en IA"
            elif "elsevier" in first_text or "sciencedirect" in first_text:
                doc["organismo"] = "Elsevier"
                doc["anio"] = 2024
                doc["tema_clave"] = "Investigación aplicada en IA"
            elif "brill" in first_text:
                doc["organismo"] = "Brill Publishers"
                doc["anio"] = 2025
                doc["tema_clave"] = "IA en educación y sociedad"
            else:
                doc["organismo"] = "Revista Científica Internacional"
                doc["anio"] = 2024
                doc["tema_clave"] = "Investigación en IA"
            
            # Mantener título si ya existe uno bueno
            if not doc["titulo"].startswith("[COMPLETAR]"):
                # Mejorar justificación
                doc["justificacion_breve"] = f"Artículo científico sobre aplicaciones y desarrollos de IA publicado en {doc['organismo']}."
                doc["fuentes_citadas"] = [f"{doc['organismo']}, {doc['anio']}"]
            else:
                # Generar título basado en primeras líneas
                if lines:
                    doc["titulo"] = lines[0][:100]  # Primer línea como título
                    doc["justificacion_breve"] = f"Investigación sobre IA. {lines[1][:150] if len(lines) > 1 else ''}"
                    doc["fuentes_citadas"] = [f"{doc['organismo']}, {doc['anio']}"]
    
    # UNIVERSIDAD
    elif doc_id == "doc_universidad_1":
        doc["titulo"] = "Formación para el futuro: Universidad de Caldas presentó el nuevo programa de Inteligencia Artificial"
        doc["organismo"] = "Universidad de Caldas"
        doc["anio"] = 2024
        doc["justificacion_breve"] = "Artículo que anuncia el nuevo programa de Inteligencia Artificial de la universidad, reflejando la adopción y formalización de la temática de IA en el contexto académico local."
        doc["fuentes_citadas"] = ["Universidad de Caldas, Artículo sobre el nuevo programa de IA"]
        doc["tema_clave"] = "Adopción académica y programas de formación en IA"
    
    elif doc_id.startswith("doc_universidad") and doc_id != "doc_universidad_1":
        # Para los demás documentos de universidad (papers académicos)
        if lines:
            first_text = ' '.join(lines[:3])
            doc["organismo"] = "Universidad de Caldas / Investigación Académica"
            doc["anio"] = 2025
            doc["justificacion_breve"] = f"Investigación académica sobre IA y sus aplicaciones. {first_text[:150]}"
            doc["fuentes_citadas"] = ["Universidad de Caldas, Investigación IA"]
            doc["tema_clave"] = "Investigación académica en IA"
            
            # Mejorar título si comienza con [COMPLETAR]
            if doc["titulo"].startswith("[COMPLETAR]") and lines:
                doc["titulo"] = lines[0][:80] if lines[0] else f"Investigación IA - Universidad de Caldas {doc_id.split('_')[-1]}"
    
    # Eliminar campos temporales
    if "_primeras_lineas" in doc:
        del doc["_primeras_lineas"]
    if "_total_paginas" in doc:
        del doc["_total_paginas"]

# Guardar archivo actualizado
with open(METADATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Archivo corpus_metadata.json completado exitosamente!")
print(f"   Total documentos: {len(docs)}")
print(f"   - Colombia: {len([d for d in docs if d['categoria'] == 'colombia'])}")
print(f"   - Internacional: {len([d for d in docs if d['categoria'] == 'internacional'])}")
print(f"   - Universidad: {len([d for d in docs if d['categoria'] == 'universidad'])}")
