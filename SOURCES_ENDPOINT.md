# 📚 Endpoint `/sources` - Fuentes Documentales

**Fecha:** 9 de noviembre de 2025  
**Versión:** 0.3.0  
**Feature:** Listado de fuentes documentales agrupadas por categoría

---

## 📋 Resumen

El endpoint `/sources` permite obtener un listado completo de todas las fuentes documentales **únicas** disponibles en la base de datos ChromaDB, organizadas por categoría (Colombia, Internacional, Universidad de Caldas).

**Nota importante:** Este endpoint retorna documentos únicos (deduplicados por título). Internamente, ChromaDB almacena múltiples "chunks" (fragmentos) de cada documento PDF para optimizar la búsqueda semántica, pero este endpoint los agrupa y muestra solo una vez cada documento.

### **Chunks vs Documentos:**

```
📄 document_colombia_1.pdf (1 archivo físico)
    ↓ Se divide en chunks para ChromaDB
    → chunk_1: "El proyecto de ley..."
    → chunk_2: "Los sistemas de alto riesgo..."
    → chunk_3: "La supervisión..."
    → ... (múltiples chunks)
    ↓ Este endpoint los agrupa
    → 1 documento único en la respuesta
```

---

## 🔧 Especificación del Endpoint

### **GET `/sources`**

Retorna todas las fuentes documentales disponibles, agrupadas por categoría.

#### **Request:**

```bash
GET http://localhost:9000/sources
```

No requiere parámetros ni body.

#### **Response (200 OK):**

```json
{
  "status": "ok",
  "total_sources": 3,
  "total_categories": 3,
  "categories": [
    {
      "category": "colombia",
      "category_name": "Colombia",
      "count": 1,
      "sources": [
        {
          "title": "ABC Proyecto de Ley de Inteligencia Artificial (Colombia)",
          "source": "Gobierno de Colombia (Promovido por MinCiencias y articulado con MinTIC/SIC)",
          "year": "No especificado (Iniciativa legislativa)"
        }
      ]
    },
    {
      "category": "internacional",
      "category_name": "Internacional",
      "count": 1,
      "sources": [
        {
          "title": "Ley de IA de la UE: primera normativa sobre inteligencia artificial",
          "source": "Parlamento Europeo / Unión Europea",
          "year": 2024
        }
      ]
    },
    {
      "category": "universidad",
      "category_name": "Universidad de Caldas",
      "count": 1,
      "sources": [
        {
          "title": "Formación para el futuro: Universidad de Caldas presentó el nuevo programa de Inteligencia Artificial",
          "source": "Universidad de Caldas",
          "year": "N/A"
        }
      ]
    }
  ]
}
```

#### **Estructura de la Respuesta:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `status` | string | Estado de la petición (`"ok"` o `"error"`) |
| `total_sources` | number | Número total de fuentes disponibles |
| `total_categories` | number | Número de categorías |
| `categories` | array | Lista de categorías con sus fuentes |

#### **Estructura de cada categoría:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `category` | string | ID de la categoría (`"colombia"`, `"internacional"`, `"universidad"`) |
| `category_name` | string | Nombre legible de la categoría |
| `count` | number | Número de fuentes en esta categoría |
| `sources` | array | Lista de fuentes |

#### **Estructura de cada fuente:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `title` | string | Título del documento |
| `source` | string | Organismo o fuente del documento |
| `year` | string/number | Año de publicación |

---

## 💻 Ejemplos de Implementación

### **JavaScript/Fetch Vanilla**

