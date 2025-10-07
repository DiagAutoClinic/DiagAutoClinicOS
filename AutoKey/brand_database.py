#!/usr/bin/env python3
"""
Global Automotive Brand Database
Top 25 most driven brands with their specific protocols and systems
"""

BRAND_DATABASE = {
    "Toyota": {
        "region": "Japan",
        "diagnostic_protocols": ["ISO 15765-4 (CAN)", "ISO 14230-4 (KWP2000)", "ISO 9141-2"],
        "common_ecus": ["ECM", "TCM", "ABS", "SRS", "Body ECU", "Immobilizer"],
        "key_systems": ["Smart Key", "G-Box", "ID4C", "ID4D"],
        "pin_codes": ["Smart Code System", "Nissan-ECU-Clone"],
        "obd_protocol": "J1939, J1979",
        "market_share": "10.5%"
    },
    "Volkswagen": {
        "region": "Germany",
        "diagnostic_protocols": ["UDS (ISO 14229)", "KWP2000", "TP 2.0"],
        "common_ecus": ["Engine ECU", "DSG", "ABS/ESP", "Airbag", "Instrument Cluster"],
        "key_systems": ["VVDI", "Immo 4/5", "Megamos Crypto"],
        "pin_codes": ["SKC Calculator", "VAG Commander"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "7.8%"
    },
    "Hyundai": {
        "region": "South Korea",
        "diagnostic_protocols": ["K-Line", "CAN", "UDS"],
        "common_ecus": ["PCM", "TCM", "ABS", "Immobilizer", "Smart Key"],
        "key_systems": ["Hyundai HS", "Hitag2", "AES"],
        "pin_codes": ["PIN from VIN", "Dealer System"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "7.2%"
    },
    "Ford": {
        "region": "USA",
        "diagnostic_protocols": ["MS-CAN", "HS-CAN", "UDS", "J1850 PWM"],
        "common_ecus": ["PCM", "GEM", "IC", "ABS", "PAT"],
        "key_systems": ["PATS", "Smart Access", "MyKey"],
        "pin_codes": ["PATS Code", "Dealer PIN"],
        "obd_protocol": "J1850, ISO 15765-4",
        "market_share": "5.1%"
    },
    "Honda": {
        "region": "Japan",
        "diagnostic_protocols": ["K-Line", "CAN", "HDS Protocol"],
        "common_ecus": ["PCM", "BCM", "SRS", "ABS", "Immobilizer"],
        "key_systems": ["Honda Smart", "Nissan-ECU-Clone"],
        "pin_codes": ["PIN Code", "Immobilizer Code"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "4.9%"
    },
    "Nissan": {
        "region": "Japan",
        "diagnostic_protocols": ["CONSULT-III", "K-Line", "CAN"],
        "common_ecus": ["ECM", "BCM", "NATS", "ABS", "Airbag"],
        "key_systems": ["NATS", "Intelligent Key", "Hitag2"],
        "pin_codes": ["NATS Code", "BCM PIN"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "4.5%"
    },
    "Chevrolet": {
        "region": "USA",
        "diagnostic_protocols": ["GMLAN", "UDS", "J1850 VPW"],
        "common_ecus": ["PCM", "BCM", "TCM", "ABS", "Immobilizer"],
        "key_systems": ["Passlock", "VATS", "Smart Key"],
        "pin_codes": ["Security Code", "Dealer PIN"],
        "obd_protocol": "J1850, ISO 15765-4",
        "market_share": "4.3%"
    },
    "Kia": {
        "region": "South Korea",
        "diagnostic_protocols": ["K-Line", "CAN", "UDS"],
        "common_ecus": ["PCM", "TCM", "Immobilizer", "Smart Key"],
        "key_systems": ["Kia HS", "Hitag2", "AES"],
        "pin_codes": ["PIN from VIN", "Dealer System"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "4.1%"
    },
    "Mercedes-Benz": {
        "region": "Germany",
        "diagnostic_protocols": ["XENTRY", "UDS", "KWP2000"],
        "common_ecus": ["SAM", "ESM", "DAS", "ABS", "Airbag"],
        "key_systems": ["DAS", "Keyless Go", "EIS"],
        "pin_codes": ["Dealer PIN", "SCR Code"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "3.8%"
    },
    "BMW": {
        "region": "Germany",
        "diagnostic_protocols": ["ISTA", "UDS", "KWP2000"],
        "common_ecus": ["DME", "EGS", "CAS", "DSC", "Airbag"],
        "key_systems": ["CAS", "FEM", "BDC", "Comfort Access"],
        "pin_codes": ["ISN Code", "Dealer PIN"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "3.5%"
    },
    # Additional brands...
    "Audi": {
        "region": "Germany",
        "diagnostic_protocols": ["VAS", "UDS", "KWP2000"],
        "common_ecus": ["Engine", "Transmission", "Immobilizer", "MMI"],
        "key_systems": ["Audi Smart", "Advanced Key"],
        "pin_codes": ["Dealer PIN", "Component Protection"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "2.9%"
    },
    "Renault": {
        "region": "France",
        "diagnostic_protocols": ["CAN Clip", "UDS", "KWP2000"],
        "common_ecus": ["UCH", "Engine ECU", "BSI", "ABS"],
        "key_systems": ["Renault Card", "Hitag2"],
        "pin_codes": ["PIN Code", "UCH Code"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "2.7%"
    },
    "Peugeot": {
        "region": "France",
        "diagnostic_protocols": ["Diagbox", "UDS", "KWP2000"],
        "common_ecus": ["BSI", "Engine ECU", "ABS", "Airbag"],
        "key_systems": ["Peugeot Card", "Hitag2"],
        "pin_codes": ["PIN Code", "BSI Code"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "2.5%"
    },
    "Fiat": {
        "region": "Italy",
        "diagnostic_protocols": ["Examiner", "KWP2000", "CAN"],
        "common_ecus": ["Body Computer", "Engine ECU", "ABS"],
        "key_systems": ["Fiat Code", "Blue&Me"],
        "pin_codes": ["Code Card", "Dealer PIN"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "2.3%"
    },
    "Volvo": {
        "region": "Sweden",
        "diagnostic_protocols": ["VIDA", "UDS", "KWP2000"],
        "common_ecus": ["CEM", "ECM", "DEM", "BCM"],
        "key_systems": ["Volvo Key", "Passive Entry"],
        "pin_codes": ["Dealer PIN", "CPO Code"],
        "obd_protocol": "ISO 15765-4",
        "market_share": "2.1%"
    },
    "Mazda": {
	"region": "Japan",
	"diagnostic_protocols": ["Mazda Diagnostic", "CAN", "K-Line"],
	"common_ecus": ["PCM", "TCM", "ABS", "Immobilizer"],
	"key_systems": ["Mazda Advanced Key", "Flip Key"],
	"pin_codes": ["Dealer PIN", "Immobilizer Code"],
	"obd_protocol": "ISO 15765-4",
	"market_share": "2.0%"
    },
    "Subaru": {
	"region": "Japan", 
	"diagnostic_protocols": ["Subaru Select Monitor", "CAN"],
	"common_ecus": ["ECM", "TCM", "ABS", "Body Integrated Unit"],
	"key_systems": ["Subaru Keyless", "Smart Key"],
	"pin_codes": ["PIN Code", "Security Code"],
	"obd_protocol": "ISO 15765-4",
	"market_share": "1.8%"
    },
}


def get_brand_list():
    """Return list of all supported brands"""
    return list(BRAND_DATABASE.keys())


def get_brand_info(brand_name):
    """Get detailed information for a specific brand"""
    return BRAND_DATABASE.get(brand_name, {})


def get_brands_by_region(region):
    """Get all brands from a specific region"""
    return [brand for brand, info in BRAND_DATABASE.items()
            if info.get('region') == region]


def get_brands_by_protocol(protocol):
    """Get brands that use a specific diagnostic protocol"""
    return [brand for brand, info in BRAND_DATABASE.items()
            if protocol in info.get('diagnostic_protocols', [])]
