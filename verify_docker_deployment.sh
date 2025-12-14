#!/bin/bash
# Script de verificación pre-despliegue para Ubuntu 24
# Uso: bash verify_docker_deployment.sh

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🐳 VERIFICACIÓN PRE-DESPLIEGUE DOCKER - UBUNTU 24           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0

# Función para imprimir resultados
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

check_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ==================== VERIFICACIONES DE SISTEMA ====================
echo -e "${YELLOW}=== VERIFICACIÓN DE SISTEMA ===${NC}"
echo ""

# Verificar SO
if grep -qi "ubuntu.*24" /etc/os-release 2>/dev/null; then
    check_pass "Sistema: Ubuntu 24.04 detectado"
else
    check_fail "Sistema: No es Ubuntu 24.04 (puede funcionar igual)"
fi

# Verificar Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    check_pass "Docker: Instalado - $DOCKER_VERSION"
else
    check_fail "Docker: NO está instalado"
    check_info "Instala Docker: curl -fsSL https://get.docker.com | sudo sh"
fi

# Verificar Docker Compose
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version 2>&1 | head -1)
    check_pass "Docker Compose: Instalado - $COMPOSE_VERSION"
else
    check_fail "Docker Compose: NO está instalado"
    check_info "Instala Compose: sudo apt-get install -y docker-compose"
fi

# Verificar que Docker está corriendo
if command -v docker &> /dev/null; then
    if sudo docker ps &> /dev/null; then
        check_pass "Docker daemon: Corriendo"
    else
        check_fail "Docker daemon: NO está corriendo"
        check_info "Inicia Docker: sudo systemctl start docker"
    fi
fi

# Verificar Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    check_pass "Git: Instalado - $GIT_VERSION"
else
    check_fail "Git: NO está instalado"
    check_info "Instala Git: sudo apt-get install -y git"
fi

# ==================== VERIFICACIONES DE ARCHIVOS ====================
echo ""
echo -e "${YELLOW}=== VERIFICACIÓN DE ARCHIVOS ===${NC}"
echo ""

FILES_REQUIRED=("Dockerfile" "compose.yml" "requirements.txt" ".env.example")

for file in "${FILES_REQUIRED[@]}"; do
    if [ -f "$file" ]; then
        check_pass "Archivo: $file existe"
    else
        check_fail "Archivo: $file FALTA"
    fi
done

# Verificar directorios
DIRS_REQUIRED=("app" "models" "logs")

for dir in "${DIRS_REQUIRED[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directorio: $dir existe"
    else
        check_fail "Directorio: $dir FALTA"
    fi
done

# Verificar archivos en app
APP_FILES=("app/main.py" "app/config.py" "app/api/routes.py")

for file in "${APP_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "Archivo app: $file existe"
    else
        check_fail "Archivo app: $file FALTA"
    fi
done

# Verificar modelos
if [ -f "models/mobilenetv2_waste.h5" ]; then
    MODEL_SIZE=$(ls -lh models/mobilenetv2_waste.h5 | awk '{print $5}')
    check_pass "Modelo TensorFlow: Existe ($MODEL_SIZE)"
elif [ -f "models/mobilenetv2_waste_pytorch.pth" ]; then
    MODEL_SIZE=$(ls -lh models/mobilenetv2_waste_pytorch.pth | awk '{print $5}')
    check_pass "Modelo PyTorch: Existe ($MODEL_SIZE)"
else
    check_fail "Modelos: NO hay modelos .h5 o .pth"
fi

# ==================== VERIFICACIÓN DE .env ====================
echo ""
echo -e "${YELLOW}=== VERIFICACIÓN DE CONFIGURACIÓN ===${NC}"
echo ""

if [ -f ".env" ]; then
    check_pass "Configuración: .env existe"
    
    # Verificar variables importantes
    if grep -q "MODEL_PATH" .env; then
        MODEL_PATH=$(grep "^MODEL_PATH=" .env | cut -d '=' -f2)
        check_pass "Configuración: MODEL_PATH definido ($MODEL_PATH)"
    else
        check_fail "Configuración: MODEL_PATH no está definido"
    fi
else
    if [ -f ".env.example" ]; then
        check_info "Configuración: .env no existe pero .env.example sí"
        check_info "Debes copiar: cp .env.example .env"
    else
        check_fail "Configuración: Ni .env ni .env.example existen"
    fi
