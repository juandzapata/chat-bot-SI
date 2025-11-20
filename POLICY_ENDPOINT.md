# 📜 Endpoint de Política - Guía de Integración Frontend

## Información General

El endpoint `/policy` proporciona acceso a la política de uso, privacidad y términos del servicio del ChatBot IA de la Universidad de Caldas.

---

## 📡 Especificación del Endpoint

### URL
```
GET http://localhost:9000/policy
```

### Método
`GET`

### Parámetros
Ninguno requerido.

### Headers de Respuesta
```
Content-Type: text/plain; charset=utf-8
```

### Código de Estado
- `200 OK` - Política retornada exitosamente
- `404 Not Found` - Archivo de política no encontrado
- `500 Internal Server Error` - Error del servidor

---

## 📥 Respuesta

### Formato
Texto plano en formato Markdown (224 líneas)

### Contenido
```markdown
# 📜 Política de Uso y Privacidad - ChatBot IA Universidad de Caldas

**Última actualización:** 19 de noviembre de 2025  
**Versión:** 1.0.0

---

## 1. Introducción

Bienvenido al ChatBot de Inteligencia Artificial de la Universidad de Caldas...

## 2. Alcance del Servicio

### 2.1 Propósito
Este chatbot está diseñado para:
- ✅ Proporcionar información sobre normativas de IA en Colombia
- ✅ Consultar regulaciones internacionales sobre IA
...

## 3. Uso Responsable
...

## 13. Notificación de Cambios
...
```

### Secciones Incluidas
1. Introducción
2. Alcance del Servicio
3. Uso Responsable
4. Privacidad y Protección de Datos
5. Fuentes de Información
6. Modelos de IA Utilizados
7. Derechos de Autor y Propiedad Intelectual
8. Limitación de Responsabilidad
9. Cumplimiento Normativo
10. Información de Contacto
11. Aceptación de la Política
12. Modificaciones a la Política
13. Notificación de Cambios

---

## 💻 Implementación en Frontend

### React / Next.js

#### Opción 1: Componente Simple con Estado

```typescript
import { useState, useEffect } from 'react';

function PolicyPage() {
  const [policy, setPolicy] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPolicy();
  }, []);

  const fetchPolicy = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:9000/policy');
      
      if (!response.ok) {
        throw new Error('No se pudo cargar la política');
      }
      
      const text = await response.text();
      setPolicy(text);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando política...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="policy-container">
      <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
        {policy}
      </pre>
    </div>
  );
}

export default PolicyPage;
```

#### Opción 2: Con React Markdown (Renderizado Formateado)

```typescript
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

function PolicyPage() {
  const [policy, setPolicy] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch('http://localhost:9000/policy')
      .then(res => res.text())
      .then(text => {
        setPolicy(text);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error cargando política:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <span>Cargando política...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <ReactMarkdown className="prose lg:prose-xl">
        {policy}
      </ReactMarkdown>
    </div>
  );
}

export default PolicyPage;
```

#### Opción 3: Modal de Aceptación de Términos

```typescript
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface PolicyModalProps {
  onAccept: () => void;
  onReject: () => void;
}

function PolicyModal({ onAccept, onReject }: PolicyModalProps) {
  const [policy, setPolicy] = useState<string>('');
  const [accepted, setAccepted] = useState<boolean>(false);

  useEffect(() => {
    fetch('http://localhost:9000/policy')
      .then(res => res.text())
      .then(setPolicy);
  }, []);

  return (
    <div className="modal-overlay">
      <div className="modal-content max-w-3xl max-h-[80vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          Términos y Condiciones
        </h2>
        
        <div className="prose mb-6">
          <ReactMarkdown>{policy}</ReactMarkdown>
        </div>

        <div className="flex items-center mb-4">
          <input
            type="checkbox"
            id="accept-terms"
            checked={accepted}
            onChange={(e) => setAccepted(e.target.checked)}
            className="mr-2"
          />
          <label htmlFor="accept-terms">
            He leído y acepto la política de uso y privacidad
          </label>
        </div>

        <div className="flex gap-4">
          <button
            onClick={onAccept}
            disabled={!accepted}
            className="btn-primary"
          >
            Aceptar y Continuar
          </button>
          <button onClick={onReject} className="btn-secondary">
            Rechazar
          </button>
        </div>
      </div>
    </div>
  );
}

export default PolicyModal;
```

