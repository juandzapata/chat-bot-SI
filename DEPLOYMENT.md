# Deployment Guide - Chatbot RAG Backend

## 🚀 Railway Deployment (Recomendado)

### ✅ Cambios Aplicados para Producción

1. **ChromaDB Embebido**: Configurado para funcionar sin servicio separado
2. **Variables de entorno**: `USE_EMBEDDED_CHROMA=true` en producción
3. **Dockerfile optimizado**: Sin `--reload`, copias selectivas
4. **railway.json**: Configuración automática

---

## 📋 Pasos para Desplegar

### **1. Push a GitHub**
```bash
git add .
git commit -m "Preparar backend para Railway deployment"
git push origin main
```

### **2. Configurar Railway**

1. Ir a [railway.app](https://railway.app) y crear cuenta con GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Seleccionar repositorio **`chat-bot-SI`**
4. Railway detectará `railway.json` automáticamente

### **3. Configurar Variables de Entorno**

En el dashboard de Railway, agregar estas variables:

```bash
GOOGLE_API_KEY=tu_api_key_de_gemini_aqui
USE_EMBEDDED_CHROMA=true
CHROMA_PERSIST_DIR=/data/vector_store
MODE=production
```

**Importante**: `GOOGLE_API_KEY` es obligatoria para que funcione Gemini.

### **4. Configurar Volumen Persistente (Crítico)**

Railway necesita persistir tu base vectorial:

1. En el servicio, ir a **"Settings"** → **"Volumes"**
2. Click **"+ New Volume"**
3. **Mount Path**: `/data/vector_store`
4. Esto preservará tus 4,814 embeddings entre deployments

### **5. Deploy Automático**

Railway construirá y desplegará automáticamente. Obtendrás una URL:
```
https://chat-bot-si-production.up.railway.app
```

---

## 🧪 Probar el Deployment

### **Endpoint Raíz**
```bash
curl https://tu-app.up.railway.app/
```

**Respuesta esperada:**
```json
{
  "message": "Chatbot IA - Regulación y Ética",
  "status": "online"
}
```

### **Hacer una Pregunta**
```bash
curl -X POST https://tu-app.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué es la IA ética?",
    "model": "gemini",
    "response_mode": "brief"
  }'
```

### **Ver Fuentes Disponibles**
```bash
curl https://tu-app.up.railway.app/sources
```

### **Ver Política de Uso**
```bash
curl https://tu-app.up.railway.app/policy
```

---

## 🔧 Configuración del Frontend

Una vez desplegado el backend, actualiza tu frontend:

```javascript
// Cambiar de localhost a Railway URL
const API_URL = 'https://tu-app.up.railway.app';

async function sendMessage(question, model = 'gemini', mode = 'brief') {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      // Railway maneja CORS automáticamente
    },
    body: JSON.stringify({
      question: question,
      model: model,
      response_mode: mode
    })
  });
  
  const data = await response.json();
  return data;
}
```

---

## 🔄 Desarrollo Local vs Producción

### **Desarrollo Local (docker-compose)**
```bash
# .env
USE_EMBEDDED_CHROMA=false
CHROMA_HOST=chroma_db
CHROMA_PORT=8000

# Levantar servicios
docker-compose up -d
```

### **Producción (Railway)**
```bash
# Variables de entorno en Railway
USE_EMBEDDED_CHROMA=true
CHROMA_PERSIST_DIR=/data/vector_store
MODE=production
```

**El código detecta automáticamente el modo y usa:**
- **Desarrollo**: ChromaDB HTTP (servicio separado)
- **Producción**: ChromaDB Embebido (mismo contenedor)

---

## ⚠️ Consideraciones Importantes

### **1. Vector Store**
- **Problema**: Si no configuras volumen, pierdes embeddings en cada deploy
- **Solución**: Volumen persistente en `/data/vector_store` (4,814 chunks)

### **2. Logs Anonimizados**
- Railway rota logs automáticamente
- Tus logs JSON se guardan en `/app/logs` (también persistir si necesario)

### **3. Re-ingesta de Documentos**
Si necesitas actualizar el corpus en producción:
```bash
# Conectar a Railway CLI
railway login
railway link

# Ejecutar script de ingesta
railway run python -m app.rag.ingest_all
```

### **4. CORS**
Railway maneja CORS automáticamente, pero si tienes problemas:

```python
# En app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-frontend.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoreo

Railway proporciona:
- **Logs en tiempo real**: Ver requests y respuestas
- **Métricas**: CPU, RAM, network
- **Health checks**: Verifica `/` cada 60s

Para ver logs:
```bash
railway logs
```

---

## 💰 Costos Estimados

Railway Free Tier:
- **500 horas/mes gratis**
- **1GB RAM incluido**
- **1GB storage persistente**

Tu chatbot consume aproximadamente:
- **RAM**: ~300-500MB (ChromaDB embebido + FastAPI)
- **Storage**: ~50MB (4,814 embeddings + docs)
- **Network**: Mínimo (solo API calls)

**Estimado**: $0-5/mes con tráfico bajo-medio

---

## 🆘 Troubleshooting

### **Error: "ChromaDB connection refused"**
✅ Verificar `USE_EMBEDDED_CHROMA=true` en variables de entorno

### **Error: "GOOGLE_API_KEY not found"**
✅ Agregar `GOOGLE_API_KEY` en Railway dashboard

### **Error: "No collections found"**
✅ Ejecutar script de ingesta: `railway run python -m app.rag.ingest_all`

### **Error: 404 en /chat**
✅ Verificar que el servicio esté corriendo: `railway logs`

### **Error: Embeddings desaparecen después de redeploy**
✅ Configurar volumen persistente en `/data/vector_store`

---

## ✅ Checklist Pre-Deployment

- [x] Código modificado para ChromaDB embebido
- [x] `railway.json` configurado
- [x] Dockerfile optimizado (sin --reload)
- [ ] Push a GitHub (main branch)
- [ ] Cuenta Railway creada
- [ ] Proyecto conectado a repo
- [ ] Variables de entorno configuradas (`GOOGLE_API_KEY`)
- [ ] Volumen persistente configurado (`/data/vector_store`)
- [ ] Deployment exitoso
- [ ] Endpoints probados (/, /chat, /sources, /policy)
- [ ] Frontend actualizado con nueva URL

---

## 🚀 Siguientes Pasos

1. **Deploy inicial**: Seguir pasos 1-5
2. **Probar endpoints**: Verificar que todo funciona
3. **Actualizar frontend**: Cambiar URL de localhost a Railway
4. **Monitorear**: Revisar logs durante primeras horas
5. **Documentar**: Anotar URL final para presentación
