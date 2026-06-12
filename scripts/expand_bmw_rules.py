import json
import os
import sys

def main():
    rules_path = r"c:\Users\DACOS\Documents\DACOS\DACOS\DiagAutoClinicOS-main\DiagAutoClinicOS\src\vin\rules\dacos_vin_rules_v0.0.4.json"
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bmw_rules = data["oem_profiles"]["BMW"]["vds_rules"]
    
    # Remove ineffective hint rules
    bmw_rules = [r for r in bmw_rules if r.get("id") not in ["bmw_series_3_g20_hint", "bmw_series_x5_g05_hint"]]
    
    new_rules = [
        # G20 3 Series Rules
        {
            "id": "bmw_g20_330i",
            "markets": ["US", "ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "5R"},
            "meaning": {
                "model": "3 Series (G20)",
                "series": "3 Series",
                "trim_level": "330i",
                "body_type": "Sedan"
            },
            "confidence": 0.9
        },
        {
            "id": "bmw_g20_m340i",
            "markets": ["US", "ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "5V"},
            "meaning": {
                "model": "3 Series (G20)",
                "series": "3 Series",
                "trim_level": "M340i",
                "body_type": "Sedan"
            },
            "confidence": 0.9
        },
        
        # G05 X5 Rules
        {
            "id": "bmw_g05_x5_cr",
            "markets": ["US", "ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "CR"},
            "meaning": {
                "model": "X5 (G05)",
                "series": "X5",
                "body_type": "SUV"
            },
            "confidence": 0.9
        },
        {
            "id": "bmw_g05_x5_ju",
            "markets": ["US", "ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "JU"},
            "meaning": {
                "model": "X5 (G05)",
                "series": "X5",
                "body_type": "SUV"
            },
            "confidence": 0.9
        },
         {
            "id": "bmw_g05_x5_cv",
            "markets": ["US", "ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "CV"},
            "meaning": {
                "model": "X5 (G05)",
                "series": "X5",
                "body_type": "SUV"
            },
            "confidence": 0.9
        },

        # F30 3 Series Rules (Expanded)
        {
            "id": "bmw_f30_320i_3a",
            "markets": ["ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "3A"},
            "meaning": {
                "model": "3 Series (F30)",
                "series": "3 Series",
                "body_type": "Sedan"
            },
            "confidence": 0.88
        },
        {
            "id": "bmw_f30_320i_8c",
            "markets": ["ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "8C"},
            "meaning": {
                "model": "3 Series (F30)",
                "series": "3 Series",
                "body_type": "Sedan"
            },
            "confidence": 0.88
        },
        
        # F20 1 Series Rules
        {
            "id": "bmw_f20_1series_1s",
            "markets": ["ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "1S"},
            "meaning": {
                "model": "1 Series (F20)",
                "series": "1 Series",
                "body_type": "Hatchback"
            },
            "confidence": 0.88
        },
        {
            "id": "bmw_f20_1series_1r",
            "markets": ["ZA", "EU"],
            "position": [4, 5],
            "pattern": {"type": "exact", "value": "1R"},
            "meaning": {
                "model": "1 Series (F20)",
                "series": "1 Series",
                "body_type": "Hatchback"
            },
            "confidence": 0.88
        }
    ]
    
    # Merge new rules (avoid duplicates by id)
    existing_ids = {r.get("id") or r.get("rule_id") for r in bmw_rules}
    for rule in new_rules:
        if rule["id"] not in existing_ids:
            bmw_rules.append(rule)
            print(f"Added rule: {rule['id']}")
        else:
            print(f"Skipping duplicate rule: {rule['id']}")
            
    data["oem_profiles"]["BMW"]["vds_rules"] = bmw_rules
    
    with open(rules_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("Successfully updated BMW rules.")

if __name__ == "__main__":
    main()
