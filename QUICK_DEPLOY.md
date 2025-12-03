# 🚀 Guía Rápida de Deployment - 5 Minutos

## ✅ Preparación Completada

Tu backend ya está **listo para deployment** en Railway con estos cambios:

1. ✅ ChromaDB configurado en modo embebido (producción)
2. ✅ ChromaDB en modo HTTP (desarrollo local)
3. ✅ Detección automática de entorno
4. ✅ Dockerfile optimizado
5. ✅ `railway.json` configurado

---

## 📋 Checklist Pre-Deployment

- [ ] Tienes cuenta en GitHub (tu repo: `juandzapata/chat-bot-SI`)
- [ ] Tienes `GOOGLE_API_KEY` válida para Gemini
- [ ] Frontend separado (actualizar URL después)

---

## 🎯 Pasos para Desplegar (5 minutos)

### **1. Push a GitHub** (30 segundos)
```bash
git add .
git commit -m "Backend listo para Railway"
git push origin main
```

### **2. Crear cuenta en Railway** (1 minuto)
1. Ir a [railway.app](https://railway.app)
2. Click "Login with GitHub"
3. Autorizar Railway

### **3. Crear Proyecto** (1 minuto)
1. Dashboard → "New Project"
2. "Deploy from GitHub repo"
3. Seleccionar `juandzapata/chat-bot-SI`
4. Railway empieza a construir automáticamente

### **4. Configurar Variables** (1 minuto)
En el dashboard del proyecto:

1. Click en tu servicio
2. Tab "Variables"
3. Agregar:
   ```
   GOOGLE_API_KEY = tu_clave_aqui
   ```
   (Las demás ya están en `railway.json`)

### **5. Configurar Volumen** (1 minuto) - **CRÍTICO**
1. Tab "Settings" → "Volumes"
2. Click "+ New Volume"
3. Mount Path: `/data/vector_store`
4. Click "Add"

**⚠️ Sin esto, pierdes tus embeddings en cada deploy**

### **6. Esperar Deploy** (1 minuto)
Railway construye y despliega. Verás:
- ✅ Build success
- ✅ Deploy success
- 🌐 URL generada: `https://chat-bot-si-production-xxx.up.railway.app`

---

## 🧪 Probar el Deployment

### **Endpoint Raíz**
```bash
curl https://tu-url.up.railway.app/
```

**Esperado:**
```json
{
  "status": "ChatBot IA funcionando correctamente",
  "mode": "production",
  "chroma_status": "Conexión exitosa a ChromaDB"
}
```

### **Hacer Pregunta**
```bash
curl -X POST https://tu-url.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué es la IA ética?",
    "model": "gemini",
    "response_mode": "brief"
  }'
```

---

## 🔧 Actualizar Frontend

En tu frontend separado, cambiar:

```javascript
// ANTES (desarrollo)
const API_URL = 'http://localhost:9000';

// DESPUÉS (producción)
const API_URL = 'https://tu-url.up.railway.app';
```

---

## 📊 Monitoreo

### **Ver Logs en Tiempo Real**
Railway Dashboard → Tu servicio → "Deployments" → "View Logs"

### **Métricas**
Railway Dashboard → Tu servicio → "Metrics"
- CPU usage
- Memory usage
- Request count

---

## ⚠️ Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| 500 Internal Server Error | Ver logs: buscar "GOOGLE_API_KEY" |
| "No collections found" | Ejecutar: `railway run python -m app.rag.ingest_all` |
| Embeddings desaparecen | Verificar volumen en `/data/vector_store` |
| CORS errors desde frontend | Agregar dominio en `app/main.py` CORS |

---

## 💰 Costos

**Railway Free Tier:**
- 500 horas/mes gratis
- 1GB RAM
- 1GB storage

**Tu app consume:**
- ~400MB RAM
- ~50MB storage
- Tráfico: mínimo

**Estimado: $0/mes** con tráfico bajo (proyecto académico)

---

## 📱 Siguiente Paso: Frontend

Una vez el backend esté deployed:

1. Copiar URL de Railway
2. Actualizar `API_URL` en frontend
3. Desplegar frontend en Vercel/Netlify
4. Listo para presentar

---

## 🎓 Para la Presentación

**Backend desplegado en:** https://tu-url.up.railway.app  
**Documentación completa:** `DEPLOYMENT.md`  
**Tiempo total de setup:** ~5 minutos  

**Demostración en vivo:**
```bash
# Desde cualquier lugar del mundo
curl -X POST https://tu-url.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué dice el AI Act sobre sistemas de alto riesgo?", "model": "gemini", "response_mode": "extended"}'
```

---

## 🔗 Links Importantes

- **Railway Dashboard**: https://railway.app/dashboard
- **Docs Railway**: https://docs.railway.app
- **Tu Repo**: https://github.com/juandzapata/chat-bot-SI
- **Deployment Guide Completo**: Ver `DEPLOYMENT.md`