```javascript
async function loadSources() {
  try {
    const response = await fetch('http://localhost:9000/sources');
    
    if (!response.ok) {
      throw new Error('Error al cargar fuentes');
    }
    
    const data = await response.json();
    
    console.log(`Total de fuentes: ${data.total_sources}`);
    console.log(`Categorías: ${data.total_categories}`);
    
    // Iterar por categorías
    data.categories.forEach(category => {
      console.log(`\n${category.category_name} (${category.count} documento(s)):`);
      
      category.sources.forEach(source => {
        console.log(`  - ${source.title} (${source.year})`);
      });
    });
    
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Uso
loadSources();

// Salida esperada:
// Total de fuentes: 3
// Categorías: 3
//
// Colombia (1 documento(s)):
//   - ABC Proyecto de Ley de Inteligencia Artificial (Colombia) (No especificado)
//
// Internacional (1 documento(s)):
//   - Ley de IA de la UE: primera normativa sobre inteligencia artificial (2024)
//
// Universidad de Caldas (1 documento(s)):
//   - Formación para el futuro... (N/A)
```

---

### **React Component**

```jsx
import { useState, useEffect } from 'react';

function SourcesViewer() {
  const [sources, setSources] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      const response = await fetch('http://localhost:9000/sources');
      const data = await response.json();
      setSources(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando fuentes...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!sources) return null;

  return (
    <div className="sources-viewer">
      <h2>Fuentes Documentales</h2>
      <p>Total: {sources.total_sources} documentos en {sources.total_categories} categorías</p>
      
      {sources.categories.map(category => (
        <div key={category.category} className="category">
          <h3>{category.category_name} ({category.count})</h3>
          
          <ul>
            {category.sources.map((source, idx) => (
              <li key={idx}>
                <strong>{source.title}</strong>
                <br />
                <small>{source.source} - {source.year}</small>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default SourcesViewer;
```

---

### **Vue.js Component**

```vue
<template>
  <div class="sources-viewer">
    <h2>Fuentes Documentales</h2>
    
    <div v-if="loading">Cargando fuentes...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    
    <div v-else>
      <p>
        Total: {{ sources.total_sources }} documentos 
        en {{ sources.total_categories }} categorías
      </p>
      
      <div 
        v-for="category in sources.categories" 
        :key="category.category"
        class="category"
      >
        <h3>{{ category.category_name }} ({{ category.count }})</h3>
        
        <ul>
          <li v-for="(source, idx) in category.sources" :key="idx">
            <strong>{{ source.title }}</strong>
            <br>
            <small>{{ source.source }} - {{ source.year }}</small>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      sources: null,
      loading: true,
      error: null
    }
  },
  
  mounted() {
    this.loadSources();
  },
  
  methods: {
    async loadSources() {
      try {
        const response = await fetch('http://localhost:9000/sources');
        this.sources = await response.json();
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.category {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.category h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.category ul {
  list-style: none;
  padding: 0;
}

.category li {
  margin: 10px 0;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}
</style>
```

---

## 🎨 UI/UX - Componente de Lista de Fuentes

### **Diseño Propuesto:**

```html
<!-- Card por categoría -->
<div class="sources-container">
  <!-- Categoría: Colombia -->
  <div class="category-card">
    <div class="category-header">
      <h3>🇨🇴 Colombia</h3>
      <span class="badge">11 documentos</span>
    </div>
    
    <div class="sources-list">
      <div class="source-item">
        <h4>ABC Proyecto de Ley de Inteligencia Artificial (Colombia)</h4>
        <p class="source-meta">
          <span class="source-org">Gobierno de Colombia</span>
          <span class="source-year">2024</span>
        </p>
      </div>
      <!-- Más documentos... -->
    </div>
  </div>
  
  <!-- Categoría: Internacional -->
  <div class="category-card">
    <div class="category-header">
      <h3>🌍 Internacional</h3>
      <span class="badge">10 documentos</span>
    </div>
    
    <div class="sources-list">
      <!-- Documentos... -->
    </div>
  </div>
  
  <!-- Categoría: Universidad -->
  <div class="category-card">
    <div class="category-header">
      <h3>🎓 Universidad de Caldas</h3>
      <span class="badge">1 documento</span>
    </div>
    
    <div class="sources-list">
      <!-- Documentos... -->
    </div>
  </div>
</div>
```

