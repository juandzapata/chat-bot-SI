# 📚 Instrucciones de Ingesta del Corpus - ChatBot IA Universidad de Caldas

## 🎯 Resumen

Este documento explica cómo usar el sistema de ingesta automatizada del corpus de documentos para el chatbot con arquitectura RAG.

## ✅ Estado Actual del Sistema

### Funcionalidades Implementadas

1. **FileLoader** (`app/rag/file_loader.py`)
   - Soporte para PDF, TXT, MD, DOCX
   - Extracción de texto robusta con múltiples bibliotecas
   - Manejo de errores y logging detallado

2. **Ingest All** (`app/rag/ingest_all.py`)
   - Lectura automática de `corpus_metadata.json`
   - Chunking inteligente de documentos (1000 chars con overlap de 200)
   - Métadatos completos preservados
   - Inserción batch en ChromaDB

3. **Endpoints FastAPI** (`app/main.py`)
   - `POST /ingest_all` - Ejecutar ingesta completa
   - `POST /chat` - Consultar con RAG
   - `GET /collection_stats` - Ver estadísticas
   - `POST /ingest_test` - Prueba básica

## 🚀 Uso del Sistema

### Opción 1: Vía API (Recomendado)

```bash
# 1. Levantar servicios con Docker
docker-compose up -d

# 2. Ejecutar ingesta via endpoint
curl -X POST http://localhost:9000/ingest_all

# 3. Verificar estadísticas
curl http://localhost:9000/collection_stats

# 4. Probar chat
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuál es la normativa sobre IA en Colombia?", "top_k": 3}'
```

### Opción 2: Ejecución Directa del Script

```bash
# Desde el directorio raíz del proyecto
cd /path/to/chat-bot-project

# Activar ambiente virtual (si aplica)
source venv/bin/activate  # o tu comando preferido

# Ejecutar ingesta
python -m app.rag.ingest_all
```

## 📂 Estructura del Corpus

El sistema espera la siguiente estructura:

```
data/
└── corpus/
    ├── corpus_metadata.json       # Metadatos de todos los documentos
    ├── colombia/
    │   └── document_colombia_1.pdf
    ├── international/
    │   └── document_international_1.pdf
    └── university/
        └── document_university_1.png  (actualmente no procesable sin OCR)
```

### Formato de corpus_metadata.json

```json
{
  "documentos_regulacion_ia": [
    {
      "id": "doc_unique_id",
      "titulo": "Título del documento",
      "organismo": "Fuente/Organismo",
      "anio": 2024,
      "categoria": "colombia|international|university",
      "ruta_archivo": "data/corpus/{categoria}/.pdf",
      "justificacion_breve": "Breve descripción",
      "fuentes_citadas": ["..."],
      "tema_clave": "Tema principal"
    }
  ]
}
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Modo de ejecución
MODE=development

# ChromaDB
CHROMA_HOST=chroma_db
CHROMA_PORT=8000

# FastAPI Backend
APP_HOST=0.0.0.0
APP_PORT=9000

# Gemini API
GEMINI_API_KEY=tu_api_key_aqui
```

### Dependencias

Ver `docker/requirements.txt`:

```
fastapi
uvicorn
chromadb
pydantic
python-dotenv
google-generativeai
PyPDF2
pdfplumber
python-docx
```

## 📊 Proceso de Ingesta

1. **Carga de Metadatos**: Lee `corpus_metadata.json`
2. **Construcción de Rutas**: Resuelve rutas de archivos desde metadata
3. **Extracción de Texto**: Usa FileLoader apropiado
4. **Chunking**: Divide en chunks de 1000 caracteres con overlap de 200
5. **Embeddings**: Genera embeddings con Gemini text-embedding-004
6. **Inserción**: Agrega a ChromaDB con metadatos completos

## 🎛️ Parámetros Configurables

En `app/rag/ingest_all.py`:

```python
CHUNK_SIZE = 1000      # Tamaño de chunks en caracteres
CHUNK_OVERLAP = 200    # Solapamiento entre chunks
COLLECTION_NAME = "documentos_ucaldas"
```

## 🧪 Pruebas

### Test Básico

```bash
# Test simple de ingesta
curl -X POST http://localhost:9000/ingest_test
```

### Test Completo

```bash
# Ingesta completa
curl -X POST http://localhost:9000/ingest_all | jq

# Verificar
curl http://localhost:9000/collection_stats | jq

# Probar chat
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué dice la normativa europea sobre IA?",
    "top_k": 3
  }' | jq
```

## 🔍 Monitoreo y Logs

Los logs se muestran en consola con niveles INFO y ERROR:

```
🚀 Iniciando ingesta del corpus completo...
✓ Metadatos cargados: 3 documentos
📄 Procesando: Ley de IA de la UE (doc_internacional_1)
  → Dividido en 45 chunks
✓ 45 chunks agregados exitosamente
✅ Ingesta completada
   Exitosos: 3/3
```

## 🐛 Solución de Problemas

### Error: "Archivo no encontrado"

Verificar que las rutas en `corpus_metadata.json` sean correctas y los archivos existan.

### Error: "No hay biblioteca PDF disponible"

```bash
pip install pdfplumber PyPDF2
```

### Error: ChromaDB connection

```bash
# Verificar que ChromaDB esté corriendo
docker-compose ps

# Reiniciar servicios
docker-compose restart
```

## 📝 Notas Importantes

1. **Imágenes**: Los archivos PNG/JPG requieren OCR (pytesseract) que NO está habilitado por defecto para evitar dependencias adicionales.
2. **Chunking**: El solapamiento asegura contexto en límites de chunks.
3. **Metadatos**: Todos los campos del JSON de metadata se preservan en cada chunk.
4. **Performance**: La inserción batch es más eficiente que inserts individuales.

## 🔮 Próximos Pasos

- [ ] Implementar OCR para imágenes con Tesseract
- [ ] Agregar endpoint de actualización incremental
- [ ] Webhook para notificaciones de ingesta
- [ ] Dashboard de monitoreo
- [ ] Métricas de calidad de chunks

## 📞 Soporte

Para problemas o preguntas, consultar la documentación principal en `README.md`.
