"""
src/vin/layer1_iso.py

Layer 1 - Deterministic ISO Decode
Decodes standard VIN positions: WMI (1-3), Model Year (10), Plant (11), Serial (12-17)
All outputs are wrapped in EpistemologicalValue for full provenance and trust tracking.
"""

from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

from .vin_validator_layer0 import validate_vin, VinValidationError
from .models import (
    EpistemologicalValue,
    EpistemologicalStatus,
    SourceType,
    FieldSource,
    verified_value
)

# Model year decoding table (1980-2009 cycle, then 2010+ repeat)
YEAR_CODES = {
    'A': (1980, '1980 or 2010'), 'B': (1981, '1981 or 2011'), 'C': (1982, '1982 or 2012'),
    'D': (1983, '1983 or 2013'), 'E': (1984, '1984 or 2014'), 'F': (1985, '1985 or 2015'),
    'G': (1986, '1986 or 2016'), 'H': (1987, '1987 or 2017'), 'J': (1988, '1988 or 2018'),
    'K': (1989, '1989 or 2019'), 'L': (1990, '1990 or 2020'), 'M': (1991, '1991 or 2021'),
    'N': (1992, '1992 or 2022'), 'P': (1993, '1993 or 2023'), 'R': (1994, '1994 or 2024'),
    'S': (1995, '1995 or 2025'), 'T': (1996, '1996 or 2026'), 'V': (1997, '1997 or 2027'),
    'W': (1998, '1998 or 2028'), 'X': (1999, '1999 or 2029'), 'Y': (2000, '2000 or 2030'),
    '0': (2000, '2000 or 2030'),  # '0' is sometimes used instead of 'Y'
    '1': (2001, '2001'), '2': (2002, '2002'), '3': (2003, '2003'),
    '4': (2004, '2004'), '5': (2005, '2005'), '6': (2006, '2006'),
    '7': (2007, '2007'), '8': (2008, '2008'), '9': (2009, '2009'),
}

# Starter WMI lookup table (expandable)
WMI_TO_MANUFACTURER_COUNTRY = {
    # BMW
    'WBA': ('BMW AG', 'Germany'),
    'WBS': ('BMW M', 'Germany'),
    '5UX': ('BMW USA', 'United States'),
    'WBY': ('BMW i', 'Germany'),
    # VAG
    'WVW': ('Volkswagen', 'Germany'),
    'WVG': ('Volkswagen', 'Germany'),
    'WV1': ('Volkswagen Commercial', 'Germany'),
    'WV2': ('Volkswagen Commercial', 'Germany'),
    'WV3': ('Volkswagen Commercial', 'Germany'),
    'WAU': ('Audi', 'Germany'),
    'TRU': ('Audi', 'Hungary'),
    'TMB': ('Skoda', 'Czech Republic'),
    'VSS': ('SEAT', 'Spain'),
    '3VW': ('Volkswagen', 'Mexico'),
    '3VV': ('Volkswagen', 'Mexico'),
    '1VW': ('Volkswagen', 'United States'),
    '1V2': ('Volkswagen', 'United States'),
    # Mercedes-Benz
    'W1K': ('Mercedes-Benz', 'Germany'),
    'WDB': ('Mercedes-Benz', 'Germany/South Africa'),
    '4JG': ('Mercedes-Benz USA', 'United States'),
    # Toyota / Lexus
    'JTD': ('Toyota', 'Japan'),
    'JTJ': ('Lexus', 'Japan'),
    '4T1': ('Toyota', 'United States'),
    '5TD': ('Toyota', 'United States'),
    # Honda
    'JHM': ('Honda', 'Japan'),
    '1HG': ('Honda', 'United States'),
    # ZA local (examples)
    'AAU': ('BMW South Africa (Rosslyn)', 'South Africa'),
    'ADM': ('Mercedes-Benz South Africa (East London)', 'South Africa'),
    'AFV': ('Mercedes-Benz South Africa', 'South Africa'),
    'AHT': ('Toyota South Africa (Prospecton)', 'South Africa'),
    'AAV': ('Volkswagen South Africa (Kariega)', 'South Africa'),
    'AAM': ('Audi South Africa', 'South Africa'),
    'AFA': ('Ford South Africa (Silverton)', 'South Africa'),
    'WF0': ('Ford Europe', 'Germany'),
}