---

### Vue.js

#### Opción 1: Composición API

```vue
<template>
  <div class="policy-page">
    <div v-if="loading" class="loading">
      Cargando política...
    </div>
    
    <div v-else-if="error" class="error">
      Error: {{ error }}
    </div>
    
    <div v-else class="policy-content">
      <pre>{{ policy }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const policy = ref('');
const loading = ref(true);
const error = ref(null);

const fetchPolicy = async () => {
  try {
    const response = await fetch('http://localhost:9000/policy');
    if (!response.ok) throw new Error('Error al cargar política');
    policy.value = await response.text();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

onMounted(fetchPolicy);
</script>

<style scoped>
.policy-content pre {
  white-space: pre-wrap;
  font-family: inherit;
  padding: 1rem;
}
</style>
```

#### Opción 2: Options API

```vue
<template>
  <div class="policy-container">
    <h1>Política de Uso y Privacidad</h1>
    
    <div v-if="loading">Cargando...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else v-html="formattedPolicy"></div>
  </div>
</template>

<script>
import { marked } from 'marked'; // Instalar: npm install marked

export default {
  data() {
    return {
      policy: '',
      loading: true,
      error: null
    };
  },
  computed: {
    formattedPolicy() {
      return marked(this.policy);
    }
  },
  mounted() {
    this.loadPolicy();
  },
  methods: {
    async loadPolicy() {
      try {
        const response = await fetch('http://localhost:9000/policy');
        this.policy = await response.text();
      } catch (err) {
        this.error = 'No se pudo cargar la política';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

### JavaScript Vanilla

#### Opción 1: Básica

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Política de Uso</title>
  <style>
    #policy-content {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      white-space: pre-wrap;
      font-family: Arial, sans-serif;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div id="policy-content">Cargando política...</div>

  <script>
    const API_BASE = 'http://localhost:9000';

    async function loadPolicy() {
      try {
        const response = await fetch(`${API_BASE}/policy`);
        
        if (!response.ok) {
          throw new Error('Error al cargar la política');
        }
        
        const policyText = await response.text();
        document.getElementById('policy-content').textContent = policyText;
      } catch (error) {
        document.getElementById('policy-content').textContent = 
          'Error al cargar la política: ' + error.message;
      }
    }

    // Cargar al iniciar la página
    loadPolicy();
  </script>
</body>
</html>
```

#### Opción 2: Con Markdown Parser

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Política de Uso</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    .container {
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
    }
    .policy-content {
      line-height: 1.8;
    }
  </style>
</head>
<body>
  <div class="container">
    <div id="policy-content" class="policy-content">
      Cargando...
    </div>
  </div>

  <script>
    fetch('http://localhost:9000/policy')
      .then(response => response.text())
      .then(markdown => {
        const html = marked.parse(markdown);
        document.getElementById('policy-content').innerHTML = html;
      })
      .catch(error => {
        document.getElementById('policy-content').innerHTML = 
          '<p>Error al cargar la política.</p>';
        console.error('Error:', error);
      });
  </script>
