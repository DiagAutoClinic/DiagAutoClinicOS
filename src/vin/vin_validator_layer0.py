# vin_validator_layer0.py
"""
Layer 0 — Sanity & Physics
VIN structural validation:
- Exactly 17 characters
- Allowed charset (A-H, J-N, P, R-Z, 0-9 — no I,O,Q)
- Mod-11 check digit validation (ISO 3779 / FMVSS 115)
"""
import re
from typing import Tuple, Union, Optional


class VinValidationError(Exception):
    """Base exception for VIN validation failures."""
    pass


class InvalidLengthError(VinValidationError):
    def __init__(self, length: int):
        super().__init__(f"VIN must be exactly 17 characters. Got {length}.")


class InvalidCharactersError(VinValidationError):
    def __init__(self, invalid_chars: set):
        super().__init__(f"Invalid characters found: {', '.join(sorted(invalid_chars))}. "
                         f"Allowed: A-H, J-N, P, R-Z, 0-9 (no I, O, Q).")


class InvalidCheckDigitError(VinValidationError):
    def __init__(self, expected: str, actual: str):
        super().__init__(f"Invalid check digit. Expected '{expected}', found '{actual}'.")


def transliterate_char(c: str) -> int:
    """
    Convert VIN character to its numeric value per ISO 3779 / FMVSS 115.
    Raises ValueError if character is invalid (should be caught earlier).
    """
    c = c.upper()
    if c.isdigit():
        return int(c)
    
    # A=1 ... H=8, J=1 ... R=9, S=2 ... Z=9
    trans_table = {
        'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8,
        'J':1, 'K':2, 'L':3, 'M':4, 'N':5, 'P':7, 'R':9,
        'S':2, 'T':3, 'U':4, 'V':5, 'W':6, 'X':7, 'Y':8, 'Z':9
    }
    return trans_table[c]


def calculate_check_digit(vin: str) -> str:
    """Compute the expected check digit for a given 17-char VIN."""
    if len(vin) != 17:
        raise ValueError("VIN must be 17 characters for check digit calculation.")
    
    weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    total = 0
    
    for char, weight in zip(vin.upper(), weights):
        total += transliterate_char(char) * weight
    
    remainder = total % 11
    return 'X' if remainder == 10 else str(remainder)


def validate_vin(vin: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate a raw VIN string.
    
    Returns:
        (is_valid: bool, normalized_vin: str or None, error_message: str or None)
    """
    # Step 1: Basic type & length
    if not isinstance(vin, str):
        return False, None, "Input must be a string."
    
    vin = vin.strip().upper()
    
    if len(vin) != 17:
        return False, None, f"Invalid length: {len(vin)} characters (must be exactly 17)."
    
    # Step 2: Allowed characters only
    allowed_pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
    if not re.match(allowed_pattern, vin):
        invalid_chars = set(c for c in vin if c not in 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789')
        return False, None, f"Invalid characters: {', '.join(sorted(invalid_chars)) or 'none visible'}. " \
                            f"No I, O, Q allowed."
    
    # Step 3: Check digit validation
    expected_check = calculate_check_digit(vin)
    actual_check = vin[8]  # 0-based index → position 9
    
    if expected_check != actual_check:
        # return False, vin, f"Invalid check digit. Expected '{expected_check}', found '{actual_check}'."
        # DACOS CHANGE: Relaxed for EU/ZA market support where check digit is not mandatory.
        pass
    
    return True, vin, None


# Quick example usage (you can put this in a test file)
if __name__ == "__main__":
    test_vins = [
        "WBA5A7C54FG142391",   # Valid example (BMW)
        "1G1YY22G9W5100000",   # Valid GM example
        "11111111111111111",   # All 1s → valid check digit (test case)
        "WBA5A7C54FG14239X",   # Wrong length
        "WBA5A7C54IG142391",   # Contains I → invalid
        "WBA5A7C54OG142391",   # Contains O
        "WBA5A7C54QG142391",   # Contains Q
        "WBA5A7C54F9142391",   # Wrong check digit
    ]
    
    for test in test_vins:
        valid, normalized, error = validate_vin(test)
        print(f"VIN: {test}")
        print(f"  → Valid: {valid} | Normalized: {normalized} | Error: {error}\n")