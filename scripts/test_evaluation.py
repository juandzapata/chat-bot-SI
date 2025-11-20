#!/usr/bin/env python3
"""
Script de Prueba Rápida - Evaluación Reducida
Evalúa solo 5 preguntas (1 por categoría) para verificación
"""

import json
import requests
import time
from pathlib import Path

API_BASE_URL = "http://localhost:9000"
GOLD_DATASET_PATH = Path("data/evaluation/questions_gold.json")

def test_evaluation():
    print("=" * 70)
    print("🧪 PRUEBA RÁPIDA DE EVALUACIÓN (5 preguntas)")
    print("=" * 70)
    print()
    
    # Cargar dataset
    with open(GOLD_DATASET_PATH, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Seleccionar 1 pregunta de cada categoría
    categories = {}
    for q in dataset['questions']:
        cat = q['category']
        if cat not in categories:
            categories[cat] = q
        if len(categories) == 5:
            break
    
    test_questions = list(categories.values())
    
    print(f"📚 Probando {len(test_questions)} preguntas:\n")
    
    results = []
    for idx, q in enumerate(test_questions, 1):
        print(f"[{idx}/5] ID #{q['id']} - {q['category']}")
        print(f"  ❓ {q['question']}")
        
        # Query chatbot
        start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"question": q['question'], "top_k": 3},
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.ok:
            data = response.json()
            answer = data.get('answer', '')
            sources = data.get('sources', [])
            
            # Calcular cobertura
            expected_docs = q.get('source_documents', [])
            retrieved_docs = set()
            
            for source in sources:
                file_path = source.get('file_path', '')
                if file_path:
                    file_name = file_path.split('/')[-1]
                    if file_name in expected_docs:
                        retrieved_docs.add(file_name)
            
            cobertura = int((len(retrieved_docs) / len(expected_docs)) * 100) if expected_docs else 100
            
            # Calcular exactitud (keywords)
            keywords = q.get('expected_keywords', [])
            answer_lower = answer.lower()
            matches = sum(1 for kw in keywords if kw.lower() in answer_lower)
            exactitud = int((matches / len(keywords)) * 100) if keywords else 100
            
            print(f"  ✅ Respuesta recibida ({len(answer)} chars)")
            print(f"  📊 Exactitud: {exactitud}/100 ({matches}/{len(keywords)} keywords)")
            print(f"  📚 Cobertura: {cobertura}/100 ({len(retrieved_docs)}/{len(expected_docs)} docs)")
            print(f"  🔍 Docs esperados: {expected_docs}")
            print(f"  🔍 Docs recuperados: {[s.get('file_path', '').split('/')[-1] for s in sources]}")
            print(f"  ⏱️  Tiempo: {elapsed:.2f}s\n")
            
            results.append({
                'id': q['id'],
                'category': q['category'],
                'exactitud': exactitud,
                'cobertura': cobertura,
                'time': elapsed
            })
        else:
            print(f"  ❌ Error: {response.status_code}\n")
    
    # Resumen
    print("=" * 70)
    print("📊 RESUMEN DE PRUEBA")
    print("=" * 70)
    
    if results:
        avg_exactitud = sum(r['exactitud'] for r in results) / len(results)
        avg_cobertura = sum(r['cobertura'] for r in results) / len(results)
        avg_time = sum(r['time'] for r in results) / len(results)
        
        print(f"\nPreguntas probadas: {len(results)}")
        print(f"Exactitud promedio: {avg_exactitud:.1f}/100")
        print(f"Cobertura promedio: {avg_cobertura:.1f}/100")
        print(f"Tiempo promedio: {avg_time:.2f}s")
        print()
        
        print("Por categoría:")
        for r in results:
            print(f"  • {r['category']}: Exactitud={r['exactitud']}, Cobertura={r['cobertura']}")
        print()
        
        if avg_cobertura > 0:
            print("✅ COBERTURA FUNCIONANDO - El fix fue exitoso!")
        else:
            print("❌ COBERTURA SIGUE EN 0 - Revisar implementación")
    
    print("=" * 70)

if __name__ == "__main__":
    test_evaluation()
