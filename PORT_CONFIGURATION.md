# 🔧 Configuración Dinámica de Puerto (PORT)

## ¿Cómo funciona?

El sistema está **completamente preparado** para cambiar el puerto desde la variable `.env`. Los cambios se propagan en todas las capas:

```
.env (PORT=8080)
    ↓
Dockerfile (ENV PORT y EXPOSE)
    ↓
compose.yml (${PORT} en ports)
    ↓
app/config.py (PORT en Settings)
    ↓
app.main:app (accesible en puerto)
```

---

## 📝 Pasos para Cambiar el Puerto

### 1. En tu `.env` local (Desarrollo)

```bash
# .env
PORT=8080
HOST=0.0.0.0
```

Luego ejecuta:
```bash
# Desarrollo con uvicorn
python run.py --port 8080

# O con compose
docker compose up -d
# Automáticamente usará PORT=8080 del .env
```

### 2. En tu servidor (Ubuntu 24 Docker)

```bash
# En Ubuntu, edita el .env
nano .env

# Busca esta sección y cambia:
PORT=9000          # Cambiar de 8000 a 9000 (ejemplo)
HOST=0.0.0.0

# Guarda (Ctrl+O, Enter, Ctrl+X)
```

Luego ejecuta:
```bash
# Reconstruir imagen (toma los ENV del Dockerfile)
docker compose down
docker compose build
docker compose up -d

# Verifica
curl http://localhost:9000/health
```

---

## 🔄 Flujo de la Configuración

### Desarrollo Local (sin Docker)

```python
# run.py - Lee argumentos CLI
python run.py --port 8080

# app/config.py - Lee .env
PORT: int = 8000  # default, se sobrescribe por .env si existe

# app/main.py - Ejecuta en puerto
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

**Prioridad:**
1. CLI argument (más alta prioridad): `--port 8080`
2. Variable `.env`: `PORT=8000`
3. Default en código: `8000` (si no hay .env)

### Docker (Producción - Ubuntu)

```dockerfile
# Dockerfile
ENV PORT=8000           # Default
EXPOSE ${PORT}          # Expone el puerto
CMD ["sh", "-c", "uvicorn ... --port ${PORT}"]
```

```yaml
# compose.yml
environment:
  - PORT=${PORT:-8000}  # Lee del .env, default 8000
  
command: uvicorn app.main:app --host ${HOST} --port ${PORT}

ports:
  - "${PORT:-8000}:${PORT:-8000}"  # Mapea puerto
```

---

## ✅ Archivos Configurados

| Archivo | Cambio | Detalle |
|---------|--------|---------|
| `.env.example` | ✅ | `PORT=8000` y `HOST=0.0.0.0` |
| `app/config.py` | ✅ | `PORT: int = 8000` y `HOST: str = "0.0.0.0"` |
| `compose.yml` | ✅ | `${PORT:-8000}` en ports y command |
| `Dockerfile` | ✅ | `ENV PORT=8000` y `EXPOSE ${PORT}` |
| `run.py` | ✅ | Ya soporta `--port` como argumento |

---

## 🔍 Verificación

### En Desarrollo

```bash
# Ver que está usando el puerto correcto
python run.py --port 9000
# Log esperado: "Accede a: http://127.0.0.1:9000"

# Desde otra terminal
curl http://localhost:9000/health
# Output: {"status": "healthy", ...}
```

### En Docker

```bash
# Ver que está usando el puerto correcto
docker compose up -d
docker logs <container_id>
# Log esperado: "Uvicorn running on http://0.0.0.0:8000"

# Verificar en host
curl http://localhost:8000/health

# O si cambiaste a 9000
curl http://localhost:9000/health
```

---

## 📋 Checklist

- [x] `.env.example` tiene `PORT=8000`
- [x] `app/config.py` lee `PORT` de `.env`
- [x] `compose.yml` usa `${PORT:-8000}` en ports
- [x] `compose.yml` pasa `PORT` al comando uvicorn
- [x] `Dockerfile` define `ENV PORT` y usa `${PORT}`
- [x] Puedes cambiar `.env` y Docker lo toma automáticamente
- [x] Backwards compatible (si no hay PORT, usa 8000)

---

## 🚀 Ejemplo Completo: Cambiar a Puerto 9000

### En Ubuntu 24:

```bash
# 1. Editar .env
nano .env
# Cambiar: PORT=9000

# 2. Reconstruir
docker compose down
docker compose build

# 3. Desplegar
docker compose up -d

# 4. Verificar
curl http://localhost:9000/health

# 5. Ver logs
docker compose logs -f
```

### En Windows/Desarrollo:

```bash
# Opción 1: Con CLI
python run.py --port 9000

# Opción 2: Con .env
# Editar .env: PORT=9000
python run.py
# Toma PORT del .env automáticamente

# Opción 3: Con Docker local
docker compose up -d
# Toma PORT del .env: 9000
```

---

## ⚠️ Notas Importantes

1. **Docker requiere reconstrucción** si cambias PORT en Dockerfile
   - El `EXPOSE ${PORT}` se evalúa en build time
   - Mejor: cambiar en `.env` y docker-compose lo maneja

2. **El puerto debe estar disponible**
   ```bash
   # Ver qué usa puerto 8000
   sudo lsof -i :8000
   
   # Ver puertos en uso
   sudo netstat -tlnp | grep LISTEN
   ```

3. **Firewall en Ubuntu**
   ```bash
   # Abrir puerto
   sudo ufw allow 8000
   sudo ufw allow 9000
   
   # Ver reglas
   sudo ufw status
   ```

4. **Acceso desde otra máquina**
   ```bash
   # Desde otra máquina en la red
   curl http://<IP_SERVIDOR>:9000/health
   # Reemplaza IP_SERVIDOR con tu IP de Ubuntu
   ```

---

## 🔐 Seguridad

- ✅ User no-root (`appuser`) ejecuta el proceso
- ✅ Puerto configurable sin modificar código
- ✅ Valores por defecto seguros
- ✅ `.env` no se comitea a Git (en `.gitignore`)

---

**Última actualización:** 2025-12-14  
**Versión:** 1.0
