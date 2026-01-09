import json

def update_rules():
    path = "src/vin/rules/dacos_vin_rules_v0.0.4.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Clean VAG in wmi_plant_mappings
    vag_wmi_obj = data["wmi_plant_mappings"].get("VAG")
    if vag_wmi_obj:
        # Keep only 'wmi' and 'plants'
        keys_to_keep = ["wmi", "plants"]
        keys_to_remove = [k for k in vag_wmi_obj.keys() if k not in keys_to_keep]
        for k in keys_to_remove:
            del vag_wmi_obj[k]
        print(f"Cleaned VAG wmi_plant_mappings, removed: {keys_to_remove}")

    # 2. Add AFV to Mercedes-Benz wmi
    mb_wmi_entry = data["wmi_plant_mappings"].get("Mercedes-Benz", {}).get("wmi")
    if mb_wmi_entry:
        if "AFV" not in mb_wmi_entry:
            mb_wmi_entry["AFV"] = {
                "manufacturer": "Mercedes-Benz South Africa",
                "country": "South Africa"
            }
            print("Added AFV to Mercedes-Benz wmi")
    
    # 3. Add SA C-Class rules to Mercedes-Benz oem_profiles
    mb_profile = data["oem_profiles"].get("Mercedes-Benz")
    if mb_profile:
        rules = mb_profile.get("vds_rules", [])
        
        # Check if rule already exists to avoid dupes
        existing_ids = {r.get("id") for r in rules}
        
        new_rules = [
            {
                "id": "mb_c_class_w205_sa",
                "markets": ["ZA"],
                "position": [4, 5, 6],
                "pattern": {
                    "type": "exact",
                    "value": "205"
                },
                "meaning": {
                    "series": "C-Class (W205)",
                    "body_type": "Sedan",
                    "assembly": "South Africa"
                },
                "confidence": 0.9,
                "notes": "East London build"
            },
             {
                "id": "mb_c_class_w206_sa",
                "markets": ["ZA"],
                "position": [4, 5, 6],
                "pattern": {
                    "type": "exact",
                    "value": "206"
                },
                "meaning": {
                    "series": "C-Class (W206)",
                    "body_type": "Sedan",
                    "assembly": "South Africa"
                },
                "confidence": 0.9,
                "notes": "East London build"
            }
        ]
        
        for rule in new_rules:
            if rule["id"] not in existing_ids:
                rules.append(rule)
                print(f"Added rule {rule['id']}")
        
        mb_profile["vds_rules"] = rules

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("Updated dacos_vin_rules_v0.0.4.json")

if __name__ == "__main__":
    update_rules()
