import os
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI(title="API SMS Escolar Colombia")

# --- CONFIGURACIÓN ---
TOKEN_SEGURIDAD = "clave_secreta_escuela_123" # Para proteger tu API

def cargar_env_desde_archivo(ruta: str = ".env") -> None:
	"""
	Carga variables de entorno desde el archivo .env sin dependencias externas.
	"""
	if not os.path.exists(ruta):
		return

	with open(ruta, "r", encoding="utf-8") as archivo_env:
		for linea in archivo_env:
			linea_limpia = linea.strip()
			if not linea_limpia or linea_limpia.startswith("#") or "=" not in linea_limpia:
				continue
			clave, valor = linea_limpia.split("=", 1)
			os.environ.setdefault(clave.strip(), valor.strip())

def obtener_configuracion_gateway() -> tuple[str, str, str]:
	"""
	Obtiene endpoint y token según servicio activo (local o cloud).
	"""
	cargar_env_desde_archivo()

	token_local = os.getenv("token_local_service", "")
	token_cloud = os.getenv("token_cloud_service", "")
	endpoint_local = os.getenv("endpoint", "")
	endpoint_cloud = os.getenv("endpoint_port", "")
	servicio_activo = os.getenv("active_service", "local").strip().lower()

	if servicio_activo == "cloud":
		return endpoint_cloud, token_cloud, "cloud"
	return endpoint_local, token_local, "local"

ANDROID_GATEWAY_URL, ANDROID_TOKEN, ACTIVE_SERVICE = obtener_configuracion_gateway()

class SMSRequest(BaseModel):
    token: str
    celular: str # Ejemplo: 3001234567
    mensaje: str

def limpiar_numero(celular: str):
    """
    Normaliza el número para Colombia.
    Elimina espacios, guiones y asegura el formato local o +57.
    La app Traccar suele funcionar mejor con el formato internacional +57.
    """
    celular = celular.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    if len(celular) == 10 and celular.startswith("3"):
        return "+57" + celular # Convierte 3001234567 a +573001234567
    
    if len(celular) == 13 and celular.startswith("+57"):
        return celular
        
    raise ValueError("Número de celular inválido para Colombia")

def enviar_sms_background(celular: str, mensaje: str):
    """
    Función que se ejecuta en segundo plano para no bloquear la API.
    """
    # Traccar Client espera POST con JSON y token de autorización
    payload = {
        'to': celular,
        'message': mensaje
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': ANDROID_TOKEN
    }
    
    try:
        # Enviamos la petición al celular Android con autenticación
        response = requests.post(ANDROID_GATEWAY_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200 or response.status_code == 202:
            print(f"✅ Enviado a {celular} usando servicio {ACTIVE_SERVICE}")
            print(f"   Respuesta: {response.text[:100]}")
        else:
            print(f"❌ Error enviando a {celular} - Status: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error de conexión con el celular: {str(e)}")

@app.post("/api/v1/enviar")
async def enviar_sms(request: SMSRequest, background_tasks: BackgroundTasks):
    
    # 1. Seguridad básica
    if request.token != TOKEN_SEGURIDAD:
        raise HTTPException(status_code=401, detail="Token no autorizado")
    
    # 2. Validación de longitud de mensaje
    if len(request.mensaje) > 160:
        raise HTTPException(status_code=400, detail="El mensaje excede 160 caracteres")

    # 3. Limpieza de número
    try:
        numero_final = limpiar_numero(request.celular)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de celular incorrecto")

    # 4. Enviar a la cola (Background)
    # IMPORTANTE: Android tiene límites de envío. 
    # Si envías 1000 de golpe, Android bloqueará la app.
    # Aquí añadimos un pequeño delay artificial si estás haciendo un bucle masivo fuera de la API,
    # pero para peticiones individuales está bien así.
    background_tasks.add_task(enviar_sms_background, numero_final, request.mensaje)

    return {"estado": "Procesando", "destino": numero_final}

@app.get("/")
def health_check():
    return {
        "status": "API Online",
        "gateway": ANDROID_GATEWAY_URL,
        "service": ACTIVE_SERVICE
    }