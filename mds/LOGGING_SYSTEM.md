# 📝 Sistema de Logs Anonimizados

## Descripción

Sistema de logging que registra todas las interacciones con el chatbot **protegiendo la privacidad del usuario** mediante anonimización automática de datos sensibles.

## 🔒 Datos Anonimizados

El sistema detecta y reemplaza automáticamente:

| Tipo | Patrón | Reemplazo |
|------|--------|-----------|
| **Emails** | `juan@example.com` | `[EMAIL_ANONIMIZADO]` |
| **Teléfonos** | `+57 300 123 4567` | `[TELEFONO_ANONIMIZADO]` |
| **Nombres propios** | `Mi nombre es Juan` | `Mi nombre es [NOMBRE_ANONIMIZADO]` |
| **Números largos** | `1234567890123` (CC/tarjetas) | `[NUMERO_ANONIMIZADO]` |
| **Session IDs** | Cualquier identificador | Hash SHA-256 (16 chars) |

## 📁 Archivos de Logs

Los logs se almacenan en el directorio `/app/logs/` (dentro del contenedor):

```
logs/
├── chatbot_YYYYMMDD.log              # Logs generales del sistema
├── interactions_YYYYMMDD.jsonl        # Interacciones usuario-chatbot (JSONL)
├── errors_YYYYMMDD.jsonl              # Errores registrados
├── system_YYYYMMDD.jsonl              # Eventos del sistema
└── analysis_report_YYYYMMDD.json     # Reporte de análisis
```

### Formato JSONL (JSON Lines)

Cada línea es un objeto JSON independiente, facilitando procesamiento por streams:

```json
{"timestamp": "2025-11-20T20:32:09.722935", "session_id": "c10099cbb84d294f", "question": "...", ...}
{"timestamp": "2025-11-20T20:35:12.481923", "session_id": "a7f8b3c2e1d59048", "question": "...", ...}
```

## 📊 Estructura de Interacción

```json
{
  "timestamp": "2025-11-20T20:32:09.722935",
  "session_id": "c10099cbb84d294f",
  "question": "Mi email es [EMAIL_ANONIMIZADO]. ¿Qué dice la ley?",
  "answer": "La ley establece...",
  "question_length": 45,
  "answer_length": 1024,
  "model": "gemini",
  "response_mode": "brief",
  "sources_count": 3,
  "response_time_seconds": 2.451,
  "metadata": {
    "top_k": 3,
    "context_length": 1567
  }
}
```

## 🛠️ Uso en Código

### Logger Principal

```python
from utils.logger import get_logger

logger = get_logger()

# Registrar interacción
logger.log_interaction(
    question="¿Qué es la IA?",
    answer="La IA es...",
    model="gemini",
    response_mode="brief",
    sources_count=3,
    response_time=1.25,
    session_id="user-123",  # Opcional
    metadata={"top_k": 5}
)

# Registrar error
logger.log_error(
    error_type="ValidationError",
    error_message="Pregunta vacía",
    context={"endpoint": "/chat"}
)

# Registrar evento del sistema
logger.log_system_event(
    event="model_switched",
    details={"from": "gemini", "to": "llama3"}
)
```

## 📈 Análisis de Logs

### Script de Análisis

```bash
# Análisis del día actual
python scripts/analyze_logs.py

# Análisis de fecha específica
python scripts/analyze_logs.py 20251120
```

### Métricas Generadas

- **Total de interacciones** y sesiones únicas
- **Distribución por modelo** (Gemini vs LLaMA3)
- **Distribución por modo** (brief vs extended)
- **Tiempos de respuesta** (min, max, avg, median)
- **Longitudes** de preguntas y respuestas
- **Fuentes consultadas** por interacción
- **Uso por hora** del día

### Ejemplo de Salida

```
📊 ANÁLISIS DE LOGS ANONIMIZADOS - 20251120
======================================================================

📈 Métricas Generales
   Total interacciones: 150
   Sesiones únicas: 42

🤖 Por Modelo
   gemini: 105 (70.0%)
   llama3: 45 (30.0%)

📝 Por Modo de Respuesta
   brief: 78 (52.0%)
   extended: 72 (48.0%)

⏱️  Tiempos de Respuesta (segundos)
   Mínimo: 1.23s
   Máximo: 15.67s
   Promedio: 4.52s
   Mediana: 3.89s
```

## 🔐 Privacidad y Seguridad

### ✅ Garantías

1. **Anonimización automática** de datos sensibles antes de almacenar
2. **Session IDs hasheados** (SHA-256) - irreversibles
3. **Sin IPs** - no se registran direcciones IP
4. **Sin geolocalización** - no se almacena ubicación
5. **Logs locales** - no se envían a servicios externos

### ⚠️ Datos NO Sensibles Registrados

- Texto de preguntas/respuestas (anonimizado)
- Modelo y modo de respuesta utilizados
- Tiempos de respuesta
- Número de fuentes consultadas
- Timestamps

## 📋 Integración con Endpoint

El logging está integrado automáticamente en `/chat`:

```json
POST /chat
{
  "question": "Mi nombre es Juan. ¿Qué es la IA?",
  "model": "gemini",
  "response_mode": "brief",
  "session_id": "optional-user-session"  // Opcional
}
```

**Resultado:** Interacción registrada con nombre anonimizado.

## 🗂️ Rotación de Logs

Los archivos de logs se organizan por fecha (`YYYYMMDD`):
- **Automático:** Se crea un nuevo archivo cada día
- **Manual:** Eliminar archivos antiguos según política de retención

### Ejemplo de Rotación

```bash
# Mantener últimos 30 días
find logs/ -name "*.log" -mtime +30 -delete
find logs/ -name "*.jsonl" -mtime +30 -delete
```

## 🚀 Casos de Uso

### 1. Monitoreo de Uso

Identificar patrones de uso, modelos preferidos, horarios pico.

### 2. Optimización de Performance

Analizar tiempos de respuesta, identificar cuellos de botella.

### 3. Mejora de Calidad

Revisar longitudes de respuestas, fuentes consultadas.

### 4. Debugging

Correlacionar errores con contexto de ejecución.

### 5. Métricas de Negocio

Sesiones únicas, tasa de adopción por modelo, engagement.

## 📦 Backup y Persistencia

Los logs se almacenan en el volumen del contenedor Docker. Para persistirlos:

```yaml
# docker-compose.yml
volumes:
  - ./logs:/app/logs  # Mapear a directorio local
```

## 🔍 Consultas Útiles

### Buscar interacciones de una sesión

```bash
grep "session_id_hash" logs/interactions_YYYYMMDD.jsonl
```

### Contar errores del día

```bash
wc -l logs/errors_YYYYMMDD.jsonl
```

### Ver última interacción

```bash
tail -1 logs/interactions_YYYYMMDD.jsonl | python -m json.tool
```

## 📚 Referencias

- **Logger:** `app/utils/logger.py`
- **Análisis:** `scripts/analyze_logs.py`
- **Integración:** `app/main.py` (endpoint `/chat`)

---

**Nota:** Este sistema cumple con principios de privacy-by-design, minimizando datos personales y anonimizando automáticamente información sensible.
