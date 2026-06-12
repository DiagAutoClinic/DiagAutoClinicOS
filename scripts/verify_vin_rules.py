import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vin.decoder import decode_vin
from src.vin.vin_validator_layer0 import calculate_check_digit
from src.vin.models import EpistemologicalValue

def make_valid_vin(wmi, vds, year, plant, serial):
    # Construct VIN with '0' as check digit placeholder
    # WMI(3) + VDS(5) + Check(1) + Year(1) + Plant(1) + Serial(6)
    # VIN length: 3 + 5 + 1 + 1 + 1 + 6 = 17
    pre_vin = f"{wmi}{vds}0{year}{plant}{serial}"
    try:
        check_digit = calculate_check_digit(pre_vin)
    except Exception as e:
        print(f"Error calculating check digit for {pre_vin}: {e}")
        return pre_vin # Fallback
        
    valid_vin = f"{wmi}{vds}{check_digit}{year}{plant}{serial}"
    return valid_vin

def get_val(epist_val):
    if isinstance(epist_val, EpistemologicalValue):
        return epist_val.value
    return epist_val

def test_vin(name, vin):
    print(f"\n--- Testing {name} ---")
    print(f"VIN: {vin}")
    # Use ZA for Hilux, Diesel, and Ranger SA. EU for Ford 2.0. US for others.
    market = "US"
    if "Hilux" in name or "FTV" in name or "Ranger" in name or "South Africa" in name or "SA" in name:
        market = "ZA"
    elif "Ford 2.0" in name:
        market = "EU"
        
    result = decode_vin(vin, market_hint=market)
    
    if not result.is_valid:
        print(f"INVALID VIN: {result.epistemology_notes}")
        return

    print(f"Manufacturer: {get_val(result.manufacturer)}")
    print(f"Model: {get_val(result.model)}")
    print(f"Series: {get_val(result.series)}")
    print(f"Body Type: {get_val(result.body_type)}")
    print(f"Engine Family: {get_val(result.engine_family)}")
    print(f"Displacement: {get_val(result.displacement_cc)}")
    print(f"Cylinders: {get_val(result.cylinders)}")
    print(f"Config: {get_val(result.engine_config)}")
    print(f"Fuel: {get_val(result.fuel_type)}")
    print(f"Notes: {result.epistemology_notes}")

