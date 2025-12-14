# ⚡ Quick Start Docker - Ubuntu 24

Guía de 5 minutos para desplegar en Ubuntu 24 sin complicaciones.

---

## 🚀 Opción 1: Despliegue Automático (RECOMENDADO)

```bash
# 1. Clona el repositorio
git clone https://github.com/Darioxavierl/clasifier-server.git
cd clasifier-server

# 2. Verifica que todo está listo
bash verify_docker_deployment.sh

# 3. Despliega automáticamente
bash deploy_docker.sh

# ✓ Listo! API en http://localhost:8000/docs
```

**Tiempo total:** 5-10 minutos (depende del ancho de banda)

---

## 🔧 Opción 2: Despliegue Manual

```bash
# 1. Clona
git clone https://github.com/Darioxavierl/clasifier-server.git
cd clasifier-server

# 2. Copia configuración
cp .env.example .env

# 3. Construye imagen
docker compose build

# 4. Inicia servicios
docker compose up -d

# 5. Verifica que funciona
curl http://localhost:8000/health

# ✓ Abre http://localhost:8000/docs en navegador
```

**Tiempo total:** 5-15 minutos

---

## ✅ Verificaciones Rápidas

```bash
# ¿Funciona?
curl http://localhost:8000/health

# ¿Qué IP tengo?
hostname -I

# ¿Desde otra máquina?
curl http://<TU_IP>:8000/health

# Ver logs
docker compose logs -f

# 🔒 Verificar usuario no-root (SEGURIDAD)
docker exec waste-classifier-api whoami
# Output esperado: appuser (NOT root)

# Detener
docker compose down
```

---

## 📝 Requisitos Previos

Antes de clonar, instala:

```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Docker
sudo apt-get install -y docker.io docker-compose
sudo systemctl start docker

# Git
sudo apt-get install -y git

# (Opcional) Permite usar docker sin sudo
sudo usermod -aG docker $USER
# Cierra sesión y vuelve a conectar
```

---

## 🐛 Si Algo Falla

1. **Ejecuta verificación:**
   ```bash
   bash verify_docker_deployment.sh
   ```

2. **Ve los logs:**
   ```bash
   docker compose logs | tail -50
   ```

3. **Revisa guía completa:**
   - DOCKER_UBUNTU_GUIDE.md (detallado)
   - TROUBLESHOOTING_DOCKER.md (problemas comunes)

---

## 🎯 Próximos Pasos

**Usar la API:**
- Abre: http://localhost:8000/docs
- Prueba un endpoint
- Descarga la respuesta

**Acceder desde otra máquina:**
```bash
# En la otra máquina:
curl http://<IP_SERVIDOR>:8000/health
# Reemplaza <IP_SERVIDOR> con tu IP
```

**Producción:**
- Lee: DOCKER_UBUNTU_GUIDE.md (sección "Siguientes Pasos")
- Configura SSL/TLS
- Configura reverse proxy
- Configura monitoreo

---

## 💡 Tips

```bash
# Ver estado en tiempo real
docker stats

# Entrar en contenedor (debug)
docker compose exec api bash

# Logs con busqueda
docker compose logs | grep "error"

# Reiniciar servicios
docker compose restart

# Ver configuración
cat .env
```

---

**¿Preguntas?** Revisa la documentación completa:
- 📖 DOCKER_UBUNTU_GUIDE.md
- 🔧 TROUBLESHOOTING_DOCKER.md
- 📚 README.md
