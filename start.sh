#!/bin/bash
# Script para iniciar FastAPI con el puerto de Railway

# Railway inyecta la variable PORT
PORT=${PORT:-9000}

echo "🚀 Iniciando FastAPI en puerto $PORT"

# Iniciar uvicorn
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