</body>
</html>
```

#### Opción 3: Modal de Términos

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>ChatBot IA</title>
  <style>
    .modal {
      display: none;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0,0,0,0.5);
    }
    .modal.active {
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .modal-content {
      background-color: white;
      padding: 30px;
      border-radius: 8px;
      max-width: 700px;
      max-height: 80vh;
      overflow-y: auto;
    }
    .modal-actions {
      margin-top: 20px;
      display: flex;
      gap: 10px;
    }
    button {
      padding: 10px 20px;
      cursor: pointer;
    }
    #accept-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  </style>
</head>
<body>
  <div id="app">
    <h1>ChatBot IA - Universidad de Caldas</h1>
    <p>Por favor, acepta los términos para continuar.</p>
  </div>

  <div id="policy-modal" class="modal active">
    <div class="modal-content">
      <h2>Términos y Condiciones</h2>
      <div id="policy-text" style="white-space: pre-wrap; margin: 20px 0;">
        Cargando...
      </div>
      
      <label>
        <input type="checkbox" id="accept-checkbox"> 
        He leído y acepto la política de uso y privacidad
      </label>
      
      <div class="modal-actions">
        <button id="accept-btn" disabled>Aceptar y Continuar</button>
        <button id="reject-btn">Rechazar</button>
      </div>
    </div>
  </div>

  <script>
    const modal = document.getElementById('policy-modal');
    const policyText = document.getElementById('policy-text');
    const checkbox = document.getElementById('accept-checkbox');
    const acceptBtn = document.getElementById('accept-btn');
    const rejectBtn = document.getElementById('reject-btn');

    // Cargar política
    fetch('http://localhost:9000/policy')
      .then(res => res.text())
      .then(text => {
        policyText.textContent = text;
      })
      .catch(err => {
        policyText.textContent = 'Error al cargar la política.';
      });

    // Habilitar botón cuando se acepta checkbox
    checkbox.addEventListener('change', (e) => {
      acceptBtn.disabled = !e.target.checked;
    });

    // Aceptar términos
    acceptBtn.addEventListener('click', () => {
      localStorage.setItem('termsAccepted', 'true');
      modal.classList.remove('active');
      console.log('Términos aceptados');
    });

    // Rechazar términos
    rejectBtn.addEventListener('click', () => {
      alert('Debes aceptar los términos para usar el servicio');
    });

    // Verificar si ya aceptó anteriormente
    if (localStorage.getItem('termsAccepted') === 'true') {
      modal.classList.remove('active');
    }
  </script>
</body>
</html>
```

---

### Angular

```typescript
// policy.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PolicyService {
  private apiUrl = 'http://localhost:9000';

  constructor(private http: HttpClient) {}

  getPolicy(): Observable<string> {
    return this.http.get(`${this.apiUrl}/policy`, { 
      responseType: 'text' 
    });
  }
}

// policy.component.ts
import { Component, OnInit } from '@angular/core';
import { PolicyService } from './policy.service';

@Component({
  selector: 'app-policy',
  templateUrl: './policy.component.html',
  styleUrls: ['./policy.component.css']
})
export class PolicyComponent implements OnInit {
  policyText: string = '';
  loading: boolean = true;
  error: string | null = null;

  constructor(private policyService: PolicyService) {}

  ngOnInit(): void {
    this.policyService.getPolicy().subscribe({
      next: (text) => {
        this.policyText = text;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error al cargar la política';
        this.loading = false;
      }
    });
  }
}
```

```html
<!-- policy.component.html -->
<div class="policy-container">
  <h1>Política de Uso y Privacidad</h1>
  
  <div *ngIf="loading">Cargando...</div>
  <div *ngIf="error">{{ error }}</div>
  
  <pre *ngIf="!loading && !error" class="policy-content">
    {{ policyText }}
  </pre>
</div>
```

---

## 🎯 Casos de Uso Recomendados

### 1. Página Dedicada de Política
Ruta: `/politica` o `/terminos`
- Mostrar política completa
- Enlace en footer
- Enlace en menú "Acerca de"

### 2. Modal de Aceptación Inicial
- Mostrar al primer uso
- Requerir aceptación antes de usar el chat
- Guardar estado en `localStorage`

### 3. Footer con Enlace
```html
<footer>
  <a href="/politica">Política de Privacidad</a> | 
  <a href="/terminos">Términos de Uso</a>
</footer>
```

