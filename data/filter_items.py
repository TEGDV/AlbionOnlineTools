import json
import re

# Constantes de materiales base
MATERIALES = ["PLANKS", "METALBAR", "LEATHER", "CLOTH", "STONEBLOCK"]

# Crear patrón regex para coincidir con T4-T8, los materiales y niveles opcionales
# Ej: T4_PLANKS, T5_METALBAR_LEVEL1@1
patron = re.compile(r"^T[4-8]_(" + "|".join(MATERIALES) + r")(_LEVEL[1-4]@[1-4])?$")


def filtrar_json(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filtrar preservando la estructura completa del objeto original
    datos_filtrados = [
        item for item in data if patron.match(item.get("UniqueName", ""))
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(datos_filtrados, f, ensure_ascii=False, indent=2)

    print(
        f"Filtrado completado. Se extrajeron {len(datos_filtrados)} materiales de interés."
    )


if __name__ == "__main__":
    filtrar_json("items.json", "materiales_refinados.json")
