# 🆕 Actualización: Modos de Respuesta Brief/Extended

**Fecha:** 8 de noviembre de 2025  
**Versión:** 0.2.0  
**Feature:** Modos de respuesta breve y extendido

---

## 📋 Resumen de Cambios

Se agregó soporte para dos modos de respuesta en el chatbot:
- **Brief (Breve)**: Respuestas concisas de ~150 palabras (~200 tokens)
- **Extended (Extendido)**: Respuestas detalladas de ~600 palabras (~800 tokens)

---

## 🔧 Cambios en la API

### 1️⃣ Endpoint `/chat` - ACTUALIZADO

#### **Request Body:**

```json
{
  "question": "¿Qué normativas de IA existen?",
  "model": "gemini",      // opcional: "gemini" o "llama3" (default: "gemini")
  "mode": "brief",        // ⭐ NUEVO: "brief" o "extended" (default: "extended")
  "top_k": 3              // opcional: número de documentos (default: 3)
}
```

#### **Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `question` | string | ✅ Sí | - | Pregunta del usuario |
| `model` | string | ❌ No | `"gemini"` | Modelo a usar: `"gemini"` o `"llama3"` |
| `mode` | string | ❌ No | `"extended"` | **NUEVO**: `"brief"` o `"extended"` |
| `top_k` | number | ❌ No | `3` | Número de documentos a recuperar |

#### **Response:**

```json
{
  "status": "ok",
  "answer": "Basado únicamente en los documentos oficiales...",
  "question": "¿Qué normativas de IA existen?",
  "model_used": "gemini",
  "response_mode": "brief",  // ⭐ NUEVO: modo utilizado
  "sources": [
    {
      "title": "Ley de IA de la UE",
      "source": "Parlamento Europeo",
      "category": "internacional",
      "year": 2024
    }
  ],
  "context_used": 3
}
```

#### **Errores:**

**400 - Modo inválido:**
```json
{
  "detail": "El modo debe ser 'brief' o 'extended'"
}
```

---

### 2️⃣ Endpoint `/models` - ACTUALIZADO

Ahora incluye información sobre los modos de respuesta disponibles.

#### **Response:**

```json
{
  "status": "ok",
  "available_models": [
    {
      "id": "gemini",
      "name": "Gemini 2.5 Flash",
      "provider": "Google",
      "description": "Modelo de Google para generación de texto"
    },
    {
      "id": "llama3",
      "name": "LLaMA 3 8B",
      "provider": "Groq",
      "description": "Modelo open source de Meta via Groq"
    }
  ],
  "default_model": "gemini",
  "total_models": 2,
  "response_modes": [          // ⭐ NUEVO
    {
      "id": "brief",
      "name": "Breve",
      "description": "Respuesta concisa (~200 tokens, ~150 palabras)",
      "max_tokens": 200
    },
    {
      "id": "extended",
      "name": "Extendido",
      "description": "Respuesta detallada (~800 tokens, ~600 palabras)",
      "max_tokens": 800
    }
  ],
  "default_mode": "extended"   // ⭐ NUEVO
}
```

---

## 💻 Ejemplos de Implementación en Frontend

### **JavaScript/Fetch Vanilla**

```javascript
// Función para hacer consultas con modo seleccionable
async function askQuestion(question, model = 'gemini', mode = 'extended') {
  try {
    const response = await fetch('http://localhost:9000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        model,
        mode  // ⭐ NUEVO parámetro
      })
    });
    
    if (!response.ok) {
      throw new Error('Error en la petición');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Uso
const result = await askQuestion(
  "¿Qué normativas de IA existen?", 
  "gemini", 
  "brief"  // Respuesta breve
);

console.log('Modo usado:', result.response_mode);
console.log('Respuesta:', result.answer);
```

---

### **React Component**

```jsx
import { useState } from 'react';

function ChatInterface() {
  const [question, setQuestion] = useState('');
  const [model, setModel] = useState('gemini');
  const [mode, setMode] = useState('extended');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('http://localhost:9000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          model,
          mode  // ⭐ NUEVO
        })
      });

      const data = await res.json();
      setResponse(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* Selector de modelo */}
        <select value={model} onChange={(e) => setModel(e.target.value)}>
          <option value="gemini">Gemini 2.5 Flash</option>
          <option value="llama3">LLaMA 3 8B</option>
        </select>

        {/* ⭐ NUEVO: Selector de modo */}
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="brief">Breve (150 palabras)</option>
          <option value="extended">Detallado (600 palabras)</option>
        </select>

        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Escribe tu pregunta..."
        />

        <button type="submit" disabled={loading}>
          {loading ? 'Consultando...' : 'Preguntar'}
        </button>
      </form>

      {/* Mostrar respuesta */}
      {response && (
        <div>
          <p><strong>Modo:</strong> {response.response_mode}</p>
          <p><strong>Modelo:</strong> {response.model_used}</p>
          <p><strong>Respuesta:</strong> {response.answer}</p>
          
          {/* Fuentes */}
          <h4>Fuentes:</h4>
          <ul>
            {response.sources.map((source, idx) => (
              <li key={idx}>
                {source.title} - {source.source} ({source.year})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
```

