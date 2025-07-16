import json
import requests
from tqdm import tqdm
import os
import pandas as pd

# Configuración
# input_file = "anuncios_51_60.json"
input_file = "anuncios.json"
output_dir = "resultados"
os.makedirs(output_dir, exist_ok=True)
json_output = os.path.join(output_dir, "anuncios_resultados.json")
url = "http://localhost:8000/analizar_full"

# Cargar anuncios
with open(input_file, "r", encoding="utf-8") as f:
    anuncios = json.load(f)

resultados = []

# Analizar cada anuncio
for anuncio in tqdm(anuncios, desc="Analizando anuncios"):
    files = {}
    data = {}

    descripcion = anuncio.get("description", "").strip()
    if descripcion:
        data["texto"] = descripcion

    imagen_path = anuncio.get("imagen_local", "").strip()
    if imagen_path and os.path.exists(imagen_path):
        files["imagen"] = (os.path.basename(imagen_path), open(imagen_path, "rb"), "image/jpeg")

    try:
        if files:
            response = requests.post(url, data=data, files=files)
        else:
            response = requests.post(url, data=data)  # 👈 esto manda JSON

        if response.ok:
            resultado = response.json()
        else:
            resultado = {"error": f"HTTP {response.status_code}", "detalle": response.text}
    except Exception as e:
        resultado = {"error": str(e)}

    anuncio["analisis_modelos"] = resultado
    resultados.append(anuncio)

# Guardar JSON
with open(json_output, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"✅ Resultados guardados en {json_output}")


# Mostrar errores
print("\n🔍 Anuncios con errores:")
for anuncio in resultados:
    error = anuncio.get("analisis_modelos", {}).get("error")
    if error:
        print(f"ID: {anuncio['id']} | Error: {error}")
        print(f"Detalle: {anuncio['analisis_modelos'].get('detalle')}\n")
