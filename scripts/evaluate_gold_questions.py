#!/usr/bin/env python3
"""
Script de Evaluación Automatizada - ChatBot IA Universidad de Caldas
Pipeline: Gold Dataset → Chatbot → Métricas → Almacenamiento

Métricas evaluadas (0-100):
- Exactitud: Presencia de keywords esperados en la respuesta
- Cobertura: Documentos fuente correctos recuperados
- Claridad: Longitud y estructura de la respuesta
- Citas: Correcta citación de fuentes
- Alucinación: Detección de información no soportada por fuentes
- Seguridad: Ausencia de disclaimers incorrectos o información peligrosa
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys

# Configuración
API_BASE_URL = "http://localhost:9000"
GOLD_DATASET_PATH = Path("data/evaluation/questions_gold.json")
RESULTS_DIR = Path("data/evaluation/results")


class ChatbotEvaluator:
    """Evaluador automatizado del chatbot con 6 métricas principales"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def load_gold_dataset(self) -> Dict[str, Any]:
        """Carga el dataset de preguntas gold"""
        print(f"📚 Cargando dataset gold desde: {GOLD_DATASET_PATH}")
        with open(GOLD_DATASET_PATH, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        print(f"✅ Dataset cargado: {dataset['metadata']['total_questions']} preguntas\n")
        return dataset
    
    def query_chatbot(self, question: str, model: str = "gemini", top_k: int = 3) -> Dict[str, Any]:
        """Realiza una consulta al chatbot"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json={"question": question, "model": model, "top_k": top_k},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def calculate_exactitud(self, answer: str, expected_keywords: List[str]) -> int:
        """
        Métrica 1: Exactitud (0-100)
        Calcula el porcentaje de keywords esperados presentes en la respuesta
        """
        if not expected_keywords:
            return 100
        
        answer_lower = answer.lower()
        matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
        score = int((matches / len(expected_keywords)) * 100)
        return score
    
    def calculate_cobertura(self, retrieved_sources: List[Dict], expected_docs: List[str]) -> int:
        """
        Métrica 2: Cobertura (0-100)
        Evalúa si los documentos recuperados coinciden con los esperados
        """
        if not expected_docs:
            return 100
        
        # Extraer nombres de archivos de las fuentes recuperadas
        retrieved_docs = set()
        for source in retrieved_sources:
            file_path = source.get('file_path', '')
            if file_path:
                # Extraer solo el nombre del archivo de la ruta completa
                file_name = file_path.split('/')[-1]  # Ej: document_international_16.pdf
                
                # Comparar con cada documento esperado
                for expected_doc in expected_docs:
                    if file_name == expected_doc:
                        retrieved_docs.add(expected_doc)
                        break
        
        # Calcular intersección
        matches = len(retrieved_docs)
        score = int((matches / len(expected_docs)) * 100)
        return score
    
    def calculate_claridad(self, answer: str) -> int:
        """
        Métrica 3: Claridad (0-100)
        Evalúa la longitud y estructura de la respuesta
        - Muy corta (<50 chars): penalización
        - Muy larga (>2000 chars): penalización leve
        - Óptimo: 200-1000 caracteres
        """
        length = len(answer)
        
        if length < 50:
            # Respuesta muy corta
            score = int((length / 50) * 50)  # Máximo 50 puntos
        elif length < 200:
            # Respuesta corta pero aceptable
            score = 50 + int(((length - 50) / 150) * 30)  # 50-80 puntos
        elif length <= 1000:
            # Rango óptimo
            score = 90
        elif length <= 2000:
            # Respuesta larga pero aceptable
            score = 85
        else:
            # Respuesta muy larga
            score = 70
        
        # Bonus: contiene párrafos (saltos de línea)
        if '\n' in answer:
            score = min(100, score + 10)
        
        return score
    
    def calculate_citas(self, answer: str, sources: List[Dict]) -> int:
        """
        Métrica 4: Citas (0-100)
        Evalúa si la respuesta cita correctamente las fuentes
        """
        if not sources:
            # Si no hay fuentes, verificar que la respuesta lo indique
            if "no tengo información" in answer.lower() or "no puedo" in answer.lower():
                return 100
            return 50  # Respuesta sin fuentes pero no lo indica claramente
        
        score = 0
        
        # Verificar que menciona "basándote" o "según"
        if any(keyword in answer.lower() for keyword in ["basándote", "basándome", "según", "de acuerdo"]):
            score += 40
        
        # Verificar que NO inventa fuentes
        if "fuente:" not in answer.lower() and "referencia:" not in answer.lower():
            score += 30  # Bien, no está inventando formato de citas
        
        # Verificar que tiene contexto de los documentos
        source_names = [s.get('title', '') + s.get('source', '') for s in sources]
        has_context = any(any(word in answer.lower() for word in name.lower().split()[:3]) 
                         for name in source_names if name)
        if has_context:
            score += 30
        
        return min(100, score)
    
    def calculate_alucinacion(self, answer: str, sources: List[Dict]) -> int:
        """
        Métrica 5: Alucinación (0-100)
        Detecta si la respuesta contiene información no soportada
        100 = sin alucinaciones, 0 = alta alucinación
        """
        score = 100
        
        # Penalización: menciona "basándote ÚNICAMENTE" pero luego añade info no pedida
        if "únicamente" in answer.lower() and len(answer) > 1500:
            score -= 10
        
        # Penalización: usa números específicos sin fuentes (posible invención)
        import re
        numbers = re.findall(r'\b\d+%\b|\b\d+\.\d+\b', answer)
        if len(numbers) > 3:  # Muchos números específicos
            score -= 15
        
        # Penalización: menciona fuentes que no existen en el corpus
        hallucination_phrases = [
            "según estudios recientes",
            "investigaciones demuestran",
            "se ha comprobado que",
            "expertos afirman"
        ]
        if any(phrase in answer.lower() for phrase in hallucination_phrases) and not sources:
            score -= 30
        
        # Bonus: usa lenguaje cauteloso
        cautious_phrases = ["puede", "podría", "es posible", "sugiere", "indica"]
        if any(phrase in answer.lower() for phrase in cautious_phrases):
            score = min(100, score + 10)
        
        return max(0, score)
    
    def calculate_seguridad(self, answer: str, question: str) -> int:
        """
        Métrica 6: Seguridad (0-100)
        Verifica que la respuesta no contenga información peligrosa o disclaimers incorrectos
        """
        score = 100
        
        # Penalización: da consejos médicos/legales sin disclaimer
        medical_legal_keywords = ["diagnóstico", "tratamiento", "medicamento", "ley dice", "legal"]
        has_sensitive = any(keyword in question.lower() for keyword in medical_legal_keywords)
        
        if has_sensitive:
            # Verificar que incluya disclaimer apropiado
            disclaimers = [
                "no sustituye",
                "consulta a un profesional",
                "asesoría profesional",
                "no es asesoría legal",
                "no soy un profesional"
            ]
            has_disclaimer = any(d in answer.lower() for d in disclaimers)
            if not has_disclaimer:
                score -= 40
        
        # Penalización: proporciona información falsa como verdadera
        if "definitivamente" in answer.lower() or "siempre es" in answer.lower():
            score -= 10
        
        # Penalización: no indica limitaciones cuando debería
        if len(answer) > 500 and "no puedo" not in answer.lower() and "limitaciones" not in answer.lower():
            score -= 5
        
        return max(0, score)
    
    def evaluate_question(self, question_data: Dict[str, Any], model: str, index: int, total: int) -> Dict[str, Any]:
        """Evalúa una pregunta individual con todas las métricas"""
        question_id = question_data['id']
        question = question_data['question']
        category = question_data['category']
        difficulty = question_data['difficulty']
        expected_keywords = question_data.get('expected_keywords', [])
        expected_docs = question_data.get('source_documents', [])
        
        print(f"[{index}/{total}] Evaluando pregunta #{question_id} ({category} - {difficulty}) - Modelo: {model}")
        print(f"  ❓ {question}")
        
        # 1. Query al chatbot
        start_time = time.time()
        response = self.query_chatbot(question, model=model)
        response_time = time.time() - start_time
        
        # Verificar error
        if "error" in response:
            print(f"  ❌ Error: {response['error']}\n")
            return {
                "question_id": question_id,
                "question": question,
                "category": category,
                "difficulty": difficulty,
                "model": model,
                "error": response['error'],
                "response_time": response_time,
                "scores": {
                    "exactitud": 0,
                    "cobertura": 0,
                    "claridad": 0,
                    "citas": 0,
                    "alucinacion": 0,
                    "seguridad": 0,
                    "total": 0
                }
            }
        
        answer = response.get('answer', '')
        sources = response.get('sources', [])
        
        # 2. Calcular métricas
        exactitud = self.calculate_exactitud(answer, expected_keywords)
        cobertura = self.calculate_cobertura(sources, expected_docs)
        claridad = self.calculate_claridad(answer)
        citas = self.calculate_citas(answer, sources)
        alucinacion = self.calculate_alucinacion(answer, sources)
        seguridad = self.calculate_seguridad(answer, question)
        
        # Score total (promedio de todas las métricas)
        total_score = int((exactitud + cobertura + claridad + citas + alucinacion + seguridad) / 6)
        
        # Mostrar resultados
        print(f"  📊 Scores: Exactitud={exactitud}, Cobertura={cobertura}, Claridad={claridad}")
        print(f"            Citas={citas}, Alucinación={alucinacion}, Seguridad={seguridad}")
        print(f"  🎯 Total: {total_score}/100")
        print(f"  ⏱️  Tiempo: {response_time:.2f}s\n")
        
        return {
            "question_id": question_id,
            "question": question,
            "category": category,
            "difficulty": difficulty,
            "model": model,
            "answer": answer,
            "sources": sources,
            "expected_keywords": expected_keywords,
            "expected_documents": expected_docs,
            "response_time": response_time,
            "scores": {
                "exactitud": exactitud,
                "cobertura": cobertura,
                "claridad": claridad,
                "citas": citas,
                "alucinacion": alucinacion,
                "seguridad": seguridad,
                "total": total_score
            }
        }
    
    def run_evaluation(self, models: List[str] = None):
        """Ejecuta la evaluación completa para uno o más modelos"""
        if models is None:
            models = ["gemini", "llama3"]
        
        print("=" * 70)
        print("🚀 INICIANDO EVALUACIÓN AUTOMATIZADA DEL CHATBOT")
        print(f"📋 Modelos a evaluar: {', '.join(models)}")
        print("=" * 70)
        print()
        
        # Cargar dataset
        dataset = self.load_gold_dataset()
        questions = dataset['questions']
        
        # Verificar API
        print("🔍 Verificando conectividad con el chatbot...")
        try:
            health = requests.get(f"{API_BASE_URL}/", timeout=5)
            health.raise_for_status()
            print("✅ Chatbot disponible\n")
        except Exception as e:
            print(f"❌ Error: No se puede conectar al chatbot en {API_BASE_URL}")
            print(f"   Asegúrate de que el servidor esté corriendo: docker-compose up -d\n")
            sys.exit(1)
        
        # Evaluar cada pregunta con cada modelo
        self.start_time = datetime.now()
        total_questions = len(questions)
        
        for model in models:
            print(f"\n{'='*70}")
            print(f"🤖 EVALUANDO MODELO: {model.upper()}")
            print(f"{'='*70}\n")
            
            for idx, question_data in enumerate(questions, 1):
                result = self.evaluate_question(question_data, model, idx, total_questions)
                self.results.append(result)
                
                # Pequeña pausa para no saturar
                time.sleep(0.5)
        
        self.end_time = datetime.now()
        
        # Guardar y generar reportes
        self.save_results()
        self.generate_summary()
    
    def save_results(self):
        """Guarda los resultados en JSON"""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = self.start_time.strftime("%Y_%m_%d_%H_%M")
        results_file = RESULTS_DIR / f"run_{timestamp}.json"
        
        output = {
            "metadata": {
                "execution_date": self.start_time.isoformat(),
                "total_questions": len(self.results),
                "duration_seconds": (self.end_time - self.start_time).total_seconds(),
                "api_base_url": API_BASE_URL
            },
            "results": self.results,
            "summary": self.calculate_summary_stats()
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados guardados en: {results_file}")
    
    def calculate_summary_stats(self) -> Dict[str, Any]:
        """Calcula estadísticas agregadas por modelo"""
        total = len(self.results)
        errors = sum(1 for r in self.results if 'error' in r)
        successful = total - errors
        
        if successful == 0:
            return {"error": "No se completó ninguna pregunta exitosamente"}
        
        # Agrupar por modelo
        models_data = {}
        for result in self.results:
            if 'error' in result:
                continue
            model = result.get('model', 'unknown')
            if model not in models_data:
                models_data[model] = []
            models_data[model].append(result)
        
        # Calcular estadísticas por modelo
        model_stats = {}
        for model, results in models_data.items():
            n = len(results)
            
            # Promedios por métrica
            avg_exactitud = sum(r['scores']['exactitud'] for r in results) / n
            avg_cobertura = sum(r['scores']['cobertura'] for r in results) / n
            avg_claridad = sum(r['scores']['claridad'] for r in results) / n
            avg_citas = sum(r['scores']['citas'] for r in results) / n
            avg_alucinacion = sum(r['scores']['alucinacion'] for r in results) / n
            avg_seguridad = sum(r['scores']['seguridad'] for r in results) / n
            avg_total = sum(r['scores']['total'] for r in results) / n
            
            # Por categoría
            categories = {}
            for result in results:
                cat = result['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(result['scores']['total'])
            
            category_avg = {cat: sum(scores) / len(scores) for cat, scores in categories.items()}
            
            # Por dificultad
            difficulties = {}
            for result in results:
                diff = result['difficulty']
                if diff not in difficulties:
                    difficulties[diff] = []
                difficulties[diff].append(result['scores']['total'])
            
            difficulty_avg = {diff: sum(scores) / len(scores) for diff, scores in difficulties.items()}
            
            model_stats[model] = {
                "total_questions": n,
                "average_scores": {
                    "exactitud": round(avg_exactitud, 2),
                    "cobertura": round(avg_cobertura, 2),
                    "claridad": round(avg_claridad, 2),
                    "citas": round(avg_citas, 2),
                    "alucinacion": round(avg_alucinacion, 2),
                    "seguridad": round(avg_seguridad, 2),
                    "total": round(avg_total, 2)
                },
                "by_category": {cat: round(avg, 2) for cat, avg in category_avg.items()},
                "by_difficulty": {diff: round(avg, 2) for diff, avg in difficulty_avg.items()},
                "avg_response_time": round(sum(r['response_time'] for r in results) / n, 2)
            }
        
        # Estadísticas generales
        avg_total_all = sum(r['scores']['total'] for r in self.results if 'error' not in r) / successful
        
        return {
            "total_questions": total,
            "successful": successful,
            "errors": errors,
            "overall_average": round(avg_total_all, 2),
            "by_model": model_stats
        }
    
    def generate_summary(self):
        """Genera resumen en consola y archivo Markdown con comparación de modelos"""
        summary = self.calculate_summary_stats()
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE EVALUACIÓN")
        print("=" * 70)
        print()
        print(f"Total preguntas: {summary['total_questions']}")
        print(f"Exitosas: {summary['successful']}")
        print(f"Errores: {summary['errors']}")
        print(f"Promedio general: {summary['overall_average']}/100")
        print()
        
        # Comparación por modelo
        print("=" * 70)
        print("🤖 COMPARACIÓN DE MODELOS")
        print("=" * 70)
        
        for model, stats in summary['by_model'].items():
            print(f"\n📌 {model.upper()}")
            print(f"   Preguntas: {stats['total_questions']}")
            print(f"   Tiempo promedio: {stats['avg_response_time']}s")
            print(f"   SCORES PROMEDIO:")
            print(f"     • Exactitud:     {stats['average_scores']['exactitud']}")
            print(f"     • Cobertura:     {stats['average_scores']['cobertura']}")
            print(f"     • Claridad:      {stats['average_scores']['claridad']}")
            print(f"     • Citas:         {stats['average_scores']['citas']}")
            print(f"     • Alucinación:   {stats['average_scores']['alucinacion']}")
            print(f"     • Seguridad:     {stats['average_scores']['seguridad']}")
            print(f"     • 🎯 TOTAL:      {stats['average_scores']['total']}/100")
        
        print("\n" + "=" * 70)
        
        # Generar archivo Markdown
        timestamp = self.start_time.strftime("%Y_%m_%d")
        md_file = RESULTS_DIR / f"summary_{timestamp}.md"
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 Resumen de Evaluación Comparativa - {self.start_time.strftime('%d/%m/%Y %H:%M')}\n\n")
            
            f.write("## Métricas Generales\n\n")
            f.write(f"- **Total preguntas:** {summary['total_questions']}\n")
            f.write(f"- **Exitosas:** {summary['successful']}\n")
            f.write(f"- **Errores:** {summary['errors']}\n")
            f.write(f"- **Promedio general:** {summary['overall_average']}/100\n\n")
            
            f.write("## 🤖 Comparación de Modelos\n\n")
            
            # Tabla comparativa
            f.write("### Scores Promedio por Modelo\n\n")
            f.write("| Métrica | " + " | ".join(summary['by_model'].keys()) + " |\n")
            f.write("|" + "---|" * (len(summary['by_model']) + 1) + "\n")
            
            metrics = ['exactitud', 'cobertura', 'claridad', 'citas', 'alucinacion', 'seguridad', 'total']
            metric_names = {
                'exactitud': 'Exactitud',
                'cobertura': 'Cobertura',
                'claridad': 'Claridad',
                'citas': 'Citas',
                'alucinacion': 'Alucinación',
                'seguridad': 'Seguridad',
                'total': '**TOTAL**'
            }
            
            for metric in metrics:
                row = f"| {metric_names[metric]} |"
                for model_stats in summary['by_model'].values():
                    score = model_stats['average_scores'][metric]
                    row += f" {score} |"
                f.write(row + "\n")
            
            # Tiempo de respuesta
            f.write("\n### Tiempo de Respuesta Promedio\n\n")
            f.write("| Modelo | Tiempo (s) |\n")
            f.write("|---|---|\n")
            for model, stats in summary['by_model'].items():
                f.write(f"| {model} | {stats['avg_response_time']} |\n")
            
            # Detalles por modelo
            for model, stats in summary['by_model'].items():
                f.write(f"\n## 📌 Detalles: {model.upper()}\n\n")
                
                f.write("### Por Categoría\n\n")
                f.write("| Categoría | Score |\n")
                f.write("|---|---|\n")
                for cat, score in stats['by_category'].items():
                    f.write(f"| {cat} | {score} |\n")
                
                f.write("\n### Por Dificultad\n\n")
                f.write("| Dificultad | Score |\n")
                f.write("|---|---|\n")
                for diff, score in stats['by_difficulty'].items():
                    f.write(f"| {diff} | {score} |\n")
        
        print(f"📄 Resumen Markdown guardado en: {md_file}")
        print("=" * 70)


if __name__ == "__main__":
    evaluator = ChatbotEvaluator()
    evaluator.run_evaluation()
