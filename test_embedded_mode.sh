#!/bin/bash

# Script para probar ChromaDB en modo embebido (simulando producción)

echo "🧪 Probando modo embebido de ChromaDB..."
echo ""

# Detener servicios actuales
echo "1️⃣ Deteniendo docker-compose..."
docker-compose down

# Construir imagen con configuración de producción
echo ""
echo "2️⃣ Construyendo imagen para producción..."
docker build -f docker/Dockerfile.api -t chatbot-api-prod .

# Ejecutar contenedor en modo embebido
echo ""
echo "3️⃣ Ejecutando en modo embebido..."
docker run -d --name test-embedded \
  -p 9001:9000 \
  -v $(pwd)/data:/data \
  -e USE_EMBEDDED_CHROMA=true \
  -e CHROMA_PERSIST_DIR=/data/vector_store \
  -e MODE=production \
  -e GOOGLE_API_KEY=${GOOGLE_API_KEY} \
  chatbot-api-prod

# Esperar a que inicie
echo ""
echo "4️⃣ Esperando 10 segundos para que inicie..."
sleep 10

# Probar endpoint
echo ""
echo "5️⃣ Probando endpoint raíz..."
curl -s http://localhost:9001/ | python3 -m json.tool

echo ""
echo ""
echo "6️⃣ Probando consulta al chatbot..."
curl -s -X POST http://localhost:9001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué es la IA ética?",
    "model": "gemini",
    "response_mode": "brief"
  }' | python3 -m json.tool | head -30

# Ver logs
echo ""
echo ""
echo "7️⃣ Logs del contenedor:"
docker logs test-embedded | tail -20

echo ""
echo ""
echo "✅ Prueba completada. Para limpiar:"
echo "   docker stop test-embedded && docker rm test-embedded"
echo ""
echo "Para volver a desarrollo:"
echo "   docker-compose up -d"