### **CSS Sugerido:**

```css
.sources-container {
  display: grid;
  gap: 20px;
  padding: 20px;
}

.category-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
  transition: transform 0.2s;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.category-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.4em;
}

.badge {
  background: #3498db;
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 600;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.source-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.source-item h4 {
  margin: 0 0 8px 0;
  font-size: 1em;
  color: #2c3e50;
}

.source-meta {
  display: flex;
  gap: 15px;
  font-size: 0.9em;
  color: #7f8c8d;
}

.source-org::before {
  content: "📄 ";
}

.source-year::before {
  content: "📅 ";
}
```

---

## 🧪 Testing / Pruebas

### **Curl básico:**

```bash
curl http://localhost:9000/sources
```

### **Curl con formato JSON (usando jq):**

```bash
curl -s http://localhost:9000/sources | jq
```

### **Obtener solo el total de fuentes:**

```bash
curl -s http://localhost:9000/sources | jq '.total_sources'
```

### **Obtener solo las categorías:**

```bash
curl -s http://localhost:9000/sources | jq '.categories[].category_name'
```

### **Obtener documentos de una categoría específica:**

```bash
# Colombia
curl -s http://localhost:9000/sources | jq '.categories[] | select(.category == "colombia")'

# Internacional
curl -s http://localhost:9000/sources | jq '.categories[] | select(.category == "internacional")'

# Universidad
curl -s http://localhost:9000/sources | jq '.categories[] | select(.category == "universidad")'
```

---

## 📊 Casos de Uso

### **1. Mostrar fuentes en página "Acerca de"**
- Listar todas las fuentes documentales que respaldan el chatbot
- Generar confianza mostrando transparencia en las fuentes

### **2. Filtro por categoría en el chat**
- Permitir al usuario filtrar respuestas por categoría
- "Solo buscar en documentos de Colombia"
- "Solo buscar en normativas internacionales"

### **3. Estadísticas del corpus**
- Mostrar métricas del sistema
- "Nuestro chatbot cuenta con X documentos de Y categorías"

### **4. Página de referencias bibliográficas**
- Generar lista de referencias automáticamente
- Exportar como PDF o Markdown

### **5. Validación de cobertura documental**
- Verificar qué áreas tienen más/menos documentación
- Identificar gaps en el corpus

---

## 🔄 Integración con otros endpoints

### **Uso conjunto con `/chat`:**

```javascript
// 1. Primero obtener fuentes disponibles
const sourcesData = await fetch('/sources').then(r => r.json());

// 2. Mostrar al usuario las categorías disponibles
console.log('Categorías disponibles:', sourcesData.categories.map(c => c.category_name));

// 3. Usuario hace una pregunta
const chatResponse = await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    question: "¿Qué normativas existen?",
    model: "gemini"
  })
});

// 4. En la respuesta, los sources citados se pueden cruzar con la lista completa
const { sources } = await chatResponse.json();
console.log('Documentos citados:', sources);
```

---

## ⚡ Optimizaciones Futuras

### **1. Cache en frontend**
```javascript
// Guardar en localStorage para evitar peticiones repetidas
const cachedSources = localStorage.getItem('sources');
if (cachedSources) {
  return JSON.parse(cachedSources);
}

const sources = await fetch('/sources').then(r => r.json());
localStorage.setItem('sources', JSON.stringify(sources));
```

### **2. Parámetros de filtro (opcional)**
```javascript
// Posible extensión futura
GET /sources?category=colombia
GET /sources?year=2024
GET /sources?search=IA
```

### **3. Paginación (si el corpus crece mucho)**
```javascript
GET /sources?page=1&limit=10
```

---

## 📝 Notas Técnicas

### **Deduplicación automática:**
- ✅ **El endpoint ya incluye deduplicación por título**
- Los documentos PDF se dividen en chunks (fragmentos) cuando se ingresan a ChromaDB
- Cada chunk tiene los mismos metadatos (título, organismo, año)
- El endpoint agrupa automáticamente los chunks del mismo documento
- Por tanto, **cada documento aparece solo una vez** en la respuesta