@dataclass
class IsoLayer1Result:
    """Structured output of Layer 1 with full epistemological wrapping"""
    vin_normalized: str
    wmi: EpistemologicalValue
    manufacturer: EpistemologicalValue
    country_of_origin: EpistemologicalValue
    model_year: EpistemologicalValue
    assembly_plant_code: EpistemologicalValue
    assembly_plant: EpistemologicalValue
    serial_number: EpistemologicalValue


def decode_iso(vin: str) -> IsoLayer1Result:
    """
    Layer 1: Deterministic ISO decode of standard VIN fields.
    All fields are epistemologically annotated (Layer 1 = VERIFIED).
    """
    # Step 0: Validate first (Layer 0)
    is_valid, normalized, error = validate_vin(vin)
    if not is_valid:
        raise VinValidationError(f"Layer 0 validation failed: {error}")

    vin = normalized.upper()

    # Helper to create verified values
    def verified_field(value: Any, field_name: str, unit: Optional[str] = None) -> EpistemologicalValue:
        return verified_value(
            value=value,
            source_id=f"iso_position_{field_name}",
            confidence=1.0,
            unit=unit
        )

    # WMI (positions 1-3)
    wmi = vin[0:3]
    manufacturer, country = WMI_TO_MANUFACTURER_COUNTRY.get(wmi, ("Unknown Manufacturer", "Unknown Country"))
    
    wmi_ev = verified_field(wmi, "wmi")
    mfr_ev = verified_field(manufacturer, "manufacturer")
    country_ev = verified_field(country, "country_of_origin")

    # Model Year (position 10)
    year_code = vin[9]
    if year_code not in YEAR_CODES:
        year_ev = EpistemologicalValue(
            value=None,
            status=EpistemologicalStatus.UNKNOWN,
            confidence=0.0,
            sources=[FieldSource(SourceType.LAYER_1_ISO, "iso_position_10", 0.0)],
            explanation="Invalid year code"
        )
    else:
        base_year, ambiguity_note = YEAR_CODES[year_code]
        # For repeating codes (letters and '0'), there's 30-year cycle ambiguity
        # Without additional context (like serial number patterns), we return the base year
        # More sophisticated logic could examine serial number ranges to disambiguate
        year = base_year
            
        explanation = f"ISO year code '{year_code}' -> {year}"
        if "or" in ambiguity_note:
            explanation += f" (30-year cycle ambiguity: {ambiguity_note})"
        
        year_ev = EpistemologicalValue(
            value=year,
            status=EpistemologicalStatus.VERIFIED,
            confidence=1.0 if "or" not in ambiguity_note else 0.85,  # Lower confidence for ambiguous years
            sources=[FieldSource(SourceType.LAYER_1_ISO, "iso_position_10", 1.0)],
            explanation=explanation
        )

    # Plant Code (position 11)
    plant_code = vin[10]
    plant_name = None  # Plant names are highly OEM-specific -> stub for Layer 1
    plant_code_ev = verified_field(plant_code, "plant_code")
    plant_ev = EpistemologicalValue(
        value=plant_name,
        status=EpistemologicalStatus.UNKNOWN,
        confidence=0.0,
        sources=[FieldSource(SourceType.LAYER_1_ISO, "iso_position_11", 0.0)],
        explanation="Plant name requires manufacturer-specific lookup (Layer 2)"
    )

    # Serial Number (positions 12-17)
    serial = vin[11:17]
    serial_ev = verified_field(serial, "serial_number")

    return IsoLayer1Result(
        vin_normalized=vin,
        wmi=wmi_ev,
        manufacturer=mfr_ev,
        country_of_origin=country_ev,
        model_year=year_ev,
        assembly_plant_code=plant_code_ev,
        assembly_plant=plant_ev,
        serial_number=serial_ev
    )


# Quick smoke test
if __name__ == "__main__":
    try:
        result = decode_iso("WBA5A7C54FG142391")  # Example BMW VIN
        print("Layer 1 Result:")
        for field_name, value in vars(result).items():
            if isinstance(value, EpistemologicalValue):
                print(f"{field_name:18}: {value.value} | {value.status.value} | conf={value.confidence}")
            else:
                print(f"{field_name:18}: {value}")
    except Exception as e:
        print(f"Error: {e}")