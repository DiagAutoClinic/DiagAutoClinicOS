import json
from pathlib import Path

def enhance_vag_rules():
    file_path = Path("src/vin/rules/dacos_vin_rules_v0.0.4.json")
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    vag_profile = data.get("oem_profiles", {}).get("VAG")
    if not vag_profile:
        print("VAG profile not found")
        return

    rules = vag_profile.get("vds_rules", [])
    
    # 1. Update existing rules with body types
    suv_models = ["Tiguan", "Touareg", "T-Cross", "T-Roc", "Q2", "Q3", "Q5", "Q7", "Q8", "Kodiaq", "Karoq", "Kamiq", "Ateca", "Arona", "Tarraco"]
    pickup_models = ["Amarok"]
    
    count_updated = 0
    for rule in rules:
        meaning = rule.get("meaning", {})
        model = meaning.get("model", "")
        
        # Check for SUVs
        is_suv = any(m in model for m in suv_models)
        if is_suv and "body_type" not in meaning:
            meaning["body_type"] = "SUV"
            count_updated += 1
            
        # Check for Pickups
        is_pickup = any(m in model for m in pickup_models)
        if is_pickup and "body_type" not in meaning:
            meaning["body_type"] = "Pickup"
            count_updated += 1

    print(f"Updated {count_updated} rules with body type info.")

    # 2. Add new rules for Commercial Vehicles
    new_rules = [
        {
            "id": "vw_model_caddy_2k",
            "markets": ["EU", "ZA"],
            "position": [7, 8],
            "pattern": {"type": "exact", "value": "2K"},
            "meaning": {"model": "Caddy (Mk3/Mk4)", "platform": "PQ35", "body_type": "MPV/Van"},
            "confidence": 0.9
        },
        {
            "id": "vw_model_caddy_sb",
            "markets": ["EU", "ZA"],
            "position": [7, 8],
            "pattern": {"type": "exact", "value": "SB"},
            "meaning": {"model": "Caddy (Mk5)", "platform": "MQB", "body_type": "MPV/Van"},
            "confidence": 0.9
        },
        {
            "id": "vw_model_transporter_t5_7h",
            "markets": ["EU", "ZA"],
            "position": [7, 8],
            "pattern": {"type": "exact", "value": "7H"},
            "meaning": {"model": "Transporter T5", "body_type": "Van/Bus"},
            "confidence": 0.9
        },
        {
            "id": "vw_model_transporter_t5_7j",
            "markets": ["EU", "ZA"],
            "position": [7, 8],
            "pattern": {"type": "exact", "value": "7J"},
            "meaning": {"model": "Transporter T5 (Platform)", "body_type": "Chassis Cab"},
            "confidence": 0.9
        },
        {
            "id": "vw_model_transporter_t6_7e",
            "markets": ["EU", "ZA"],
            "position": [7, 8],
            "pattern": {"type": "exact", "value": "7E"},
            "meaning": {"model": "Transporter T6", "body_type": "Van/Bus"},
            "confidence": 0.9
        },
        {
            "id": "vw_model_crafter_2e",
            "markets": ["EU", "ZA"],
            "position": [7, 8],
            "pattern": {"type": "exact", "value": "2E"},
            "meaning": {"model": "Crafter (Mk1)", "body_type": "Van"},
            "confidence": 0.9
        },
        {
            "id": "vw_model_crafter_sy",
            "markets": ["EU", "ZA"],
            "position": [7, 8],
            "pattern": {"type": "exact", "value": "SY"},
            "meaning": {"model": "Crafter (Mk2)", "body_type": "Van"},
            "confidence": 0.9
        }
    ]

    # Check for duplicates before adding
    existing_ids = {r.get("id") for r in rules}
    count_added = 0
    for rule in new_rules:
        if rule["id"] not in existing_ids:
            rules.append(rule)
            count_added += 1
        else:
            print(f"Skipping duplicate rule id: {rule['id']}")

    print(f"Added {count_added} new rules.")
    
    # Save back
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print("Saved dacos_vin_rules_v0.0.4.json")

if __name__ == "__main__":
    enhance_vag_rules()
