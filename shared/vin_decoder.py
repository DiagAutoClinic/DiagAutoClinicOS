import re


class VINDecoder:
    def __init__(self):
        # WMI to Brand mapping (30+ globals)
        self.wmi_to_brand = {
            # Honda/Acura (US/Japan)
            '1HG': 'Honda', '5FN': 'Honda', 'JH2': 'Honda', 'JHM': 'Honda', '2HG': 'Acura',
            # Toyota/Lexus
            'JTE': 'Toyota', 'JTJ': 'Toyota', 'JTD': 'Toyota', '4T1': 'Toyota', 'JT2': 'Toyota',
            'JTH': 'Lexus', 'JT6': 'Lexus',
            # Ford/Lincoln
            '1FA': 'Ford', '1FM': 'Ford', '1FT': 'Ford', '2FM': 'Ford', '3FA': 'Ford',
            '5L1': 'Lincoln', '1LN': 'Lincoln',
            # GM/Chevy/GMC/Cadillac
            '1G1': 'Chevrolet', '1GC': 'GMC', '1G2': 'Pontiac', '1G3': 'Saturn', '1G4': 'Buick',
            '1G6': 'Cadillac', '1G8': 'Saturn', '2G1': 'Chevrolet', '3GC': 'GMC',
            # Nissan/Infiniti
            '1N4': 'Nissan', 'JN1': 'Nissan', 'JN8': 'Nissan', '3N1': 'Nissan',
            'JN3': 'Infiniti',
            # Europe: VW/Audi/BMW/Mercedes
            'WVW': 'Volkswagen', 'WBA': 'BMW', 'WBS': 'BMW', 'WBX': 'BMW',
            'WDD': 'Mercedes', 'WDB': 'Mercedes', 'WME': 'Smart',
            'WAU': 'Audi', 'TRU': 'Audi',
            # Others: Kia/Hyundai/Subaru/Mazda
            'KNA': 'Kia', 'KMH': 'Hyundai', 'ZFA': 'Fiat', 'JF1': 'Subaru',
            'JM1': 'Mazda', '1Y1': 'Mazda',
            # Generic/Euro/Asia fallbacks
            'SAJ': 'Jaguar', 'WP0': 'Porsche', 'VF3': 'Peugeot', 'Z3S': 'Citroen',
            'LVV': 'Volvo', 'YV1': 'Volvo', 'KL1': 'Suzuki', 'MM6': 'Mitsubishi'
        }

    def decode(self, vin):
        vin = vin.strip().upper()
        full_vin = vin  # Keep original for output

        if len(vin) != 17:
            return {'error': 'VIN must be 17 characters', 'full_vin': full_vin}

        # Regex: A-HJ-NPR-Z0-9 (no I/O/Q)
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
            return {
                'error': 'Invalid characters - Use A-H, J-N, P-Z, 0-9 only (no I, O, Q)', 'full_vin': full_vin}

        # VIN sections
        wmi = vin[:3]      # Pos 1-3: Manufacturer
        vds = vin[3:8]     # Pos 4-8: Vehicle Descriptor
        vis = vin[8:]      # Pos 9+: Vehicle Identifier
        year_char = vin[9]  # Pos 10: Model Year
        plant = vin[10]    # Pos 11: Plant
        serial = vin[11:]  # Pos 12-17: Serial

        # Brand
        brand = self.wmi_to_brand.get(wmi, 'Generic')

        # Model estimate (VDS patterns)
        model = self._estimate_model(vds, brand)

        # Year decoder (VIN std: 1980-2009: A=80, 1=01...9=09; 2010+: A=10,
        # B=11... up to Y=30)
        year = self._decode_year(year_char)

        return {
            'full_vin': full_vin,
            'wmi': wmi,
            'vds': vds,
            'vis': vis,
            'brand': brand,
            'model': model,
            'year': year,
            'plant': plant,
            'serial': serial,
            'error': None
        }

    def _decode_year(self, year_char):
        # 1980-2009: A=1980, B=81...Y=2000, 1=2001,2=02...9=09
        pre_2010_codes = {
            'A': 1980, 'B': 1981, 'C': 1982, 'D': 1983, 'E': 1984, 'F': 1985, 'G': 1986, 'H': 1987,
            'J': 1988, 'K': 1989, 'L': 1990, 'M': 1991, 'N': 1992, 'P': 1993, 'R': 1994, 'S': 1995,
            'T': 1996, 'V': 1997, 'W': 1998, 'X': 1999, 'Y': 2000,
            '1': 2001, '2': 2002, '3': 2003, '4': 2004, '5': 2005, '6': 2006, '7': 2007, '8': 2008, '9': 2009
        }

        # 2010+: A=2010, B=11...Y=2030 (no I/O/Q/U/Z)
        post_2010_codes = {
            'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014, 'F': 2015, 'G': 2016, 'H': 2017,
            'J': 2018, 'K': 2019, 'L': 2020, 'M': 2021, 'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025,
            'T': 2026, 'V': 2027, 'W': 2028, 'X': 2029, 'Y': 2030
        }

        # Guess era: If numeric 1-9, likely 2001-09; letters check both
        if year_char.isdigit() and '1' <= year_char <= '9':
            return 2000 + int(year_char)  # e.g., '3' = 2003
        elif year_char in pre_2010_codes:
            year_pre = pre_2010_codes[year_char]
            if year_char in post_2010_codes:  # A-Y overlap
                # Heuristic: If WMI US/Japan (e.g., 1HG), post-2010 more likely
                # if >2009
                if year_pre <= 2009:
                    return year_pre
                else:
                    return post_2010_codes[year_char]  # Prefer newer
            return year_pre
        elif year_char in post_2010_codes:
            return post_2010_codes[year_char]
        else:
            return 'Unknown Year'

    def _estimate_model(self, vds, brand):
        # VDS patterns for models (expandable)
        patterns = {
            'Honda': {
                'CM': 'Accord', 'CM2': 'Civic', 'CM4': 'CR-V', 'CM8': 'Accord',
                'default': 'Generic Honda Model (e.g., Sedan/SUV)'
            },
            'Toyota': {
                'BU': 'RAV4', 'BU5': '4Runner', 'TE': 'Camry', 'GK': 'Highlander',
                'default': 'Generic Toyota Model (e.g., Sedan/SUV)'
            },
            'Ford': {
                'DP': 'F-150', 'DP5': 'Mustang', 'FA': 'Explorer', 'FN': 'Focus',
                'default': 'Generic Ford Model (e.g., Truck/Sedan)'
            },
            'BMW': {
                'WBA': '3 Series', 'WBS': 'M Series', 'default': 'Generic BMW Model'
            },
            # Defaults for others
        }
        brand_patterns = patterns.get(brand, {})
        for key in sorted(
                brand_patterns.keys(), key=len, reverse=True):  # Longer first
            if key in vds:
                return brand_patterns[key]
        return brand_patterns.get(
            'default', f'Generic {brand} Model (e.g., Sedan/SUV)')


# Quick test
if __name__ == "__main__":
    decoder = VINDecoder()
    result = decoder.decode('1HGCM82633A004352')
    print(result)
