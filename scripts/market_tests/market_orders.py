import json
import urllib.request


def obtener_ordenes_mercado(archivo_json, mejor_opcion=False):
    with open(archivo_json, "r", encoding="utf-8") as f:
        materiales = json.load(f)

    item_ids = [item["UniqueName"] for item in materiales]
    ids_query = ",".join(item_ids)

    # Endpoint modificado para precios actuales
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{ids_query}.json"
    ciudades_excluidas = {"Brecilien", "Caerleon"}

    req = urllib.request.Request(url, headers={"User-Agent": "AODP-Market-Client/1.0"})
    resultados_crudos = {}

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

            for record in data:
                # La clave cambia a 'city' en el endpoint de precios
                city = record.get("city", "Desconocida")
                if city in ciudades_excluidas:
                    continue

                item_id = record.get("item_id", "Desconocido")
                sell_price = record.get("sell_price_min", 0)
                buy_price = record.get("buy_price_max", 0)

                # Descartar registros vacíos o sin actualizar
                if sell_price > 0 or buy_price > 0:
                    if item_id not in resultados_crudos:
                        resultados_crudos[item_id] = []

                    resultados_crudos[item_id].append(
                        {
                            "city": city,
                            "sell_price_min": sell_price,
                            "buy_price_max": buy_price,
                        }
                    )

        salida_final = []

        if mejor_opcion:
            for item_id, locs in resultados_crudos.items():
                ventas_validas = [loc for loc in locs if loc["sell_price_min"] > 0]
                compras_validas = [loc for loc in locs if loc["buy_price_max"] > 0]

                mejor_compra = (
                    min(ventas_validas, key=lambda x: x["sell_price_min"])
                    if ventas_validas
                    else None
                )
                mejor_venta = (
                    max(compras_validas, key=lambda x: x["buy_price_max"])
                    if compras_validas
                    else None
                )

                salida_final.append(
                    {
                        "item_id": item_id,
                        "best_city_to_buy": mejor_compra,
                        "best_city_to_sell": mejor_venta,
                    }
                )
        else:
            for item_id, locs in resultados_crudos.items():
                for loc in locs:
                    salida_final.append(
                        {
                            "item_id": item_id,
                            "city": loc["city"],
                            "sell_price": loc["sell_price_min"],
                            "buy_price": loc["buy_price_max"],
                        }
                    )

        print(json.dumps(salida_final, indent=2, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    obtener_ordenes_mercado("data/materiales_simplificados.json", mejor_opcion=True)
