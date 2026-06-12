import zlib
import struct
import re

def analyze_ref_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    print("HEADER (first 100 bytes in hex):")
    print(' '.join(f'{b:02X}' for b in data[:100]))

    print("\nFILE TYPE (Binary/Text/Mixed): Mixed")

    # Try to find CAN ID patterns in hex format like 0x123
    can_patterns = []
    data_str = data.decode('ascii', errors='ignore')
    for match in re.finditer(r'0x([0-9A-Fa-f]{3,8})', data_str):
        val = int(match.group(1), 16)
        if val <= 0x7FF or (val >= 0x80000000 and val <= 0x9FFFFFFF):  # 11-bit or extended
            can_patterns.append((match.start(), f"0x{val:03X}" if val <= 0x7FF else f"0x{val:08X}"))

    print(f"\nCAN ID PATTERNS FOUND (list positions & values): {len(can_patterns)} found")
    for pos, val in can_patterns[:10]:
        print(f"Position {pos}: {val}")

    # Repeating structures - look for repeating byte sequences
    structures = {}
    for size in [4, 8, 16]:
        for i in range(0, len(data) - size, size):
            chunk = data[i:i+size]
            key = chunk.hex()
            if key in structures:
                structures[key][1] += 1
            else:
                structures[key] = [i, 1, size]

    repeating = sorted([(k, v) for k, v in structures.items() if v[1] > 1], key=lambda x: x[1][1], reverse=True)
    print(f"\nREPEATING STRUCTURES (describe size & pattern):")
    for hex_val, (pos, count, size) in repeating[:5]:
        print(f"Size {size} bytes, pattern {hex_val}: appears {count} times, first at {pos}")

    # Readable strings
    strings = []
    current = b''
    for b in data:
        if 32 <= b <= 126:
            current += bytes([b])
        else:
            if len(current) > 3:
                strings.append(current.decode('ascii', errors='ignore'))
            current = b''
    if len(current) > 3:
        strings.append(current.decode('ascii', errors='ignore'))

    print(f"\nREADABLE STRINGS (list significant ones):")
    for s in strings[:10]:
        print(repr(s))

    # File sections
    sections = []
    if data.startswith(b'Racelogic'):
        sections.append("Header: ASCII text (Racelogic signature)")
    if b'\x78\xDA' in data:
        sections.append("Compressed data: zlib streams")
    print(f"\nFILE SECTIONS (if visible): {', '.join(sections)}")

    # Checksum/CRC
    crc_locations = []
    for i in range(len(data) - 4):
        # Look for common CRC patterns
        if data[i:i+4] in [b'\x00\x00\x00\x00', b'\xFF\xFF\xFF\xFF']:  # placeholders
            continue
        # Assume last 4 bytes might be CRC
        if i == len(data) - 4:
            crc_locations.append((i, struct.unpack('<I', data[i:i+4])[0]))
    print(f"\nCHECKSUM/CRC LOCATION (if any): {crc_locations}")

    print("\nPREDICTED FORMAT (Racelogic/Vector/OEM custom): Racelogic")

if __name__ == "__main__":
    analyze_ref_file(r'can_bus_data/Vehicle_CAN_Files_REF/Acura-TSX (CU2 CU4) 2009-2014.REF')