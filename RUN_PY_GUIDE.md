# 🚀 run.py - Uso de PORT y HOST desde .env

## ¿Qué cambió?

`run.py` ahora usa automáticamente los valores de `PORT` y `HOST` del `.env` si no los proporcionas por CLI.

---

## Prioridad de Configuración

```
1. Argumentos CLI (más alta prioridad)
   --port 9000 --host 192.168.1.10
   
2. Variables en .env (media prioridad)
   PORT=8000
   HOST=0.0.0.0
   
3. Defaults de config.py (más baja prioridad)
   PORT = 8000
   HOST = "0.0.0.0"
```

**Ejemplo:**
```bash
# .env tiene PORT=8000
python run.py
# ✅ Usa puerto 8000 (de .env)

python run.py --port 9000
# ✅ Usa puerto 9000 (CLI sobrescribe .env)
```

---

## Cómo Usar

### Opción 1: Usar .env (RECOMENDADO)

```bash
# 1. Editar .env
nano .env
# Cambiar:
# PORT=8080
# HOST=0.0.0.0

# 2. Ejecutar sin argumentos
python run.py
# ✅ Automáticamente usa PORT=8080 de .env
```

**Output:**
```
Host: 0.0.0.0
Port: 8080
Accede a: http://0.0.0.0:8080
Docs: http://0.0.0.0:8080/docs
```

### Opción 2: Sobrescribir con CLI (para desarrollo)

```bash
# Usar .env pero cambiar puerto solo este comando
python run.py --port 9000

# Usar .env pero cambiar host solo este comando  
python run.py --host 127.0.0.1

# Cambiar ambos
python run.py --host 127.0.0.1 --port 9000
```

### Opción 3: Con reload (desarrollo con cambios automáticos)

```bash
python run.py --reload

# Detecta cambios en código y reinicia automáticamente
# Útil durante desarrollo
```

---

## Ejemplos Prácticos

### Desarrollo Local

```bash
# 1. .env tiene:
PORT=8000
HOST=0.0.0.0

# 2. Ejecutar
python run.py --reload

# 3. Output
# Host: 0.0.0.0
# Port: 8000
# Reload: True
# Accede a: http://0.0.0.0:8000/docs
```

### Solo Localhost (para desarrollo seguro)

```bash
python run.py --host 127.0.0.1

# Solo accesible desde tu máquina
# No desde otra máquina en la red
```

### Puerto Específico (testing)

```bash
python run.py --port 9999

# Usa HOST y PORT de .env pero sobrescribe puerto
# Host: 0.0.0.0
# Port: 9999
```

---

## Flujo de Carga de Configuración

```
app.config.settings
  ├─ Lee .env si existe
  ├─ Lee variables de entorno (export PORT=8000)
  └─ Usa defaults si no encuentra
  
run.py
  ├─ Lee settings
  ├─ Chequea argumentos CLI
  ├─ Usa CLI si se proporciona
  └─ Usa settings (del .env) si no
```

---

## Comparación: Antes vs Después

### ANTES (hardcodeado)

```python
parser.add_argument(
    "--port",
    type=int,
    default=8000,  # ❌ Hardcodeado
    help="Puerto donde escuchar (default: 8000)"
)
```

```bash
python run.py
# Siempre usa 8000, ignora .env
```

### AHORA (dinámico)

```python
parser.add_argument(
    "--port",
    type=int,
    default=None,  # ✅ None = usar .env
    help=f"Puerto donde escuchar (default: {settings.PORT} desde .env)"
)

# Luego:
port = args.port if args.port is not None else settings.PORT
```

```bash
python run.py
# Usa .env PORT=8000
```

---

## Verificación

```bash
# Ver qué valores toma del .env
python -c "from app.config import settings; print(f'PORT={settings.PORT}, HOST={settings.HOST}')"

# Output:
# PORT=8000, HOST=0.0.0.0

# Ejecutar
python run.py
# Usa esos valores
```

---

## CLI Arguments Completo

```bash
python run.py [opciones]

Opciones:
  --host HOST       Host donde escuchar (default: valor de .env)
  --port PORT       Puerto donde escuchar (default: valor de .env)
  --reload          Habilitar auto-reload en cambios de código
  --workers W       Número de workers (default: 1)
  -h, --help        Ver esta ayuda
```

**Ejemplos:**

```bash
python run.py
# Usa .env

python run.py --port 9000
# Usa .env HOST, pero puerto 9000

python run.py --host 127.0.0.1 --port 9000
# Usa 127.0.0.1:9000

python run.py --reload --workers 4
# 4 workers con reload
```

---

## 🔄 Docker vs run.py

### En Docker
```bash
docker compose up -d
# Lee .env
# Ejecuta: uvicorn app.main:app --host ${HOST} --port ${PORT}
```

### En Desarrollo Local
```bash
python run.py
# Lee .env
# Ejecuta: uvicorn con settings de .env
```

**Resultado:** Mismo comportamiento en ambos 🎯

---

## Casos de Uso

### 1. Desarrollo Normal
```bash
python run.py
# Lee .env automáticamente
```

### 2. Desarrollo con Reload
```bash
python run.py --reload
# Auto-recompila en cambios
```

### 3. Testing en Puerto Diferente
```bash
python run.py --port 8888
# No interfiere con otro proceso en 8000
```

### 4. Acceso desde Red
```bash
# .env tiene HOST=0.0.0.0
python run.py
# Accesible desde otras máquinas en 192.168.x.x:8000
```

### 5. Solo Localhost
```bash
python run.py --host 127.0.0.1
# Solo desde tu máquina
```

---

**Última actualización:** 2025-12-14  
**Versión:** 1.0
