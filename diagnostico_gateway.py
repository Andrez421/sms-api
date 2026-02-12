#!/usr/bin/env python3
"""
Script de diagnóstico completo para verificar el gateway SMS
"""
import requests
import json

GATEWAY_URL = "http://10.3.61.55:8082"
TOKEN = "0fc18a1f-fa88-40c4-9b87-69f08502aad9"

print("=" * 70)
print("🔍 DIAGNÓSTICO COMPLETO DEL GATEWAY SMS")
print("=" * 70)

# Test 1: Verificar conectividad básica
print("\n1️⃣ Verificando conectividad con el gateway...")
print("-" * 70)
try:
	response = requests.get(GATEWAY_URL, timeout=5)
	print(f"✅ Gateway accesible - Status: {response.status_code}")
	if "Send SMS using following API" in response.text:
		print("✅ Gateway respondiendo correctamente")
except Exception as e:
	print(f"❌ Error de conectividad: {e}")
	exit(1)

# Test 2: Verificar autenticación
print("\n2️⃣ Verificando autenticación...")
print("-" * 70)
headers_sin_auth = {"Content-Type": "application/json"}
payload_test = {"to": "+573001234567", "message": "test"}

try:
	response = requests.post(GATEWAY_URL, json=payload_test, headers=headers_sin_auth, timeout=5)
	if response.status_code == 401:
		print("✅ Gateway requiere autenticación (esperado)")
	else:
		print(f"⚠️  Gateway respondió {response.status_code} sin autenticación")
except Exception as e:
	print(f"❌ Error: {e}")

# Test 3: Verificar autenticación con token
print("\n3️⃣ Verificando autenticación con token...")
print("-" * 70)
headers_con_auth = {
	"Content-Type": "application/json",
	"Authorization": TOKEN
}

try:
	response = requests.post(GATEWAY_URL, json=payload_test, headers=headers_con_auth, timeout=5)
	print(f"Status Code: {response.status_code}")
	print(f"Headers: {dict(response.headers)}")
	print(f"Body: '{response.text}'")
	
	if response.status_code == 200:
		if response.text.strip() == "":
			print("⚠️  PROBLEMA DETECTADO: Gateway responde 200 OK pero sin contenido")
			print("    Esto indica que la petición fue aceptada pero puede no estar procesándose")
		else:
			print("✅ Gateway respondió correctamente")
	else:
		print(f"❌ Error: Status {response.status_code}")
except Exception as e:
	print(f"❌ Error: {e}")

# Test 4: Verificar formato de respuesta esperado
print("\n4️⃣ Análisis de la respuesta...")
print("-" * 70)
if response.status_code == 200 and response.text.strip() == "":
	print("📋 Posibles causas del problema:")
	print("   1. La app SMS Gateway en el celular NO está en primer plano")
	print("   2. El servicio LOCAL SERVICE está deshabilitado en la app")
	print("   3. Los permisos de SMS no están otorgados a la app")
	print("   4. La app está en modo de ahorro de batería (restringida)")
	print("   5. La SIM seleccionada no tiene saldo o está bloqueada")
	print("   6. El celular perdió conexión de red móvil")

# Test 5: Verificar endpoint de estado (si existe)
print("\n5️⃣ Intentando obtener estado del gateway...")
print("-" * 70)
endpoints_estado = ["/health", "/status", "/ping", "/info"]
for endpoint in endpoints_estado:
	try:
		url = f"{GATEWAY_URL}{endpoint}"
		response = requests.get(url, headers={"Authorization": TOKEN}, timeout=3)
		if response.status_code == 200:
			print(f"✅ Endpoint {endpoint} disponible:")
			print(f"   {response.text[:200]}")
	except:
		pass

print("\n" + "=" * 70)
print("📱 RECOMENDACIONES PARA EL CELULAR:")
print("=" * 70)
print("1. Abre la app 'SMS Gateway' en el celular")
print("2. Verifica que 'LOCAL SERVICE' esté habilitado (✓)")
print("3. Confirma que el token mostrado coincida con:")
print(f"   {TOKEN}")
print("4. Verifica que los endpoints mostrados incluyan:")
print(f"   {GATEWAY_URL}")
print("5. Revisa los logs de la app para ver si hay errores")
print("6. Confirma que la SIM con saldo esté seleccionada como predeterminada")
print("7. Verifica permisos de SMS en Configuración > Apps > SMS Gateway")
print("8. Desactiva optimización de batería para la app SMS Gateway")
print("=" * 70)
