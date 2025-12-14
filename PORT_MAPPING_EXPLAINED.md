# 🔌 Puerto 8000 vs 8900 - Entendiendo Port Mapping en Docker

## El Problema Observado

```
CONTAINER ID   PORTS                    NAMES
6c6470456b50   8000/tcp, 0.0.0.0:8900->8900/tcp    waste-classifier-api
```

¿Por qué aparecen dos puertos? ¿Cuál debería usar?

---

## 🎯 Explicación Simple

### Mapeo de Puertos en Docker

```
HOST (tu servidor Ubuntu)
    ↓ (port 8900)
    └─→ Docker Container
        └─→ uvicorn escucha en 8900
```

**El mapeo `8900:8900` significa:**
- **8900** (izquierda) = Puerto en el HOST (tu Ubuntu)
- **8900** (derecha) = Puerto dentro del contenedor

### ✅ Acceso Correcto

```bash
# Desde tu servidor Ubuntu:
curl http://localhost:8900/health    # ✅ CORRECTO
curl http://localhost:8000/health    # ❌ INCORRECTO

# Desde otra máquina en la red:
curl http://192.168.x.x:8900/health  # ✅ CORRECTO
```

---

## 🔍 El "8000/tcp" en docker ps

```
8000/tcp, 0.0.0.0:8900->8900/tcp
└─ Esto es confuso porque:
   - 8000/tcp = el EXPOSE en Dockerfile (solo informativo)
   - 0.0.0.0:8900->8900/tcp = el mapeo real (activo)
```

**Explicación técnica:**

1. **EXPOSE 8000** en Dockerfile es **solo documentación**
   - No bloquea o permite puertos
   - Es informativo para el desarrollador
   - No afecta el funcionamiento real

2. **El puerto real** es el que define `uvicorn --port 8900`
   - Viene de la variable PORT en .env
   - Se mapea en docker-compose.yml
   - Es lo que realmente funciona

---

## 📋 Cómo Funciona el Sistema Actual

### En Ubuntu (en el servidor)

```bash
# 1. Tu .env tiene:
PORT=8900
HOST=0.0.0.0

# 2. compose.yml lee tu .env y ejecuta:
ports:
  - "8900:8900"    # Mapea puerto 8900 del host → 8900 del contenedor

# 3. Dockerfile establece:
ENV PORT=8000              # Default (si no hay .env)
EXPOSE 8000                # Solo informativo

# 4. compose.yml ejecuta:
command: uvicorn app.main:app --host 0.0.0.0 --port 8900
                                              ↑
                                        Lee de .env
```

### El Flujo Completo

```
.env (PORT=8900)
  ↓
compose.yml lee ${PORT}
  ├─ ports: 8900:8900
  └─ command: ... --port 8900
    ↓
uvicorn escucha en 8900 dentro del contenedor
  ↓
docker mapea: HOST:8900 → CONTAINER:8900
  ↓
Accedes desde: curl http://localhost:8900
```

---

## ✅ Verificación en Ubuntu

### Ver qué puerto realmente está usando

```bash
# Ver puerto mapeado
docker ps
# Output: 0.0.0.0:8900->8900/tcp  ← Puerto real (activo)

# Ver configuración del contenedor
docker inspect waste-classifier-api | grep -A 10 PortBindings

# Ver logs del contenedor
docker logs waste-classifier-api | grep -i "uvicorn"
# Debería mostrar: "Uvicorn running on http://0.0.0.0:8900"

# Verificar que escucha en 8900
docker exec waste-classifier-api ss -tlnp
# Output: LISTEN 0.0.0.0:8900 (appuser)
```

### Probar conectividad

```bash
# Desde el servidor (localhost)
curl http://localhost:8900/health

# Desde otra máquina (reemplaza IP)
curl http://192.168.1.100:8900/health

# Ver que responde
echo "Conexión exitosa" > /tmp/test.txt
```

---

## 🐛 Si Algo No Funciona

### Problema 1: "Connection refused en 8000"

```bash
# ❌ INCORRECTO - puerto no mapeado
curl http://localhost:8000/health
# Connection refused

# ✅ CORRECTO - usa el puerto mapeado
curl http://localhost:8900/health
# {"status": "healthy"}
```

**Solución:** Usa siempre el puerto del HOST (el que aparece en `docker ps`)

### Problema 2: "8000/tcp" sigue apareciendo en docker ps

```bash
# Esto es normal y esperado:
# - 8000/tcp = EXPOSE en Dockerfile (informativo, no activo)
# - 0.0.0.0:8900->8900/tcp = Mapeo real (activo)

# NO es un error, es solo información adicional
```

**Solución:** Ignora el "8000/tcp". Usa el puerto del mapeo activo (8900).

### Problema 3: Querré cambiar a puerto 8080

```bash
# En Ubuntu:
nano .env
# Cambiar: PORT=8080

# Reconstruir
docker compose down
docker compose build --no-cache
docker compose up -d

# Verificar nuevo puerto
docker ps
# Output: 0.0.0.0:8080->8080/tcp

# Acceder
curl http://localhost:8080/health
```

---

## 📊 Tabla de Referencia

| Elemento | Valor | Dónde | Función |
|----------|-------|-------|---------|
| EXPOSE | 8000 | Dockerfile | Documentación (no activo) |
| ENV PORT | 8000 | Dockerfile | Default si no hay .env |
| PORT | 8900 | .env en Ubuntu | Variable que usa compose |
| ports | 8900:8900 | compose.yml | Mapeo HOST:CONTAINER |
| uvicorn | --port 8900 | compose.yml | Puerto real que escucha app |
| Acceso | localhost:8900 | Tu navegador | Puerto para conectar |

---

## 🔐 Seguridad & Best Practices

✅ **Lo que está bien:**
- Variable PORT en .env (configurable)
- EXPOSE es solo informativo (no bloquea)
- compose.yml mapea dinámicamente
- Usuario no-root (appuser) ejecuta proceso

✅ **Puertos recomendados:**
- Desarrollo: 8000-8999 (no privilegiados)
- Producción: 8000-8999 o detrás de reverse proxy (nginx:80)
- Nunca: <1024 sin privilegios root

---

## 🚀 Comandos Útiles

```bash
# Ver puerto real en uso
docker ps | grep waste-classifier

# Ver todos los puertos del contenedor
docker port waste-classifier-api

# Ver si el puerto está escuchando
sudo netstat -tlnp | grep 8900

# Entrar al contenedor y ver puerto interno
docker exec waste-classifier-api ss -tlnp
# Output: LISTEN 0.0.0.0:8900 (app escucha internamente)

# Verificar variable PORT en contenedor
docker exec waste-classifier-api echo $PORT

# Verificar logs de uvicorn
docker logs waste-classifier-api | tail -20
```

---

## ✅ Conclusión

**Tu setup está correcto:**
- ✅ compose.yml mapea 8900:8900 correctamente
- ✅ uvicorn escucha en puerto 8900
- ✅ El "8000/tcp" en docker ps es solo documentación de Dockerfile
- ✅ Accede via: `curl http://localhost:8900/health`

**El "8000/tcp" que ves es normal y NO indica un problema.**

---

**Última actualización:** 2025-12-14  
**Versión:** 1.0