fi

# ==================== VERIFICACIÓN DE DOCKERFILE ====================
echo ""
echo -e "${YELLOW}=== VERIFICACIÓN DE DOCKERFILE ===${NC}"
echo ""

if [ -f "Dockerfile" ]; then
    if grep -q "FROM python" Dockerfile; then
        check_pass "Dockerfile: Estructura base válida"
    else
        check_fail "Dockerfile: Estructura inválida"
    fi
    
    if grep -q "EXPOSE 8000" Dockerfile; then
        check_pass "Dockerfile: Puerto 8000 expuesto"
    else
        check_fail "Dockerfile: Puerto 8000 NO expuesto"
    fi
    
    if grep -q "requirements.txt" Dockerfile; then
        check_pass "Dockerfile: requirements.txt incluido"
    else
        check_fail "Dockerfile: requirements.txt NO incluido"
    fi
fi

# ==================== VERIFICACIÓN DE COMPOSE ====================
echo ""
echo -e "${YELLOW}=== VERIFICACIÓN DE DOCKER COMPOSE ===${NC}"
echo ""

if [ -f "compose.yml" ]; then
    if grep -q "services:" compose.yml; then
        check_pass "Compose: Estructura válida"
    else
        check_fail "Compose: Estructura inválida"
    fi
    
    if grep -q "ports:" compose.yml && grep -q "8000" compose.yml; then
        check_pass "Compose: Puerto 8000 mapeado"
    else
        check_fail "Compose: Puerto 8000 NO mapeado"
    fi
    
    if grep -q "volumes:" compose.yml; then
        check_pass "Compose: Volúmenes configurados"
    else
        check_info "Compose: Sin volúmenes (pueden agregarse)"
    fi
fi

# ==================== VERIFICACIÓN DE PUERTOS ====================
echo ""
echo -e "${YELLOW}=== VERIFICACIÓN DE PUERTOS ===${NC}"
echo ""

if command -v netstat &> /dev/null; then
    if sudo netstat -tlnp 2>/dev/null | grep -q ":8000"; then
        check_fail "Puerto 8000: YA ESTÁ EN USO"
        check_info "Usa otro puerto o mata el proceso"
    else
        check_pass "Puerto 8000: Disponible"
    fi
else
    if command -v ss &> /dev/null; then
        if sudo ss -tlnp 2>/dev/null | grep -q ":8000"; then
            check_fail "Puerto 8000: YA ESTÁ EN USO"
        else
            check_pass "Puerto 8000: Disponible"
        fi
    else
        check_info "Puerto 8000: No se pudo verificar (herramientas no disponibles)"
    fi
fi

# ==================== VERIFICACIÓN DE GIT ====================
echo ""
echo -e "${YELLOW}=== VERIFICACIÓN DE GIT ===${NC}"
echo ""

if [ -d ".git" ]; then
    check_pass "Git: Repositorio local existe"
    
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ "$CURRENT_BRANCH" = "main" ]; then
        check_pass "Git: En rama main"
    else
        check_info "Git: En rama $CURRENT_BRANCH (deberías estar en main)"
    fi
else
    check_info "Git: No clonado (puedes clonarlo más tarde)"
fi

# ==================== INFORMACIÓN DEL SISTEMA ====================
echo ""
echo -e "${YELLOW}=== INFORMACIÓN DEL SISTEMA ===${NC}"
echo ""

check_info "RAM disponible: $(free -h | awk 'NR==2 {print $7}')"
check_info "Espacio en disco: $(df -h . | awk 'NR==2 {print $4}')"
check_info "CPU cores: $(nproc)"
check_info "Kernel: $(uname -r)"

# ==================== RESUMEN ====================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo -e "║${GREEN}   VERIFICACIÓN COMPLETADA${NC}"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Verificaciones pasadas: $CHECKS_PASSED${NC}"
echo -e "${RED}✗ Verificaciones fallidas: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ TODO LISTO PARA DESPLEGAR${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "  1. docker compose build"
    echo "  2. docker compose up -d"
    echo "  3. curl http://localhost:8000/health"
    echo ""
    exit 0
else
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}✗ HAY PROBLEMAS - REVISA ARRIBA${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    exit 1
fi