### 4. Sección en "Acerca de"
Incluir extractos de:
- Privacidad y datos
- Modelos de IA utilizados
- Limitaciones del servicio

---

## 🔧 Configuración Adicional

### CORS
El endpoint ya está configurado con CORS habilitado. No requiere configuración adicional.

### Cache
Recomendación: Cachear en frontend por 1 hora

```typescript
// Ejemplo con cache
const CACHE_KEY = 'chatbot-policy';
const CACHE_DURATION = 3600000; // 1 hora en ms

async function getCachedPolicy() {
  const cached = localStorage.getItem(CACHE_KEY);
  if (cached) {
    const { text, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp < CACHE_DURATION) {
      return text;
    }
  }
  
  const response = await fetch('http://localhost:9000/policy');
  const text = await response.text();
  
  localStorage.setItem(CACHE_KEY, JSON.stringify({
    text,
    timestamp: Date.now()
  }));
  
  return text;
}
```

---

## 📊 Ejemplo de Flujo Completo

```
Usuario visita sitio
       ↓
Verificar localStorage('termsAccepted')
       ↓
    No aceptado → Mostrar modal
       ↓
Fetch GET /policy
       ↓
Renderizar markdown en modal
       ↓
Usuario marca checkbox
       ↓
Botón "Aceptar" habilitado
       ↓
Click → Guardar en localStorage
       ↓
Cerrar modal → Permitir uso del chat
```

---

## ✅ Testing

### Prueba Manual
```bash
curl http://localhost:9000/policy
```

### Prueba desde Navegador
```javascript
fetch('http://localhost:9000/policy')
  .then(res => res.text())
  .then(console.log);
```

### Verificar Headers
```bash
curl -I http://localhost:9000/policy
```

Deberías ver:
```
HTTP/1.1 200 OK
content-type: text/plain; charset=utf-8
```

---

## 📚 Recursos Útiles

### Librerías de Markdown Recomendadas

**React:**
- `react-markdown`: Renderizado de markdown
- `remark-gfm`: Soporte para GitHub Flavored Markdown

**Vue:**
- `markdown-it`: Parser markdown
- `vue-markdown-render`: Componente Vue

**Angular:**
- `ngx-markdown`: Directiva Angular para markdown

**Vanilla JS:**
- `marked`: Parser markdown simple y rápido
- `markdown-it`: Parser completo y extensible

### Instalación

```bash
# React
npm install react-markdown remark-gfm

# Vue
npm install markdown-it

# Angular
npm install ngx-markdown marked
```

---

## 🚀 Ejemplo Completo: Aplicación React

```typescript
// App.tsx
import { useState, useEffect } from 'react';
import PolicyModal from './components/PolicyModal';
import ChatInterface from './components/ChatInterface';

function App() {
  const [termsAccepted, setTermsAccepted] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem('termsAccepted') === 'true';
    setTermsAccepted(accepted);
  }, []);

  const handleAccept = () => {
    localStorage.setItem('termsAccepted', 'true');
    setTermsAccepted(true);
  };

  const handleReject = () => {
    alert('Debes aceptar los términos para usar el servicio');
  };

  return (
    <div className="app">
      {!termsAccepted && (
        <PolicyModal 
          onAccept={handleAccept} 
          onReject={handleReject} 
        />
      )}
      
      {termsAccepted && <ChatInterface />}
    </div>
  );
}

export default App;
```

---

## 📝 Notas Importantes

1. **Versión:** La política está en versión 1.0.0 (19 nov 2025)
2. **Actualización:** Verificar periódicamente si hay nuevas versiones
3. **Idioma:** Contenido en español
4. **Formato:** Markdown con 224 líneas
5. **Encoding:** UTF-8
6. **Tamaño:** ~7.3 KB

---

## 🔗 Enlaces Relacionados

- **API Completa:** `API_FRONTEND.md`
- **Política Original:** `data/POLICY.md`
- **Estado del Proyecto:** `STATUS.md`
