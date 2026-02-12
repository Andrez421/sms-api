# API SMS Escolar Colombia

API simple para enviar SMS a través de un dispositivo Android con Traccar Client.

## 🚀 Estado del Servidor

✅ **Servidor corriendo en:** `http://0.0.0.0:8002`

## 📋 Configuración Completada

1. ✅ Entorno virtual creado (`venv/`)
2. ✅ Dependencias instaladas
3. ✅ Servidor FastAPI funcionando

## 🔧 Comandos Útiles

### Iniciar el servidor
```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8082 --reload
```

### Detener el servidor
Presiona `CTRL+C` en la terminal donde está corriendo

## 📡 Endpoints Disponibles

### 1. Health Check
**GET** `/`

Verifica que la API está en línea.

```bash
curl http://localhost:8082/
```

**Respuesta:**
```json
{
	"status": "API Online",
	"gateway": "http://10.125.26.186:8082"
}
```

### 2. Enviar SMS
**POST** `/api/v1/enviar`

Envía un SMS a través del dispositivo Android.

**Body (JSON):**
```json
{
	"token": "clave_secreta_escuela_123",
	"celular": "3001234567",
	"mensaje": "Hola, este es un mensaje de prueba"
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:8001/api/v1/enviar \
  -H "Content-Type: application/json" \
  -d '{
    "token": "clave_secreta_escuela_123",
    "celular": "3001234567",
    "mensaje": "Hola desde la API"
  }'
```

**Respuesta exitosa:**
```json
{
	"estado": "Procesando",
	"destino": "+573001234567"
}
```

## ⚙️ Configuración en main.py

### Variables importantes:
- `ANDROID_GATEWAY_URL`: URL del dispositivo Android con Traccar (actualmente: `http://10.125.26.186:8082`)
- `TOKEN_SEGURIDAD`: Token para proteger la API (actualmente: `clave_secreta_escuela_123`)

### Endpoints disponibles del celular:
Según tu archivo `.env`, tienes dos endpoints disponibles:
- **Endpoint 1:** `http://10.3.61.55:8082`
- **Endpoint 2:** `http://10.125.26.186:8082` ✅ **(Actualmente configurado)**

### Modificar configuración:
Edita el archivo `main.py` línea 10:

```python
ANDROID_GATEWAY_URL = "http://10.125.26.186:8082"  # Cambia según el endpoint activo
TOKEN_SEGURIDAD = "clave_secreta_escuela_123"      # Cambia por tu token seguro
```

**Nota:** Si el endpoint actual no funciona, prueba con el otro endpoint disponible.

## 📱 Configuración del Dispositivo Android

1. Instala **Traccar Client** en el dispositivo Android
2. Configura la app para que escuche en el puerto 8080
3. Asegúrate de que el dispositivo esté en la misma red o sea accesible desde el servidor
4. La IP del dispositivo debe coincidir con `ANDROID_GATEWAY_URL`

## 🔒 Seguridad

- El token de seguridad es obligatorio en cada petición
- Los mensajes están limitados a 160 caracteres
- Los números se normalizan automáticamente al formato colombiano (+57)

## 📝 Formatos de Número Aceptados

- `3001234567` → Se convierte a `+573001234567`
- `+573001234567` → Se mantiene igual
- Otros formatos generarán error

## 🐛 Solución de Problemas

### El servidor no inicia (puerto ocupado)
```bash
# Detener proceso en puerto 8001
lsof -ti:8001 | xargs kill -9

# O usar otro puerto
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### Error de módulos no encontrados
```bash
# Asegúrate de activar el entorno virtual
source venv/bin/activate

# Reinstalar dependencias si es necesario
pip install -r requirements.txt
```

### El SMS no se envía
- Verifica que el dispositivo Android esté encendido y conectado
- Confirma que la IP en `ANDROID_GATEWAY_URL` sea correcta
- Revisa los logs del servidor para ver errores de conexión
- Verifica que Traccar Client esté configurado correctamente

## 📚 Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

## 🎯 Próximos Pasos

1. Cambiar el `TOKEN_SEGURIDAD` por uno más seguro
2. Configurar el dispositivo Android con Traccar Client
3. Probar el envío de SMS desde la documentación interactiva
4. Integrar con tu sistema escolar

## 📞 Ejemplo de Integración

```python
import requests

def enviar_notificacion(celular, mensaje):
    url = "http://localhost:8001/api/v1/enviar"
    payload = {
        "token": "clave_secreta_escuela_123",
        "celular": celular,
        "mensaje": mensaje
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Uso
resultado = enviar_notificacion("3001234567", "Recordatorio de clase")
print(resultado)
```

## 🚀 Lanzador Masivo de SMS (`lanzador.py`)

El proyecto incluye un script para enviar SMS masivos desde un archivo Excel.

### Requisitos adicionales:
```bash
source venv/bin/activate
pip install pandas openpyxl tqdm
```

### Formato del archivo Excel (`destinatarios.xlsx`):
| Nombre | Celular | Variable |
|--------|---------|----------|
| Juan | 3001234567 | Pago pendiente $50.000 |
| María | 3109876543 | Reunión mañana 10am |

### Uso:
```bash
source venv/bin/activate
python lanzador.py
```

### Características:
- ✅ Lee datos desde Excel
- ✅ Barra de progreso visual
- ✅ Pausa de 8 segundos entre mensajes (evita bloqueos)
- ✅ Genera reporte CSV con resultados
- ✅ Plantilla de mensaje personalizable

### Configuración del lanzador:
Edita `lanzador.py` líneas 9-17 para ajustar:
- `API_URL`: Debe apuntar a `http://localhost:8001/api/v1/enviar` ✅
- `TOKEN`: Tu token de seguridad
- `ARCHIVO_EXCEL`: Nombre del archivo Excel
- `DELAY_SEGUNDOS`: Tiempo entre mensajes (recomendado: 8-10 segundos)