### **¿Por qué ChromaDB usa chunks?**
```
Documento original: 50 páginas
    ↓ Chunking (división en fragmentos)
    → chunk_1: Páginas 1-5   (embedding 1)
    → chunk_2: Páginas 6-10  (embedding 2)
    → chunk_3: Páginas 11-15 (embedding 3)
    → ...

Ventajas:
✓ Mejor precisión en búsqueda semántica
✓ Contexto más específico para las respuestas
✓ Manejo eficiente de documentos largos
✓ Evita límites de tokens en embeddings
```

### **Chunks en ChromaDB vs Documentos únicos:**
```bash
# Ver total de chunks en ChromaDB
curl http://localhost:9000/collection_stats
# Response: "total_chunks": 22

# Ver documentos únicos (deduplicados)
curl http://localhost:9000/sources
# Response: "total_sources": 3
```

### **Agrupación por categoría:**
- Las categorías se extraen del campo `categoria` en los metadatos de ChromaDB
- El orden de las categorías es: `colombia` → `internacional` → `universidad` → otros
- Si un documento no tiene categoría asignada, se agrupa en `"sin_categoria"`

### **Nombres de categorías:**
```javascript
{
  "colombia": "Colombia",
  "internacional": "Internacional",
  "universidad": "Universidad de Caldas",
  "sin_categoria": "Sin Categoría"
}
```

### **¿Necesito deduplicar en el frontend?**
**No.** El endpoint ya realiza la deduplicación automáticamente. Cada documento aparece solo una vez, sin importar cuántos chunks tenga en ChromaDB.

---

## 🆚 Comparación: Antes vs Ahora

### **❌ Versión Anterior (Sin deduplicación):**
```json
{
  "total_sources": 22,  // ← Contaba chunks, no documentos
  "categories": [
    {
      "category": "colombia",
      "count": 11,  // ← 1 PDF dividido en 11 chunks
      "sources": [
        {"title": "ABC Proyecto de Ley...", ...},
        {"title": "ABC Proyecto de Ley...", ...},  // ← Duplicado
        {"title": "ABC Proyecto de Ley...", ...},  // ← Duplicado
        // ... (11 veces el mismo documento)
      ]
    }
  ]
}
```

### **✅ Versión Actual (Con deduplicación):**
```json
{
  "total_sources": 3,  // ← Documentos únicos correctos
  "categories": [
    {
      "category": "colombia",
      "count": 1,  // ← 1 documento único
      "sources": [
        {"title": "ABC Proyecto de Ley...", ...}  // ← Aparece solo 1 vez
      ]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### **Error: No se encuentran fuentes**

```json
{
  "status": "ok",
  "total_sources": 0,
  "total_categories": 0,
  "categories": []
}
```

**Solución:**
1. Verificar que ChromaDB esté corriendo: `docker ps`
2. Verificar que se hayan ingestado documentos: `POST /ingest_all`
3. Verificar la colección: `GET /collection_stats`

### **Error 500: Internal Server Error**

**Causas comunes:**
- ChromaDB no está disponible
- Error de conexión con la base de datos
- Problema con los metadatos

**Solución:**
```bash
# Reiniciar ChromaDB
docker-compose restart chromadb

# Verificar logs
docker-compose logs chromadb
```

---

## 📞 Soporte y Documentación Relacionada

**Archivos relacionados:**
- `app/main.py` - Endpoint `/sources` implementado
- `app/rag/chroma_manager.py` - Función `get_all_sources()`
- `data/corpus/corpus_metadata.json` - Metadatos de documentos
- `API_FRONTEND.md` - Documentación general de la API

---

**Actualización completada el:** 9 de noviembre de 2025  
**Desarrollado por:** ChatBot IA - Universidad de Caldas  
**Feature:** Sources endpoint con agrupación por categoría
