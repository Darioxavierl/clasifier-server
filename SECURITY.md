# 🔒 Políticas de Seguridad - Docker & Producción

## Usuario No-Root (Crítico)

### ¿Por qué?
Ejecutar contenedores como `root` es un riesgo de seguridad. Si se compromete la aplicación, el atacante tendría acceso total al sistema.

### ¿Cómo está configurado?

**Usuario del contenedor:**
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

- **Usuario:** `appuser`
- **UID:** 1000 (usuario regular, no root que es 0)
- **Permisos:** Solo en `/code` (directorio de la aplicación)
- **Proceso ejecutado:** Bajo `appuser`, no `root`

### Verificar en tu servidor

```bash
# Ver el usuario del contenedor en ejecución
docker exec waste-classifier-api whoami
# Output esperado: appuser

# Ver proceso con detalles de usuario
docker top waste-classifier-api
# Busca: UID 1000 en lugar de 0

# Alternativa - inspeccionar imagen
docker image inspect clasifier-server:latest | grep -i user
```

### Qué NO puede hacer `appuser`

❌ Modificar `/etc/passwd` (usuarios del sistema)  
❌ Acceder a otros contenedores  
❌ Ejecutar comandos privilegiados (sin sudo, que no tiene)  
❌ Instalar paquetes del sistema  
❌ Acceder a archivos fuera de `/code`  

### Qué SÍ puede hacer `appuser`

✅ Ejecutar la aplicación FastAPI  
✅ Leer/escribir en `/code/app`  
✅ Leer/escribir en `/code/models`  
✅ Crear/leer/escribir logs en `/code/logs`  
✅ Acceder a variables de entorno  

---

## Otros Puntos de Seguridad

### 1. Volume Permissions (Logs)

```bash
# Los logs se guardan en volumen persistente
# Propiedad: appuser:appuser (UID 1000:1000)
ls -la /code/logs

# El contenedor puede leer/escribir sin problemas
# El host puede gestionar archivos si se necesita
```

### 2. Variables de Entorno

Usar `.env` para secretos y configuración:

```bash
# ❌ MAL - secretos en texto plano en Dockerfile
ENV API_KEY=sk-1234567890

# ✅ BIEN - cargar desde .env
cp .env.example .env
# Editar .env con valores reales (NO commitear a git)
```

### 3. Red - Aislamiento de Puertos

```bash
# Solo exponer puerto 8000 (API)
EXPOSE 8000

# Accesible desde:
# - localhost:8000 (en el mismo servidor)
# - 192.168.x.x:8000 (desde otros equipos en red)
# - No expone acceso a base de datos o internos
```

### 4. Dockerfile - Minimizar Capas

```dockerfile
# ✅ BIEN - Una capa RUN
RUN apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*

# ❌ MAL - Múltiples capas RUN
RUN apt-get update
RUN apt-get install -y ...
```

### 5. .dockerignore - No incluir innecesarios

```
.venv/          # Entorno virtual
.git/           # Repositorio
tests/          # Tests no necesarios en producción
.env            # Archivos de secretos (usar compose.yml para vars)
*.md            # Documentación
```

---

## Checklist de Seguridad para Producción

- [ ] Usuario no-root configurado (appuser)
- [ ] `docker exec <container> whoami` retorna `appuser`
- [ ] `.env` NO incluido en repositorio (en `.gitignore`)
- [ ] `.env` creado en servidor con valores de producción
- [ ] Logs almacenados en volumen persistente
- [ ] Puerto 8000 accesible solo a clientes autorizados
- [ ] Docker daemon protegido (acceso limitado)
- [ ] Firewall configurado en Ubuntu (ufw)
- [ ] Updates de dependencias al día (requirements.txt)
- [ ] HTTPS/TLS habilitado (Nginx reverse proxy recomendado)

---

## Recursos de Seguridad Docker

- [CIS Docker Benchmark](https://www.cisecurity.org/cis-benchmarks/)
- [OWASP Container Security](https://owasp.org/www-project-container-security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

## Contacto & Soporte

Si encuentras vulnerabilidades de seguridad, reporta confidencialmente.

---

**Última actualización:** 2025-12-14  
**Versión Dockerfile:** 1.1 (con usuario no-root)
