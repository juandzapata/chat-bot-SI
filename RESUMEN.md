# RESUMEN EJECUTIVO - Chatbot RAG sobre IA y Regulación

## 🎯 Qué es el Proyecto
Chatbot especializado en Inteligencia Artificial, ética y regulación que responde preguntas usando **RAG (Retrieval-Augmented Generation)** con documentos oficiales de UNESCO, AI Act europeo, CONPES colombiano, IEEE, y normativas universitarias.

---

## 🏗️ Arquitectura Técnica

### **Stack Tecnológico**
- **Backend**: FastAPI (Python) - API REST
- **Base Vectorial**: ChromaDB con embeddings de Gemini (768 dimensiones)
- **LLMs**: Gemini (API) + LLaMA3 (local vía Ollama)
- **Infraestructura**: Docker + docker-compose
- **Frontend**: HTML/JS vanilla con toggles de configuración

### **Flujo RAG**
1. Usuario pregunta → FastAPI recibe request
2. ChromaDB busca top-k documentos relevantes (embeddings Gemini)
3. Contexto + pregunta → LLM (Gemini o LLaMA3)
4. Respuesta con citas verificables → Usuario

---

## 📊 Corpus de Documentos

### **39 documentos PDF + 1 PNG**
- **Colombia**: 2 documentos (CONPES, normativa nacional)
- **Internacional**: 32 documentos (UNESCO, AI Act, OECD, IEEE)
- **Universidad**: 5 PDFs + 1 PNG pendiente OCR

### **Procesamiento**
- **4,814 chunks** generados con overlap
- **Embeddings**: Gemini text-embedding-004
- **Metadata**: Categoría, título, descripción por documento
- **Chunking**: Máximo 1000 tokens por chunk con overlap de 200

---

## 🤖 Dual-LLM System

### **Gemini (API)**
- Modelo: gemini-1.5-flash
- Ventajas: Rápido, multimodal, contexto largo
- Uso: Producción principal

### **LLaMA3 (Open Source)**
- Modelo: llama3.2 vía Ollama
- Ventajas: Privacidad, sin costos API, local
- Uso: Comparación y fallback

### **Configuración del Usuario**
- Endpoint `/chat` acepta parámetro `model`: "gemini" o "llama3"
- Frontend con dropdown para seleccionar modelo

---

## 🎨 Modos de Respuesta

### **Brief (Breve)**
- Respuestas concisas de 2-3 párrafos
- Ideal para consultas rápidas
- Menos tokens, más económico

### **Extended (Extendido)**
- Respuestas detalladas con estructura formal
- Incluye antecedentes, análisis, conclusiones
- Citas explícitas con referencias

**Implementación**: Toggle en frontend + parámetro `response_mode` en API

---

## 🔍 Comandos Especiales

### `/fuentes`
Lista todos los documentos disponibles en el corpus con categorías (Colombia, Internacional, Universidad)

### `/politica`
Muestra política de uso del chatbot: limitaciones, fuentes confiables, disclaimer académico

**Endpoint**: `/sources` y `/policy` en FastAPI

---

## 🔒 Sistema de Logs Anonimizados

### **Técnicas de Privacidad**
1. **Regex Masking**: Emails → `[EMAIL_ANONIMIZADO]`, Teléfonos → `[TELEFONO_ANONIMIZADO]`, Nombres → `[NOMBRE_ANONIMIZADO]`
2. **SHA-256 Hashing**: Session IDs irreversibles (16 chars truncados)
3. **No se guarda**: IPs, user agents, datos identificables

### **Formato JSONL**
- `interactions_YYYYMMDD.jsonl`: Todas las conversaciones
- `errors_YYYYMMDD.jsonl`: Errores del sistema
- `system_YYYYMMDD.jsonl`: Eventos de inicio/apagado

### **Métricas Capturadas**
- Modelo usado, modo de respuesta, tiempo de respuesta
- Longitud de pregunta/respuesta, número de fuentes
- Distribución por hora, sesiones únicas

---

## 📈 Sistema de Evaluación

### **60 Preguntas Gold en 6 Categorías**
1. Aspectos generales de IA
2. Ética y responsabilidad
3. Regulación y normativa
4. Aplicaciones específicas
5. Riesgos y limitaciones
6. Futuro y tendencias

### **6 Métricas Automáticas**
1. **Exactitud**: Detección de keywords esperados
2. **Cobertura**: Documentos correctos recuperados
3. **Claridad**: Estructura y longitud adecuada
4. **Citas**: Referencias verificables presentes
5. **Alucinación**: Detección de información inventada
6. **Seguridad**: Disclaimers y limitaciones mencionados