def main():
    # 1. Toyota Hilux SA
    # WMI: AHT, VDS: EB6CB (starts_with), Year: G (2016), Plant: 0, Serial: 123456
    vin_hilux = make_valid_vin("AHT", "EB6CB", "G", "0", "123456")
    test_vin("Toyota Hilux SA", vin_hilux)
    
    # 2. Toyota 2AR-FE (Camry US)
    # WMI: 4T1, VDS: XD123 (Pos 5 is D), Year: G, Plant: U, Serial: 123456
    vin_2ar = make_valid_vin("4T1", "XD123", "G", "U", "123456")
    test_vin("Toyota 2AR-FE", vin_2ar)
    
    # 3. Toyota 1ZZ-FE
    # WMI: 4T1, VDS: XB123 (Pos 5 is B), Year: 5 (2005), Plant: U, Serial: 123456
    vin_1zz = make_valid_vin("4T1", "XB123", "5", "U", "123456")
    test_vin("Toyota 1ZZ-FE", vin_1zz)

    # 4. Toyota 1GD-FTV (Diesel)
    # WMI: AHT, VDS: XG123 (Pos 5 is G), Year: H (2017), Plant: 0, Serial: 123456
    vin_1gd = make_valid_vin("AHT", "XG123", "H", "0", "123456")
    test_vin("Toyota 1GD-FTV", vin_1gd)

    # 5. Toyota 2GD-FTV (Diesel)
    # WMI: AHT, VDS: XH123 (Pos 5 is H), Year: J (2018), Plant: 0, Serial: 123456
    vin_2gd = make_valid_vin("AHT", "XH123", "J", "0", "123456")
    test_vin("Toyota 2GD-FTV", vin_2gd)

    # 6. Ford Ranger Wildtrak 3.2L (SA)
    # WMI: AFA, VDS: XXMJD... (Pos 8 is D), Year: H (2017), Plant: S (Silverton - fake char, usually P or something), Serial: 123456
    # Note: AFA uses XXMJ for Ranger. Pos 8 is engine.
    # XXMJ + D (Pos 8) = XXMJD
    vin_ranger = make_valid_vin("AFA", "XXMJD", "H", "S", "123456")
    test_vin("Ford Ranger 3.2L SA", vin_ranger)

    # 7. Ford 2.0L Duratorq
    # WMI: WF0 (Ford Europe), VDS: XXGAAT... (Pos 8 is T), Year: K (2019), Plant: G, Serial: 123456
    # Note: VDS must be 5 chars for helper (Pos 4-8). Pos 8 is T.
    # XXGAT -> Pos 8 is T.
    vin_ford_20 = make_valid_vin("WF0", "XXGAT", "K", "G", "123456")
    test_vin("Ford 2.0L Duratorq", vin_ford_20)

    # 8. BMW 320i (B48 Engine - Code G)
    # WMI: WBA, VDS: 3D31G (Pos 8 is G), Year: 0, Plant: A, Serial: 123456
    vin_bmw_320i = make_valid_vin("WBA", "3D31G", "0", "A", "123456")
    test_vin("BMW 320i B48", vin_bmw_320i)

    # 9. BMW 320d (B47 Engine - Code T)
    # WMI: WBA, VDS: 3D31T (Pos 8 is T), Year: 0, Plant: A, Serial: 123456
    vin_bmw_320d = make_valid_vin("WBA", "3D31T", "0", "A", "123456")
    test_vin("BMW 320d B47", vin_bmw_320d)

    # 10. BMW 3 Series SA (AAU WMI + 3 Series VDS)
    # WMI: AAU, VDS: 3D31G (Pos 4='3' -> 3 Series, Pos 8='G' -> B48), Year: 5, Plant: N, Serial: 789012
    vin_bmw_sa = make_valid_vin("AAU", "3D31G", "5", "N", "789012")
    test_vin("BMW 3 Series SA", vin_bmw_sa)

    # 11. VW Polo 6 (AW) SA
    # WMI: AAV, VDS: ZZZAW (Pos 7-8 AW), Year: J (2018), Plant: 7 (Kariega), Serial: 123456
    vin_polo_aw = make_valid_vin("AAV", "ZZZAW", "J", "7", "123456")
    test_vin("VW Polo 6 AW South Africa", vin_polo_aw)

    # 12. VW Amarok (2H) SA
    # WMI: WVW, VDS: ZZZ2H (Pos 7-8 2H), Year: H (2017), Plant: W, Serial: 123456
    vin_amarok = make_valid_vin("WVW", "ZZZ2H", "H", "W", "123456")
    test_vin("VW Amarok 2H South Africa", vin_amarok)

    # 13. VW Polo Vivo SA (6R/9N variant)
    # WMI: AAV, VDS: ZZZ6R (Pos 4-8 starts with ZZZ6R), Year: H (2017), Plant: 7, Serial: 123456
    vin_polo_vivo = make_valid_vin("AAV", "ZZZ6R", "H", "7", "123456")
    test_vin("VW Polo Vivo South Africa", vin_polo_vivo)

    # 14. BMW B58 Engine
    # WMI: WBA, VDS: CL91C (Pos 8 is C), Year: H, Plant: A, Serial: 123456
    vin_b58 = make_valid_vin("WBA", "CL91C", "H", "A", "123456")
    test_vin("BMW B58", vin_b58)

    # 15. Mercedes-Benz C-Class SA
    # WMI: AFV, VDS: 20500 (Pos 4-6 is 205), Year: M (2021), Plant: R, Serial: 123456
    vin_mb_sa = make_valid_vin("AFV", "20500", "M", "R", "123456")
    test_vin("Mercedes-Benz C-Class SA", vin_mb_sa)

    # 16. VW Golf 7 (5G) SA
    # WMI: WVW, VDS: ZZZ5G, Year: F (2015), Plant: W, Serial: 112233
    vin_golf7 = make_valid_vin("WVW", "ZZZ5G", "F", "W", "112233")
    test_vin("VW Golf 7 (5G) SA", vin_golf7)

    # 17. Audi A4 B8 (8K) SA
    # WMI: WAU, VDS: ZZZ8K, Year: D (2013), Plant: A, Serial: 445566
    vin_audi_a4 = make_valid_vin("WAU", "ZZZ8K", "D", "A", "445566")
    test_vin("Audi A4 B8 (8K) SA", vin_audi_a4)

    # 18. Audi Q5 (8R) SA
    # WMI: WAU, VDS: ZZZ8R, Year: E (2014), Plant: A, Serial: 778899
    vin_audi_q5 = make_valid_vin("WAU", "ZZZ8R", "E", "A", "778899")
    test_vin("Audi Q5 (8R) SA", vin_audi_q5)

    # 19. VW Caddy (2K) SA
    # WMI: WV1 (Commercial), VDS: ZZZ2K, Year: G (2016), Plant: W, Serial: 334455
    vin_caddy = make_valid_vin("WV1", "ZZZ2K", "G", "W", "334455")
    test_vin("VW Caddy (2K) SA", vin_caddy)

    # 20. VW Transporter T5 (7H) SA
    # WMI: WVW, VDS: ZZZ7H, Year: E (2014), Plant: H, Serial: 667788
    vin_transporter = make_valid_vin("WVW", "ZZZ7H", "E", "H", "667788")
    test_vin("VW Transporter T5 (7H) SA", vin_transporter)

    # 21. Audi A1 (8X) SA
    # WMI: WAU, VDS: ZZZ8X, Year: F (2015), Plant: A, Serial: 112233
    vin_a1 = make_valid_vin("WAU", "ZZZ8X", "F", "A", "112233")
    test_vin("Audi A1 (8X) SA", vin_a1)

    # 22. Skoda Octavia (5E) SA
    # WMI: TMB, VDS: ZZZ5E, Year: G (2016), Plant: A, Serial: 445566
    # Note: TMB is Skoda Czech.
    vin_octavia = make_valid_vin("TMB", "ZZZ5E", "G", "A", "445566")
    test_vin("Skoda Octavia (5E) SA", vin_octavia)

    # 23. VW Tiguan Mk2 (AD) SA
    # WMI: WVG, VDS: ZZZAD, Year: H (2017), Plant: W, Serial: 778899
    # Note: Tiguan WMI is often WVG (SUV/MPV) or WVW.
    vin_tiguan = make_valid_vin("WVG", "ZZZAD", "H", "W", "778899")
    test_vin("VW Tiguan Mk2 (AD) SA", vin_tiguan)

    # 24. BMW X3 (G01) SA Rosslyn
    # WMI: AAU, VDS: 59123 (Starts with 59), Year: K (2019), Plant: N, Serial: 112233
    vin_x3_sa = make_valid_vin("AAU", "59123", "K", "N", "112233")
    test_vin("BMW X3 (G01) SA Rosslyn", vin_x3_sa)

    # 25. BMW 3 Series (F30) SA Rosslyn
    # WMI: AAU, VDS: 3A51G (Starts with 3, Pos 8 is G -> B48), Year: F (2015), Plant: N, Serial: 445566
    vin_3series_f30_sa = make_valid_vin("AAU", "3A51G", "F", "N", "445566")
    test_vin("BMW 3 Series (F30) SA Rosslyn", vin_3series_f30_sa)

    # 26. BMW 3 Series (G20) SA Rosslyn
    # WMI: AAU, VDS: 5R11G (Pos 8 is G -> B48), Year: L (2020), Plant: N, Serial: 778899
    # Note: Does NOT start with 3. Might fail 'bmw_3series_rosslyn'.
    # Does NOT have G2 at pos 2,3. Might fail 'bmw_series_3_g20_hint'.
    vin_3series_g20_sa = make_valid_vin("AAU", "5R11G", "L", "N", "778899")
    test_vin("BMW 3 Series (G20) SA Rosslyn", vin_3series_g20_sa)

    # 27. BMW X5 (G05) US Import
    # WMI: 5UX, VDS: CR6C (Pos 8 is C -> B58), Year: K (2019), Plant: L, Serial: 990011
    vin_x5_g05 = make_valid_vin("5UX", "CR61C", "K", "L", "990011")
    test_vin("BMW X5 (G05) US Import", vin_x5_g05)


if __name__ == "__main__":
    main()