---

### **Vue.js Component**

```vue
<template>
  <div class="chat-interface">
    <!-- Selectores -->
    <div class="controls">
      <select v-model="selectedModel">
        <option value="gemini">Gemini 2.5 Flash</option>
        <option value="llama3">LLaMA 3 8B</option>
      </select>

      <!-- ⭐ NUEVO: Selector de modo -->
      <select v-model="selectedMode">
        <option value="brief">Breve</option>
        <option value="extended">Detallado</option>
      </select>
    </div>

    <!-- Input de pregunta -->
    <input
      v-model="question"
      @keyup.enter="sendMessage"
      placeholder="Escribe tu pregunta..."
    />

    <button @click="sendMessage" :disabled="loading">
      {{ loading ? 'Consultando...' : 'Preguntar' }}
    </button>

    <!-- Respuesta -->
    <div v-if="response" class="response">
      <p><strong>Modo:</strong> {{ response.response_mode }}</p>
      <p>{{ response.answer }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      question: '',
      selectedModel: 'gemini',
      selectedMode: 'extended',  // ⭐ NUEVO
      response: null,
      loading: false
    }
  },
  methods: {
    async sendMessage() {
      if (!this.question.trim()) return;

      this.loading = true;

      try {
        const res = await fetch('http://localhost:9000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: this.question,
            model: this.selectedModel,
            mode: this.selectedMode  // ⭐ NUEVO
          })
        });

        this.response = await res.json();
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
```

---

## 🎨 UI/UX Recomendaciones

### **Toggle Button (Modo)**

```html
<div class="mode-toggle">
  <button 
    class="${mode === 'brief' ? 'active' : ''}"
    onclick="setMode('brief')"
  >
    📝 Breve
  </button>
  <button 
    class="${mode === 'extended' ? 'active' : ''}"
    onclick="setMode('extended')"
  >
    📄 Detallado
  </button>
</div>
```

### **Radio Buttons**

```html
<div class="mode-selector">
  <label>
    <input type="radio" name="mode" value="brief" checked>
    Respuesta breve (~150 palabras)
  </label>
  <label>
    <input type="radio" name="mode" value="extended">
    Respuesta detallada (~600 palabras)
  </label>
</div>
```

---

## 🧪 Testing / Pruebas

### **Curl - Modo Brief**
```bash
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué normativas de IA existen?",
    "model": "gemini",
    "mode": "brief"
  }'
```

### **Curl - Modo Extended**
```bash
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué normativas de IA existen?",
    "model": "llama3",
    "mode": "extended"
  }'
```

### **Verificar configuración de modos**
```bash
curl http://localhost:9000/models | jq '.response_modes'
```

---

## 📊 Tabla Comparativa

| Característica | Brief | Extended |
|----------------|-------|----------|
| **Tokens (LLaMA3)** | 200 | 800 |
| **Palabras aprox.** | 150 | 600 |
| **Uso recomendado** | Consultas rápidas, respuestas directas | Análisis profundo, explicaciones detalladas |
| **Tiempo de respuesta** | Más rápido | Más lento |
| **Costo (tokens)** | Menor | Mayor |
| **Control en Gemini** | Via prompt | Via prompt |
| **Control en LLaMA3** | Via max_tokens | Via max_tokens |

---

## 🔄 Compatibilidad Backward

- ✅ **Si NO envías el parámetro `mode`**, se usa `"extended"` por defecto
- ✅ **Todos los endpoints anteriores siguen funcionando**
- ✅ **No hay breaking changes**

### **Ejemplo sin especificar modo:**
```javascript
// Esto sigue funcionando (usa extended por defecto)
await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    question: "¿Qué es la IA?",
    model: "gemini"
    // mode no especificado → usa "extended"
  })
});
```

---

## 🚀 Próximos Pasos Sugeridos

1. **Implementar selector de modo en UI**
2. **Agregar indicador visual de longitud de respuesta**
3. **Guardar preferencia de modo en localStorage**
4. **Agregar tooltip explicando diferencias**
5. **A/B testing para determinar modo preferido por usuarios**

---

## 📞 Soporte

Para más detalles técnicos, consulta:
- `app/main.py` - Endpoint `/chat` actualizado
- `app/rag/models.py` - Implementación de modos en providers
- `API_FRONTEND.md` - Documentación general de la API

---

**Actualización completada el:** 8 de noviembre de 2025  
**Desarrollado por:** ChatBot IA - Universidad de Caldas
