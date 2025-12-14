#!/bin/bash

# Script de Diagnóstico - Docker en Ubuntu
# Ayuda a identificar por qué Docker está en estado "Restarting"

echo "🔍 DIAGNÓSTICO DOCKER - WASTE CLASSIFIER"
echo "========================================"
echo ""

# 1. Ver estado del contenedor
echo "📋 Estado del Contenedor:"
sudo docker ps -a | grep waste-classifier
echo ""

# 2. Ver logs completos
echo "📝 Últimos Logs (últimas 100 líneas):"
sudo docker logs waste-classifier-api --tail 100
echo ""

# 3. Ver si la imagen existe
echo "🖼️  Imágenes disponibles:"
sudo docker images | grep clasifier
echo ""

# 4. Ver espacio en disco
echo "💾 Espacio en disco:"
df -h | grep -E "Filesystem|/$"
echo ""

# 5. Ver memoria disponible
echo "🧠 Memoria disponible:"
free -h | head -3
echo ""

# 6. Ver procesos de Docker
echo "⚙️  Procesos del contenedor:"
sudo docker top waste-classifier-api 2>/dev/null || echo "   Contenedor no está corriendo"
echo ""

# 7. Intentar ver el error específico
echo "🔴 Intentando reiniciar y capturar error..."
echo ""
sudo docker compose down
sleep 2
echo "Levantando contenedor..."
sudo docker compose up -d
sleep 3
echo ""
echo "Estado actual:"
sudo docker ps | grep waste-classifier
echo ""
echo "Últimos logs (primeras líneas con error):"
sudo docker logs waste-classifier-api 2>&1 | head -50
echo ""

echo "✅ Diagnóstico completado"
echo ""
echo "PRÓXIMOS PASOS:"
echo "1. Si ves 'ModuleNotFoundError' → pip install falta"
echo "2. Si ves 'Port already in use' → otro proceso usa el puerto"
echo "3. Si ves 'No space left' → disco lleno"
echo "4. Si ves 'Out of memory' → memoria insuficiente"
echo "5. Si ves error de config → .env tiene problemas"
echo ""
echo "Contacta con el log completo si necesitas ayuda"
