import json
import urllib.request
from datetime import datetime, timedelta


def obtener_precios_semanales(archivo_json, solo_mas_barato=False):
    with open(archivo_json, "r", encoding="utf-8") as f:
        materiales = json.load(f)

    item_ids = [item["UniqueName"] for item in materiales]
    ids_query = ",".join(item_ids)

    now = datetime.now()
    start_date = (now - timedelta(days=7)).strftime("%m-%d-%Y")
    end_date = now.strftime("%m-%d-%Y")

    url = f"https://www.albion-online-data.com/api/v2/stats/history/{ids_query}.json?date={start_date}&end_date={end_date}&time-scale=24"
    ciudades_excluidas = {"Brecilien", "Caerleon"}

    req = urllib.request.Request(url, headers={"User-Agent": "AODP-Avg-Client/1.3"})

    # Diccionario intermedio para agrupar { item_id: { ciudad: precio } }
    resultados_crudos = {}

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

            for record in data:
                location = record.get("location", "Desconocida")
                if location in ciudades_excluidas:
                    continue

                item_id = record.get("item_id", "Desconocido")
                puntos = record.get("data", [])

                precios_validos = [
                    p["avg_price"] for p in puntos if p.get("avg_price", 0) > 0
                ]

                if precios_validos:
                    # 1. Convertir el promedio a valor entero
                    promedio = int(sum(precios_validos) / len(precios_validos))

                    if item_id not in resultados_crudos:
                        resultados_crudos[item_id] = {}
                    resultados_crudos[item_id][location] = promedio

        salida_final = []

        # 3. Lógica del parámetro solo_mas_barato
        if solo_mas_barato:
            for item_id, locs in resultados_crudos.items():
                mejor_ciudad = min(locs, key=locs.get)
                mejor_precio = locs[mejor_ciudad]
                salida_final.append(
                    {
                        "item_id": item_id,
                        "location": mejor_ciudad,
                        "price": mejor_precio,
                    }
                )
        else:
            for item_id, locs in resultados_crudos.items():
                for loc, precio in locs.items():
                    salida_final.append(
                        {"item_id": item_id, "location": loc, "price": precio}
                    )

        # 2. Imprimir estrictamente en formato JSON
        print(json.dumps(salida_final, indent=2, ensure_ascii=False))

    except Exception as e:
        # En caso de error, emitir un JSON válido
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    # Ejecución de prueba con el parámetro activado
    obtener_precios_semanales(
        "data/materiales_simplificados.json", solo_mas_barato=True
    )
