import json
import re

MATERIALES = ["PLANKS", "METALBAR", "LEATHER", "CLOTH", "STONEBLOCK"]
patron = re.compile(r"^T[4-8]_(" + "|".join(MATERIALES) + r")(_LEVEL[1-4]@[1-4])?$")


def filtrar_simplificado(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filtrar mediante regex y mapear exclusivamente Index y UniqueName
    datos_filtrados = [
        {"Index": item.get("Index"), "UniqueName": item.get("UniqueName")}
        for item in data
        if patron.match(item.get("UniqueName", ""))
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(datos_filtrados, f, ensure_ascii=False, indent=2)

    print(f"Filtrado completado. Se extrajeron {len(datos_filtrados)} elementos.")


if __name__ == "__main__":
    filtrar_simplificado("items.json", "materiales_simplificados.json")
