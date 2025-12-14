#!/bin/bash
# Script automatizado de despliegue Docker para Ubuntu 24
# Uso: bash deploy_docker.sh

set -e  # Salir si hay error

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 DESPLIEGUE AUTOMÁTICO - WASTE CLASSIFIER API DOCKER       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
PROJECT_NAME="waste-classifier"
IMAGE_NAME="$PROJECT_NAME:latest"
CONTAINER_NAME="waste-classifier-api"
PORT="8000"

# ==================== FUNCIONES ====================

step() {
    echo -e "${BLUE}▶${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ==================== VERIFICACIONES INICIALES ====================

echo -e "${YELLOW}=== PASO 1: VERIFICACIONES INICIALES ===${NC}"
echo ""

step "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado"
fi
success "Docker instalado: $(docker --version)"

step "Verificando Docker Compose..."
if ! docker compose version &> /dev/null; then
    error "Docker Compose no está instalado"
fi
success "Docker Compose instalado"

step "Verificando Docker daemon..."
if ! sudo docker ps &> /dev/null; then
    error "Docker daemon no está corriendo"
fi
success "Docker daemon corriendo"

step "Verificando archivos requeridos..."
REQUIRED_FILES=("Dockerfile" "compose.yml" "requirements.txt" ".env.example")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        error "Archivo requerido falta: $file"
    fi
done
success "Todos los archivos requeridos están presentes"

# ==================== CONFIGURACIÓN ====================

echo ""
echo -e "${YELLOW}=== PASO 2: CONFIGURACIÓN ===${NC}"
echo ""

# Verificar .env
if [ ! -f ".env" ]; then
    step "Creando .env desde .env.example..."
    cp .env.example .env
    success ".env creado"
else
    success ".env ya existe"
fi

# Mostrar configuración
step "Configuración actual:"
echo ""
if [ -f ".env" ]; then
    grep -E "^(MODEL_PATH|LOG_LEVEL|CONFIDENCE_THRESHOLD)" .env || true
fi
echo ""

read -p "¿Deseas editar .env? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vi &> /dev/null; then
        vi .env
    else
        warning "No hay editor disponible, saltando edición"
    fi
fi

# ==================== DETENER CONTENEDORES EXISTENTES ====================

echo ""
echo -e "${YELLOW}=== PASO 3: LIMPIEZA DE CONTENEDORES ANTERIORES ===${NC}"
echo ""

step "Verificando contenedores existentes..."
if docker compose ps 2>/dev/null | grep -q "waste-classifier"; then
    warning "Contenedor anterior encontrado, deteniendo..."
    docker compose down
    success "Contenedor anterior detenido"
else
    success "No hay contenedores anteriores"
fi

# ==================== CONSTRUCCIÓN DE IMAGEN ====================

echo ""
echo -e "${YELLOW}=== PASO 4: CONSTRUCCIÓN DE IMAGEN DOCKER ===${NC}"
echo ""

step "Construyendo imagen Docker..."
docker compose build

if [ $? -eq 0 ]; then
    success "Imagen construida exitosamente"
else
    error "Error al construir la imagen"
fi

# Mostrar información de la imagen
step "Información de la imagen:"
docker images | grep waste-classifier || true

# ==================== INICIAR CONTENEDOR ====================

echo ""
echo -e "${YELLOW}=== PASO 5: INICIANDO CONTENEDOR ===${NC}"
echo ""

step "Iniciando servicios con Docker Compose..."
docker compose up -d

if [ $? -eq 0 ]; then
    success "Servicios iniciados"
else
    error "Error al iniciar servicios"
fi

# Esperar a que la API esté lista
step "Esperando a que la API esté lista..."
sleep 3

# ==================== VERIFICACIONES POSTERIORES ====================

echo ""
echo -e "${YELLOW}=== PASO 6: VERIFICACIONES POSTERIORES ===${NC}"
echo ""

# Verificar que el contenedor está corriendo
step "Verificando estado del contenedor..."
if docker compose ps | grep -q "Up"; then
    success "Contenedor está corriendo"
else
    error "Contenedor no está corriendo"
fi

# Verificar puerto
step "Verificando puerto $PORT..."
if curl -s http://localhost:$PORT/health &> /dev/null; then
    success "API respondiendo en puerto $PORT"
else
    warning "API no responde aún, esperando..."
    sleep 3
    if curl -s http://localhost:$PORT/health &> /dev/null; then
        success "API respondiendo en puerto $PORT"
    else
        warning "API aún no responde - puede tardar más"
    fi
fi

# Ver logs iniciales
step "Últimos logs de la API:"
echo ""
docker compose logs --tail 10
echo ""

# ==================== PRUEBAS ====================

echo ""
echo -e "${YELLOW}=== PASO 7: PRUEBAS BÁSICAS ===${NC}"
echo ""

step "Test 1: Health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:$PORT/health 2>/dev/null || echo '{}')
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    success "Health check: OK"
else
    warning "Health check no respondió como esperado"
fi

step "Test 2: Swagger UI..."
if curl -s http://localhost:$PORT/docs &> /dev/null; then
    success "Swagger UI: Accesible en http://localhost:$PORT/docs"
else
    warning "Swagger UI: No responde aún"
fi

step "Test 3: Estado del contenedor..."
docker compose ps

# ==================== INSTRUCCIONES FINALES ====================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo -e "║${GREEN}   ✓ DESPLIEGUE COMPLETADO${NC}"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${GREEN}┌─ ACCESO A LA API${NC}"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}│${NC}  📍 Documentación Swagger:"
echo -e "${GREEN}│${NC}     http://localhost:$PORT/docs"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}│${NC}  📍 Health Check:"
echo -e "${GREEN}│${NC}     curl http://localhost:$PORT/health"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}│${NC}  📍 Predicción (ejemplo):"
echo -e "${GREEN}│${NC}     curl -X POST http://localhost:$PORT/predict \\"
echo -e "${GREEN}│${NC}       -H 'Content-Type: multipart/form-data' \\"
echo -e "${GREEN}│${NC}       -F 'file=@image.jpg'"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}└─${NC}"
echo ""

echo -e "${GREEN}┌─ COMANDOS ÚTILES${NC}"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}│${NC}  Ver logs en tiempo real:"
echo -e "${GREEN}│${NC}     docker compose logs -f"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}│${NC}  Entrar en el contenedor:"
echo -e "${GREEN}│${NC}     docker compose exec api bash"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}│${NC}  Detener servicios:"
echo -e "${GREEN}│${NC}     docker compose down"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}│${NC}  Ver estado:"
echo -e "${GREEN}│${NC}     docker compose ps"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}└─${NC}"
echo ""

echo -e "${GREEN}┌─ PRÓXIMOS PASOS${NC}"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}│${NC}  1. Abre: http://localhost:$PORT/docs"
echo -e "${GREEN}│${NC}  2. Prueba un endpoint"
echo -e "${GREEN}│${NC}  3. (Opcional) Configura SSL/TLS"
echo -e "${GREEN}│${NC}  4. (Opcional) Configura reverse proxy"
echo -e "${GREEN}│${NC}"
echo -e "${GREEN}└─${NC}"
echo ""

# Ofertar más información
read -p "¿Ver logs completos? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    docker compose logs
fi

success "¡Despliegue completado exitosamente!"
echo ""
