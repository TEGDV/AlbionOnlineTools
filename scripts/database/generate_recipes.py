import json
import os

OUTPUT_FILE = "data/recipes.json"

def generate_recipes():
    print("Generating recipes based on standard patterns...")
    recipes = {}
    
    # Base Materials by Tier
    def get_mat(mat_type, tier, ench=0):
        mat_map = {
            "plank": "WOOD",
            "bar": "METAL",
            "leather": "LEATHER",
            "cloth": "CLOTH"
        }
        res = f"T{tier}_{mat_map[mat_type]}"
        if ench > 0:
            res += f"_LEVEL{ench}@{ench}"
        return res
        
    def add_recipe(name, count1, mat1, count2, mat2, artifact=None, animal_part=None):
        for t in range(4, 9): # T4 to T8
            item_id = f"T{t}_{name}"
            reqs = [
                {"UniqueName": get_mat(mat1, t), "Count": count1},
                {"UniqueName": get_mat(mat2, t), "Count": count2}
            ]
            
            if artifact:
                reqs.append({"UniqueName": f"T{t}_{artifact}", "Count": 1})
                
            if animal_part:
                # Shapeshifter animal parts: T5=1, T6=2, T7=3, T8=4 (example simplification)
                count = t - 4 
                if count > 0:
                    reqs.append({"UniqueName": f"T{t}_{animal_part}", "Count": count})
                    
            recipes[item_id] = {
                "tier": t,
                "resources": reqs
            }

    # STANDARD WEAPONS (Examples)
    # Fire Staffs (Wood + Metal)
    add_recipe("MAIN_FIRESTAFF", 16, "plank", 8, "bar")
    add_recipe("2H_FIRESTAFF_HELL", 20, "plank", 12, "bar", artifact="ARTIFACT_2H_FIRESTAFF_HELL")
    
    # Swords (Metal + Leather)
    add_recipe("MAIN_SWORD", 16, "bar", 8, "leather")
    add_recipe("2H_DUALSWORD", 20, "bar", 12, "leather")
    add_recipe("2H_SWORD_GALATINE", 20, "bar", 12, "leather", artifact="ARTIFACT_2H_SWORD_GALATINE")
    
    # Daggers (Metal + Leather)
    add_recipe("MAIN_DAGGER", 12, "bar", 8, "leather")
    add_recipe("2H_DAGGER_KATAR", 20, "bar", 12, "leather", artifact="ARTIFACT_2H_DAGGER_KATAR")
    add_recipe("2H_DUALDAGGER_FANGS", 20, "bar", 12, "leather", artifact="ARTIFACT_2H_DUALDAGGER_FANGS") # Bloodletter/Deathgivers approximation
    
    # SHAPESHIFTER WEAPONS (Planks + Leather + Animal Part + optional artifact)
    # Prowling Staff (Panther)
    add_recipe("2H_SHAPESHIFTER_PANTHER", 20, "plank", 12, "leather", animal_part="ANIMAL_PART_PANTHER")
    add_recipe("2H_SHAPESHIFTER_BEAR", 20, "plank", 12, "leather", animal_part="ANIMAL_PART_BEAR")
    add_recipe("2H_SHAPESHIFTER_WEREWOLF", 20, "plank", 12, "leather", artifact="ARTIFACT_2H_SHAPESHIFTER_WEREWOLF", animal_part="ANIMAL_PART_WEREWOLF")
    
    # ARMORS
    add_recipe("ARMOR_CLOTH_SET1", 16, "cloth", 0, "cloth")
    add_recipe("ARMOR_LEATHER_SET1", 16, "leather", 0, "leather")
    add_recipe("ARMOR_PLATE_SET1", 16, "bar", 0, "bar")
    
    return recipes

def main():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    recipes = generate_recipes()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2)
        
    print(f"Generated {len(recipes)} recipes from known patterns.")

if __name__ == "__main__":
    main()
