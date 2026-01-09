import json
import os

def fix_vag_split():
    file_path = "src/vin/rules/dacos_vin_rules_v0.0.4.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if VAG is in wmi_plant_mappings
    if "VAG" not in data.get("wmi_plant_mappings", {}):
        print("Error: VAG not found in wmi_plant_mappings")
        return

    vag_wmi_data = data["wmi_plant_mappings"]["VAG"]
    
    # Fields to move to oem_profiles
    fields_to_move = ["markets", "vds_strategies", "vds_rules"]
    vag_oem_data = {}
    
    for field in fields_to_move:
        if field in vag_wmi_data:
            vag_oem_data[field] = vag_wmi_data[field]
            del vag_wmi_data[field]
            print(f"Moved {field} from wmi_plant_mappings to oem_profiles extraction")
    
    # Ensure oem_profiles exists
    if "oem_profiles" not in data:
        data["oem_profiles"] = {}
        
    # Add to oem_profiles
    # If VAG already exists in oem_profiles (unlikely if I deleted it), merge or overwrite?
    # Based on previous turn, I deleted the second block which was likely the oem_profiles one.
    if "VAG" in data["oem_profiles"]:
        print("Warning: VAG already exists in oem_profiles. Merging...")
        data["oem_profiles"]["VAG"].update(vag_oem_data)
    else:
        data["oem_profiles"]["VAG"] = vag_oem_data
        print("Created VAG in oem_profiles")

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    print("Successfully split VAG rules.")

if __name__ == "__main__":
    fix_vag_split()
