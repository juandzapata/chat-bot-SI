# 🌐 Documentación de API - Frontend Integration

## URL Base
```
http://localhost:9000
```

## ✅ Estado: LISTO PARA FRONTEND

La aplicación está configurada con CORS y lista para ser consumida desde cualquier frontend.

---

## 📚 Endpoints Disponibles

### 1. Health Check
**Verificar que el sistema está funcionando**

```http
GET /
```

**Response:**
```json
{
  "status": "ChatBot IA funcionando correctamente",
  "mode": "development",
  "chroma_status": "Conexión exitosa a ChromaDB"
}
```

---

### 2. Chat con RAG (Principal)
**Hacer preguntas al chatbot**

```http
POST /chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "question": "¿Qué normativas de IA existen en Colombia?",
  "top_k": 3
}
```

**Parámetros:**
- `question` (string, requerido): La pregunta del usuario
- `top_k` (int, opcional): Número de documentos a recuperar (default: 3)

**Response (Éxito):**
```json
{
  "status": "ok",
  "answer": "Basándote ÚNICAMENTE en los documentos proporcionados...",
  "question": "¿Qué normativas de IA existen en Colombia?",
  "sources": [
    {
      "title": "ABC Proyecto de Ley de Inteligencia Artificial (Colombia)",
      "source": "Gobierno de Colombia (Promovido por MinCiencias...",
      "category": "colombia",
      "year": "No especificado (Iniciativa legislativa)"
    }
  ],
  "context_used": 3
}
```

**Response (Error):**
```json
{
  "detail": "La pregunta no puede estar vacía"
}
```

---

### 3. Estadísticas de la Colección
**Ver cuántos documentos están en el sistema**

```http
GET /collection_stats
```

**Response:**
```json
{
  "status": "ok",
  "collection": "documentos_ucaldas",
  "total_chunks": 22,
  "message": "Colección contiene 22 chunks de documentos"
}
```

---

### 4. Ingesta de Documentos (Admin)
**Importar documentos al sistema**

```http
POST /ingest_all
```

**Response:**
```json
{
  "status": "ok",
  "message": "Ingesta completada exitosamente",
  "summary": {
    "total_documents": 3,
    "successful": 2,
    "failed": 1
  },
  "details": [
    {
      "success": true,
      "document_id": "doc_internacional_1",
      "chunks_count": 10,
      "message": "Documento ingerido exitosamente"
    }
  ]
}
```

---

### 5. Prueba de Ingesta
**Insertar documento de prueba**

```http
POST /ingest_test
```

**Response:**
```json
{
  "status": "ok",
  "message": "Documento doc_test_1 agregado correctamente..."
}
```

---

## 💻 Ejemplos de Uso en Frontend

### React/Next.js

```typescript
const API_BASE = 'http://localhost:9000';

// Función para hacer preguntas al chatbot
async function askQuestion(question: string, topK: number = 3) {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        top_k: topK
      })
    });
    
    if (!response.ok) {
      throw new Error('Error al comunicarse con el servidor');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Uso
const result = await askQuestion('¿Qué normativas de IA existen?');
console.log(result.answer);  // La respuesta del chatbot
console.log(result.sources); // Las fuentes utilizadas
```

### Vue.js

```javascript
const apiBase = 'http://localhost:9000';

export default {
  methods: {
    async sendMessage(question) {
      try {
        const response = await fetch(`${apiBase}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question,
            top_k: 3
          })
        });
        
        const data = await response.json();
        return data;
      } catch (error) {
        console.error('Error:', error);
        throw error;
      }
    }
  }
}
```

### JavaScript/Vanilla

```javascript
const API_BASE = 'http://localhost:9000';

async function chat(question) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: question,
      top_k: 3
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error desconocido');
  }
  
  return await response.json();
}

// Uso
chat('¿Qué normativas de IA existen en Colombia?')
  .then(result => {
    console.log('Respuesta:', result.answer);
    console.log('Fuentes:', result.sources);
  })
  .catch(error => console.error('Error:', error));
```

---

## 🎨 Estructura Recomendada de UI

### Componente de Chat

```
┌─────────────────────────────────────────┐
│  ChatBot IA - Universidad de Caldas    │
├─────────────────────────────────────────┤
│                                         │
│  [Usuario]                              │
│  ¿Qué normativas de IA existen?        │
│                                         │
│  [Asistente]                            │
│  Basándote en los documentos...         │
│                                         │
│  📚 Fuentes:                            │
│  • ABC Proyecto de Ley... (Colombia)    │
│  • Ley de IA de la UE (2024)           │
│                                         │
├─────────────────────────────────────────┤
│  Escribe tu pregunta...           [➤]  │
└─────────────────────────────────────────┘
```

### Estado de la Interfaz

```typescript
interface ChatState {
  messages: Message[];
  loading: boolean;
  sources: Source[];
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Source {
  title: string;
  source: string;
  category: string;
  year: string | number;
}
```

---

## 🔒 Seguridad y Configuración

### CORS
- Actualmente configurado para aceptar requests de cualquier origen (`*`)
- Para producción, cambiar a:
  ```python
  allow_origins=["https://tudominio.com"]
  ```

### Variables de Entorno
El backend requiere:
- `GEMINI_API_KEY`: API key de Google Gemini
- `CHROMA_HOST`: Host de ChromaDB
- `CHROMA_PORT`: Puerto de ChromaDB

### Rate Limiting
Actualmente no implementado. Recomendado para producción.

---

## 📊 Flujo Típico de Uso

1. **Usuario envía pregunta** → Frontend hace POST a `/chat`
2. **Backend busca contexto** → ChromaDB encuentra documentos relevantes
3. **Backend genera respuesta** → Gemini usa el contexto encontrado
4. **Backend retorna respuesta** → Frontend muestra al usuario con fuentes

---

## 🐛 Manejo de Errores

### Errores Comunes

**400 - Bad Request**
```json
{
  "detail": "La pregunta no puede estar vacía"
}
```

**500 - Internal Server Error**
```json
{
  "detail": "Error al generar respuesta"
}
```

### Implementación en Frontend

```typescript
try {
  const result = await askQuestion(question);
  // Mostrar resultado
} catch (error) {
  if (error.response?.status === 400) {
    // Mostrar mensaje de validación
    showError('Por favor ingresa una pregunta válida');
  } else if (error.response?.status === 500) {
    // Mostrar error del servidor
    showError('Error en el servidor. Intenta más tarde.');
  } else {
    // Error de red
    showError('Error de conexión. Verifica tu internet.');
  }
}
```

---

## 🚀 Próximos Pasos Recomendados

1. **Implementar historial de conversaciones** (opcional)
2. **Streaming de respuestas** (para UX mejorada)
3. **Feedback de usuarios** (mejorar calidad de respuestas)
4. **Autenticación** (si se requiere acceso restringido)
5. **Cache de respuestas** (para preguntas frecuentes)

---

## 📞 Soporte

Para más información, consulta:
- `INGEST_INSTRUCTIONS.md` - Detalles de ingesta
- `STATUS.md` - Estado actual del proyecto
- Logs del contenedor: `docker-compose logs -f api`
