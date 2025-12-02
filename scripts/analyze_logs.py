#!/usr/bin/env python3
"""
Script para analizar logs anonimizados del chatbot
Genera estadísticas y reportes de uso
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any
import statistics

LOGS_DIR = Path("logs")


def load_interactions(date: str = None) -> List[Dict]:
    """Carga interacciones de un día específico o el más reciente"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    interactions_file = LOGS_DIR / f"interactions_{date}.jsonl"
    
    if not interactions_file.exists():
        print(f"❌ No se encontró archivo de interacciones para {date}")
        return []
    
    interactions = []
    with open(interactions_file, 'r', encoding='utf-8') as f:
        for line in f:
            interactions.append(json.loads(line))
    
    return interactions


def analyze_interactions(interactions: List[Dict]) -> Dict[str, Any]:
    """Analiza las interacciones y genera estadísticas"""
    if not interactions:
        return {"error": "No hay interacciones para analizar"}
    
    # Métricas básicas
    total = len(interactions)
    
    # Por modelo
    models = Counter(i['model'] for i in interactions)
    
    # Por modo de respuesta
    modes = Counter(i['response_mode'] for i in interactions)
    
    # Tiempos de respuesta
    response_times = [i['response_time_seconds'] for i in interactions]
    
    # Longitudes
    question_lengths = [i['question_length'] for i in interactions]
    answer_lengths = [i['answer_length'] for i in interactions]
    
    # Fuentes consultadas
    sources_counts = [i['sources_count'] for i in interactions]
    
    # Sesiones únicas
    unique_sessions = len(set(i['session_id'] for i in interactions))
    
    # Estadísticas por hora
    hours = defaultdict(int)
    for i in interactions:
        hour = datetime.fromisoformat(i['timestamp']).hour
        hours[hour] += 1
    
    return {
        "total_interactions": total,
        "unique_sessions": unique_sessions,
        "by_model": dict(models),
        "by_response_mode": dict(modes),
        "response_times": {
            "min": round(min(response_times), 2),
            "max": round(max(response_times), 2),
            "avg": round(statistics.mean(response_times), 2),
            "median": round(statistics.median(response_times), 2)
        },
        "question_lengths": {
            "min": min(question_lengths),
            "max": max(question_lengths),
            "avg": round(statistics.mean(question_lengths), 1)
        },
        "answer_lengths": {
            "min": min(answer_lengths),
            "max": max(answer_lengths),
            "avg": round(statistics.mean(answer_lengths), 1)
        },
        "sources_consulted": {
            "min": min(sources_counts),
            "max": max(sources_counts),
            "avg": round(statistics.mean(sources_counts), 1)
        },
        "usage_by_hour": dict(sorted(hours.items()))
    }


def generate_report(date: str = None):
    """Genera reporte de análisis de logs"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print("=" * 70)
    print(f"📊 ANÁLISIS DE LOGS ANONIMIZADOS - {date}")
    print("=" * 70)
    print()
    
    interactions = load_interactions(date)
    
    if not interactions:
        print("No hay datos para analizar")
        return
    
    stats = analyze_interactions(interactions)
    
    print(f"📈 Métricas Generales")
    print(f"   Total interacciones: {stats['total_interactions']}")
    print(f"   Sesiones únicas: {stats['unique_sessions']}")
    print()
    
    print(f"🤖 Por Modelo")
    for model, count in stats['by_model'].items():
        pct = (count / stats['total_interactions']) * 100
        print(f"   {model}: {count} ({pct:.1f}%)")
    print()
    
    print(f"📝 Por Modo de Respuesta")
    for mode, count in stats['by_response_mode'].items():
        pct = (count / stats['total_interactions']) * 100
        print(f"   {mode}: {count} ({pct:.1f}%)")
    print()
    
    print(f"⏱️  Tiempos de Respuesta (segundos)")
    print(f"   Mínimo: {stats['response_times']['min']}s")
    print(f"   Máximo: {stats['response_times']['max']}s")
    print(f"   Promedio: {stats['response_times']['avg']}s")
    print(f"   Mediana: {stats['response_times']['median']}s")
    print()
    
    print(f"📏 Longitudes")
    print(f"   Preguntas (caracteres):")
    print(f"      Min: {stats['question_lengths']['min']}, Max: {stats['question_lengths']['max']}, Avg: {stats['question_lengths']['avg']}")
    print(f"   Respuestas (caracteres):")
    print(f"      Min: {stats['answer_lengths']['min']}, Max: {stats['answer_lengths']['max']}, Avg: {stats['answer_lengths']['avg']}")
    print()
    
    print(f"📚 Fuentes Consultadas")
    print(f"   Min: {stats['sources_consulted']['min']}, Max: {stats['sources_consulted']['max']}, Avg: {stats['sources_consulted']['avg']}")
    print()
    
    print(f"🕐 Uso por Hora")
    for hour, count in stats['usage_by_hour'].items():
        bar = "█" * count
        print(f"   {hour:02d}:00 - {bar} ({count})")
    print()
    
    print("=" * 70)
    
    # Guardar reporte
    report_file = LOGS_DIR / f"analysis_report_{date}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Reporte guardado en: {report_file}")


if __name__ == "__main__":
    import sys
    
    date = sys.argv[1] if len(sys.argv) > 1 else None
    generate_report(date)
