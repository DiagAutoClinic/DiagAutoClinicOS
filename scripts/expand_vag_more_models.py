import json
from pathlib import Path

def expand_vag_more_models():
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
    
    new_rules = [
        # Audi A1
        {"id": "audi_model_a1_8x", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8X"}, "meaning": {"manufacturer": "Audi", "model": "A1 (8X)", "platform": "PQ25"}, "confidence": 0.9},
        {"id": "audi_model_a1_gb", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "GB"}, "meaning": {"manufacturer": "Audi", "model": "A1 (GB)", "platform": "MQB A0"}, "confidence": 0.9},
        
        # Audi Q2
        {"id": "audi_model_q2_ga", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "GA"}, "meaning": {"manufacturer": "Audi", "model": "Q2", "platform": "MQB", "body_type": "SUV"}, "confidence": 0.9},
        
        # Audi Q3
        {"id": "audi_model_q3_8u", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8U"}, "meaning": {"manufacturer": "Audi", "model": "Q3 (8U)", "platform": "PQ35", "body_type": "SUV"}, "confidence": 0.9},
        {"id": "audi_model_q3_f3", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "F3"}, "meaning": {"manufacturer": "Audi", "model": "Q3 (F3)", "platform": "MQB", "body_type": "SUV"}, "confidence": 0.9},
        
        # Audi A7
        {"id": "audi_model_a7_4g", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4G"}, "meaning": {"manufacturer": "Audi", "model": "A7 (4G)", "platform": "MLB"}, "confidence": 0.9}, # Note: Same code as A6 4G? Often shared. Need to verify if distinct. 
        # Actually A7 4G VIN usually has 4G too. A6 and A7 share platform/codes often. 
        # If A6 is 4G and A7 is 4G, we can say "A6/A7". 
        # But let's check: A7 (Type 4G) 2010-2018. A6 (C7) is also 4G. 
        # So "model": "A6/A7 (C7/4G)" is more accurate.
        # I will update the existing 4G rule if found, or add this one.
        
        {"id": "audi_model_a7_4k", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4K"}, "meaning": {"manufacturer": "Audi", "model": "A6/A7 (C8/4K)", "platform": "MLB Evo"}, "confidence": 0.9},
        
        # Audi A8
        {"id": "audi_model_a8_4h", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4H"}, "meaning": {"manufacturer": "Audi", "model": "A8 (D4)", "platform": "MLB"}, "confidence": 0.9},
        {"id": "audi_model_a8_4n", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4N"}, "meaning": {"manufacturer": "Audi", "model": "A8 (D5)", "platform": "MLB Evo"}, "confidence": 0.9},
        
        # Audi TT
        {"id": "audi_model_tt_8j", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8J"}, "meaning": {"manufacturer": "Audi", "model": "TT (8J)", "platform": "PQ35", "body_type": "Coupe/Roadster"}, "confidence": 0.9},
        {"id": "audi_model_tt_fv", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "FV"}, "meaning": {"manufacturer": "Audi", "model": "TT (FV/8S)", "platform": "MQB", "body_type": "Coupe/Roadster"}, "confidence": 0.9},
        
        # Audi R8
        {"id": "audi_model_r8_42", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "42"}, "meaning": {"manufacturer": "Audi", "model": "R8 (Type 42)", "body_type": "Coupe/Spyder", "engine_hints": "V8/V10"}, "confidence": 0.9},
        {"id": "audi_model_r8_4s", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4S"}, "meaning": {"manufacturer": "Audi", "model": "R8 (Type 4S)", "body_type": "Coupe/Spyder", "engine_hints": "V10"}, "confidence": 0.9},
        
        # VW Others
        {"id": "vw_model_up_aa", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "AA"}, "meaning": {"model": "Up!", "platform": "NSF"}, "confidence": 0.9},
        {"id": "vw_model_scirocco_13", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "13"}, "meaning": {"model": "Scirocco", "platform": "PQ35", "body_type": "Coupe"}, "confidence": 0.9},
        {"id": "vw_model_beetle_5c", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "5C"}, "meaning": {"model": "Beetle (A5)", "platform": "PQ35/MQB"}, "confidence": 0.9},
        {"id": "vw_model_touran_1t", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "1T"}, "meaning": {"model": "Touran Mk1/Mk2", "platform": "PQ35", "body_type": "MPV"}, "confidence": 0.9},
        {"id": "vw_model_touran_5t", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "5T"}, "meaning": {"model": "Touran Mk3", "platform": "MQB", "body_type": "MPV"}, "confidence": 0.9},
        {"id": "vw_model_sharan_7n", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "7N"}, "meaning": {"model": "Sharan Mk2", "platform": "PQ46", "body_type": "MPV"}, "confidence": 0.9},
        {"id": "vw_model_arteon_3h", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "3H"}, "meaning": {"model": "Arteon", "platform": "MQB", "body_type": "Fastback/Shooting Brake"}, "confidence": 0.9},
        
        # Skoda
        {"id": "skoda_model_octavia_1z", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "1Z"}, "meaning": {"manufacturer": "Skoda", "model": "Octavia Mk2", "platform": "PQ35"}, "confidence": 0.9},
        {"id": "skoda_model_octavia_5e", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "5E"}, "meaning": {"manufacturer": "Skoda", "model": "Octavia Mk3", "platform": "MQB"}, "confidence": 0.9},
        {"id": "skoda_model_octavia_nx", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "NX"}, "meaning": {"manufacturer": "Skoda", "model": "Octavia Mk4", "platform": "MQB Evo"}, "confidence": 0.9},
        {"id": "skoda_model_superb_3t", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "3T"}, "meaning": {"manufacturer": "Skoda", "model": "Superb Mk2", "platform": "PQ46"}, "confidence": 0.9},
        {"id": "skoda_model_superb_3v", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "3V"}, "meaning": {"manufacturer": "Skoda", "model": "Superb Mk3", "platform": "MQB"}, "confidence": 0.9},
        {"id": "skoda_model_kodiaq_ns", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "NS"}, "meaning": {"manufacturer": "Skoda", "model": "Kodiaq", "platform": "MQB", "body_type": "SUV"}, "confidence": 0.9},
        {"id": "skoda_model_karoq_nu", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "NU"}, "meaning": {"manufacturer": "Skoda", "model": "Karoq", "platform": "MQB", "body_type": "SUV"}, "confidence": 0.9},
        
        # SEAT
        {"id": "seat_model_leon_5f", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "5F"}, "meaning": {"manufacturer": "SEAT", "model": "Leon Mk3", "platform": "MQB"}, "confidence": 0.9},
        {"id": "seat_model_ibiza_kj", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "KJ"}, "meaning": {"manufacturer": "SEAT", "model": "Ibiza Mk5", "platform": "MQB A0"}, "confidence": 0.9},
        {"id": "seat_model_ateca_57", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "57"}, "meaning": {"manufacturer": "SEAT", "model": "Ateca", "platform": "MQB", "body_type": "SUV"}, "confidence": 0.9},
    ]

    # Update 4G rule if exists
    updated_4g = False
    for rule in rules:
        if rule["id"] == "audi_model_a6_4g":
            rule["meaning"]["model"] = "A6/A7 (C7/4G)"
            updated_4g = True
            print("Updated audi_model_a6_4g")

    # Add new rules
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
    expand_vag_more_models()