### **Comparación Multi-Modelo**
Script `evaluate_gold_questions.py` ejecuta las 60 preguntas con:
- Gemini vs LLaMA3
- Brief vs Extended
- Diferentes valores de top-k

Genera reporte comparativo en JSON y Markdown

---

## 🐳 Docker: Por Qué y Cómo

### **Justificación Técnica**
1. **Reproducibilidad**: Mismo entorno en Mac, Linux, servidor producción
2. **Aislamiento**: ChromaDB y dependencias sin contaminar sistema
3. **Persistencia**: Volúmenes para vector_store y logs sobreviven a recreaciones
4. **Portabilidad**: Profesor/evaluador solo necesita `docker-compose up`
5. **Versionado**: Embeddings Gemini (768d) garantizados vs errores de instalación manual

### **Comandos Clave**
```bash
docker-compose up -d          # Levantar todo
docker-compose logs -f api    # Ver logs en tiempo real
docker-compose restart api    # Aplicar cambios de código
```

### **Volúmenes Críticos**
- `./data/vector_store`: 4,814 embeddings persistentes
- `./app/logs`: Logs anonimizados históricos
- `./data/corpus`: Documentos fuente

---

## ✅ Estado Actual (100% Completo)

### **Infraestructura (MLOps)**
✅ Docker reproducible con .env  
✅ Logs anonimizados con privacidad  
✅ Pipeline de evaluación automatizado  
⏳ Monitoreo de tokens/costo (pendiente)

### **LLMs**
✅ Gemini API integrado  
✅ LLaMA3 local integrado  
✅ 60 preguntas gold en 6 categorías  
✅ 6 métricas de evaluación  
✅ Comparación multi-modelo

### **RAG**
✅ ChromaDB operativo  
✅ 39 documentos confiables  
✅ Chunking optimizado  
✅ Búsqueda vectorial con parámetros ajustables  
✅ Citas verificables en respuestas

### **Frontend**
✅ Interfaz web funcional  
✅ Modos brief/extended  
✅ Mostrar fuentes y citas  
✅ Comandos `/fuentes` y `/politica`  
✅ Toggle modelo y modo sin recargar

---

## 🎓 Para la Sustentación

### **Puntos Clave a Mencionar**

1. **RAG > LLM Puro**: Reduce alucinaciones usando documentos oficiales como ground truth
2. **Dual-LLM**: Gemini para velocidad, LLaMA3 para privacidad/costos
3. **Privacidad by Design**: Logs útiles sin comprometer datos personales
4. **Evaluación Rigurosa**: 60 preguntas × 6 métricas = 360 puntos de validación
5. **Docker = Ciencia Reproducible**: Mismo ambiente en cualquier máquina

### **Posibles Preguntas del Profesor**

**¿Por qué ChromaDB y no Pinecone/Weaviate?**  
→ Open source, local, sin vendor lock-in, integración directa con embeddings Gemini

**¿Cómo garantizan la calidad de las respuestas?**  
→ Evaluación automatizada con 60 preguntas gold, 6 métricas cuantificables, comparación entre modelos

**¿Qué pasa con los datos de los usuarios?**  
→ Anonimización automática con regex + SHA-256, cumplimiento GDPR, solo métricas agregadas

**¿Por qué Gemini y LLaMA3 específicamente?**  
→ Gemini: API estable de Google, multimodal, contexto 1M tokens  
→ LLaMA3: Open source líder, ejecutable local, Meta respaldo

---

## 📏 Métricas del Sistema

- **Documentos**: 39 PDFs
- **Chunks**: 4,814 embeddings
- **Dimensiones**: 768 (Gemini)
- **Categorías**: 3 (Colombia, Internacional, Universidad)
- **Modelos**: 2 (Gemini + LLaMA3)
- **Modos**: 2 (Brief + Extended)
- **Preguntas gold**: 60 en 6 categorías
- **Métricas evaluación**: 6 automatizadas
- **Logs**: JSONL con privacidad garantizada

---

## 🚀 Próximos Pasos (Post-Evaluación)

1. Implementar monitoreo de tokens/costo con Google Cloud Billing API
2. Añadir OCR para `document_university_1.png`
3. Expandir corpus a 50+ documentos
4. Fine-tuning de LLaMA3 con conversaciones gold
5. API de feedback para mejorar respuestas
