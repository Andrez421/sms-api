import pandas as pd
import requests
import time
import sys
import os
from datetime import datetime
from tqdm import tqdm # Barra de progreso

# --- CONFIGURACIÓN ---
API_URL = "http://localhost:8001/api/v1/enviar"
TOKEN = "clave_secreta_escuela_123"
ARCHIVO_EXCEL = "destinatarios.xlsx"

# TIEMPO DE ESPERA ENTRE MENSAJES (Segundos)
# ADVERTENCIA: Android puede bloquearte si envías muy rápido.
# - 5 segundos = ~12 mensajes por minuto (Seguro)
# - 10 segundos = ~6 mensajes por minuto (Muy Seguro)
DELAY_SEGUNDOS = 8 

def cargar_env_desde_archivo(ruta: str = ".env"):
	"""
	Carga variables de entorno desde .env sin dependencias externas.
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

def obtener_configuracion():
	"""
	Obtiene configuración de ejecución para el lanzador.
	"""
	cargar_env_desde_archivo()
	api_url = os.getenv("api_url_lanzador", API_URL)
	token = os.getenv("token_api_lanzador", TOKEN)
	return api_url, token

def cargar_datos():
    try:
        # Leemos el Excel asegurando que el Celular se lea como texto (string) no como número
        df = pd.read_excel(ARCHIVO_EXCEL, dtype={'Celular': str})
        columnas_requeridas = {"Nombre", "Celular", "Variable"}
        columnas_faltantes = columnas_requeridas.difference(df.columns)
        if columnas_faltantes:
            print(f"❌ Error: Faltan columnas en el Excel: {', '.join(sorted(columnas_faltantes))}")
            sys.exit()
        return df
    except FileNotFoundError:
        print(f"❌ Error: No se encuentra el archivo '{ARCHIVO_EXCEL}'")
        sys.exit()

def construir_mensaje(row):
    # Aquí diseñas tu plantilla de mensaje
    # Ejemplo: "Hola Juan, recuerda [variable]. Att: La Escuela"
    nombre = row['Nombre']
    variable = row['Variable'] # Puede ser saldo, nota, etc.
    
    mensaje = f"Hola {nombre}, cordial saludo. Le recordamos: {variable}. Att: Secretaria Academica."
    return mensaje

def main():
    api_url, token = obtener_configuracion()

    print("--- INICIANDO LANZADOR DE SMS ESCOLAR ---")
    print(f"🔗 API destino: {api_url}")
    df = cargar_datos()
    total_sms = len(df)
    
    tiempo_estimado = (total_sms * DELAY_SEGUNDOS) / 60
    print(f"📋 Total mensajes a enviar: {total_sms}")
    print(f"⏳ Tiempo estimado: {tiempo_estimado:.2f} minutos")
    print(f"🚀 Iniciando envíos con pausa de {DELAY_SEGUNDOS} seg entre mensajes...")
    
    confirmacion = input("¿Desea continuar? (s/n): ")
    if confirmacion.lower() != 's':
        sys.exit()

    resultados = []

    # Iniciamos el bucle con barra de progreso
    for index, row in tqdm(df.iterrows(), total=total_sms, desc="Enviando", unit="sms"):
        
        celular = str(row['Celular']).strip()
        if celular == "" or celular.lower() == "nan":
            resultados.append({
                "Celular": celular,
                "Estado": "Saltado",
                "Hora": datetime.now().strftime("%H:%M:%S"),
                "Detalle": "Celular vacío"
            })
            continue

        texto_mensaje = construir_mensaje(row)
        
        estado = "Error"
        detalle = ""

        try:
            payload = {
                "token": token,
                "celular": celular,
                "mensaje": texto_mensaje
            }
            
            # Enviar a nuestra API local
            response = requests.post(api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                estado = "Enviado"
            else:
                estado = "Fallo API"
                try:
                    detalle = response.json().get('detail', 'Error desconocido')
                except ValueError:
                    detalle = response.text if response.text else "Error desconocido"
                
        except Exception as e:
            estado = "Error Conexión"
            detalle = str(e)

        # Guardamos log
        resultados.append({
            "Celular": celular,
            "Estado": estado,
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Detalle": detalle
        })

        # PAUSA DE SEGURIDAD (Vital para no bloquear la SIM)
        if index < total_sms - 1:
            time.sleep(DELAY_SEGUNDOS)

    # Generar Reporte Final
    df_resultado = pd.DataFrame(resultados)
    nombre_reporte = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df_resultado.to_csv(nombre_reporte, index=False)

    total_enviados = int((df_resultado["Estado"] == "Enviado").sum())
    total_fallos = int((df_resultado["Estado"] == "Fallo API").sum())
    total_errores = int((df_resultado["Estado"] == "Error Conexión").sum())
    total_saltados = int((df_resultado["Estado"] == "Saltado").sum())
    
    print(f"\n✅ Proceso finalizado.")
    print(f"📊 Enviados: {total_enviados} | Fallo API: {total_fallos} | Error Conexión: {total_errores} | Saltados: {total_saltados}")
    print(f"📄 Reporte guardado en: {nombre_reporte}")

if __name__ == "__main__":
    main()