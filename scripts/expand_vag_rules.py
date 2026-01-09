import json

def expand_vag_rules():
    file_path = "src/vin/rules/dacos_vin_rules_v0.0.4.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    vag_profile = data.get("oem_profiles", {}).get("VAG")
    if not vag_profile:
        print("Error: VAG profile not found in oem_profiles")
        return

    existing_rules = vag_profile.get("vds_rules", [])
    existing_ids = {r.get("id") for r in existing_rules}

    new_rules = [
        # VW Models
        {"id": "vw_model_golf5_1k", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "1K"}, "meaning": {"model": "Golf Mk5/Jetta Mk5", "platform": "PQ35"}, "confidence": 0.9},
        {"id": "vw_model_golf6_5k", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "5K"}, "meaning": {"model": "Golf Mk6", "platform": "PQ35"}, "confidence": 0.9},
        {"id": "vw_model_golf7_5g", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "5G"}, "meaning": {"model": "Golf Mk7", "platform": "MQB"}, "confidence": 0.9},
        {"id": "vw_model_golf8_cd", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "CD"}, "meaning": {"model": "Golf Mk8", "platform": "MQB Evo"}, "confidence": 0.9},
        {"id": "vw_model_passat_b6_3c", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "3C"}, "meaning": {"model": "Passat B6/B7", "platform": "PQ46"}, "confidence": 0.9},
        {"id": "vw_model_passat_b8_3g", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "3G"}, "meaning": {"model": "Passat B8", "platform": "MQB"}, "confidence": 0.9},
        {"id": "vw_model_tiguan_mk1_5n", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "5N"}, "meaning": {"model": "Tiguan Mk1", "platform": "PQ35"}, "confidence": 0.9},
        {"id": "vw_model_tiguan_mk2_ad", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "AD"}, "meaning": {"model": "Tiguan Mk2", "platform": "MQB"}, "confidence": 0.9},
        {"id": "vw_model_touran_1t", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "1T"}, "meaning": {"model": "Touran", "platform": "PQ35/MQB"}, "confidence": 0.9},
        {"id": "vw_model_touareg_mk1_7l", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "7L"}, "meaning": {"model": "Touareg Mk1", "platform": "PL71"}, "confidence": 0.9},
        {"id": "vw_model_touareg_mk2_7p", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "7P"}, "meaning": {"model": "Touareg Mk2", "platform": "PL72"}, "confidence": 0.9},
        {"id": "vw_model_touareg_mk3_cr", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "CR"}, "meaning": {"model": "Touareg Mk3", "platform": "MLB Evo"}, "confidence": 0.9},
        {"id": "vw_model_polo_mk6_aw", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "AW"}, "meaning": {"model": "Polo Mk6", "platform": "MQB A0"}, "confidence": 0.9},
        {"id": "vw_model_troc_a1", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "A1"}, "meaning": {"model": "T-Roc", "platform": "MQB A1"}, "confidence": 0.9},
        
        # Audi Models
        {"id": "audi_model_a3_8p", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8P"}, "meaning": {"manufacturer": "Audi", "model": "A3 (8P)", "platform": "PQ35"}, "confidence": 0.9},
        {"id": "audi_model_a3_8v", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8V"}, "meaning": {"manufacturer": "Audi", "model": "A3 (8V)", "platform": "MQB"}, "confidence": 0.9},
        {"id": "audi_model_a3_8y", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8Y"}, "meaning": {"manufacturer": "Audi", "model": "A3 (8Y)", "platform": "MQB Evo"}, "confidence": 0.9},
        {"id": "audi_model_a4_8k", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8K"}, "meaning": {"manufacturer": "Audi", "model": "A4 (B8)", "platform": "MLB"}, "confidence": 0.9},
        {"id": "audi_model_a4_8w", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8W"}, "meaning": {"manufacturer": "Audi", "model": "A4 (B9)", "platform": "MLB Evo"}, "confidence": 0.9},
        {"id": "audi_model_a5_8t", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8T"}, "meaning": {"manufacturer": "Audi", "model": "A5 (8T)", "platform": "MLB"}, "confidence": 0.9},
        {"id": "audi_model_a6_4g", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4G"}, "meaning": {"manufacturer": "Audi", "model": "A6 (C7)", "platform": "MLB"}, "confidence": 0.9},
        {"id": "audi_model_a6_4a", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4A"}, "meaning": {"manufacturer": "Audi", "model": "A6 (C8)", "platform": "MLB Evo"}, "confidence": 0.9},
        {"id": "audi_model_q5_8r", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "8R"}, "meaning": {"manufacturer": "Audi", "model": "Q5 (8R)", "platform": "MLB"}, "confidence": 0.9},
        {"id": "audi_model_q5_fy", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "FY"}, "meaning": {"manufacturer": "Audi", "model": "Q5 (FY)", "platform": "MLB Evo"}, "confidence": 0.9},
        {"id": "audi_model_q7_4l", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4L"}, "meaning": {"manufacturer": "Audi", "model": "Q7 (4L)", "platform": "PL71"}, "confidence": 0.9},
        {"id": "audi_model_q7_4m", "markets": ["EU", "ZA"], "position": [7, 8], "pattern": {"type": "exact", "value": "4M"}, "meaning": {"manufacturer": "Audi", "model": "Q7 (4M)", "platform": "MLB Evo"}, "confidence": 0.9},
    ]

    added_count = 0
    for rule in new_rules:
        if rule["id"] not in existing_ids:
            existing_rules.append(rule)
            added_count += 1
        else:
            print(f"Skipping duplicate rule ID: {rule['id']}")

    vag_profile["vds_rules"] = existing_rules
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    print(f"Successfully added {added_count} new VAG rules.")

if __name__ == "__main__":
    expand_vag_rules()
