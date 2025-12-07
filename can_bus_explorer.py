#!/usr/bin/env python3
"""
🏎️ CAN Bus Reference File Explorer - Entertainment Edition 🏎️
Explore the fascinating world of vehicle CAN bus data!
"""

import os
import random
from pathlib import Path
from collections import defaultdict

# Fun facts about vehicles
VEHICLE_FACTS = {
    "Ferrari": "🏎️ Ferrari's prancing horse logo was originally on WWI fighter planes!",
    "Lamborghini": "🐂 Lamborghini started as a tractor company before making supercars!",
    "BMW": "🔵 BMW's logo represents a spinning propeller - they made aircraft engines!",
    "Audi": "⭕ Audi's four rings represent four companies that merged in 1932!",
    "Porsche": "🏁 The Porsche 911 has been in production since 1964!",
    "McLaren": "🧡 McLaren's orange color is called 'Papaya Orange' - Bruce McLaren's favorite!",
    "Lotus": "🪶 Lotus founder Colin Chapman's motto: 'Simplify, then add lightness'",
    "Aston Martin": "🎬 Aston Martin has appeared in 14 James Bond films!",
    "Mercedes": "⭐ Mercedes-Benz's three-pointed star represents land, sea, and air!",
    "Honda": "🏍️ Honda is the world's largest motorcycle manufacturer!",
    "Toyota": "🔺 Toyota's logo contains all letters of 'TOYOTA' hidden in the ovals!",
    "Nissan": "☀️ Nissan means 'sun origin' in Japanese!",
    "Chevrolet": "🎀 The Chevy bowtie logo may have been inspired by wallpaper!",
    "Ford": "🔵 Ford's blue oval has been used since 1927!",
    "Dodge": "🐏 The Dodge Ram logo represents determination and strength!",
}

def get_vehicle_stats(ref_dir):
    """Analyze the collection of REF files"""
    files = list(Path(ref_dir).glob("*.REF"))
    
    # Categorize by manufacturer
    manufacturers = defaultdict(list)
    for f in files:
        name = f.stem
        if "-" in name:
            make = name.split("-")[0]
            model = name.split("-", 1)[1]
            manufacturers[make].append(model)
    
    return manufacturers, len(files)

def display_banner():
    """Display a cool ASCII banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🏎️  CAN BUS REFERENCE FILE EXPLORER  🏎️                      ║
    ║  ═══════════════════════════════════════                      ║
    ║  Exploring the digital heartbeat of vehicles!                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def display_manufacturer_chart(manufacturers):
    """Display a visual chart of manufacturers"""
    print("\n📊 MANUFACTURER DISTRIBUTION:")
    print("=" * 60)
    
    # Sort by count
    sorted_makes = sorted(manufacturers.items(), key=lambda x: len(x[1]), reverse=True)
    max_count = max(len(v) for v in manufacturers.values())
    
    for make, models in sorted_makes[:15]:  # Top 15
        bar_length = int((len(models) / max_count) * 40)
        bar = "█" * bar_length
        print(f"{make:20} │{bar} ({len(models)})")
        
        # Show fun fact if available
        if make in VEHICLE_FACTS:
            print(f"                     └─ {VEHICLE_FACTS[make]}")

def display_racing_cars(manufacturers):
    """Show racing/GT cars in the collection"""
    print("\n🏁 RACING & GT CARS IN COLLECTION:")
    print("=" * 60)
    
    racing_keywords = ["GT3", "GT4", "Racing", "Cup", "Challenge", "LMS", "TCR"]
    racing_cars = []
    
    for make, models in manufacturers.items():
        for model in models:
            if any(kw in model for kw in racing_keywords):
                racing_cars.append(f"{make} {model}")
    
    for car in sorted(racing_cars):
        print(f"  🏎️ {car}")
    
    print(f"\n  Total racing cars: {len(racing_cars)}")

def display_year_analysis(manufacturers):
    """Analyze year ranges in the collection"""
    print("\n📅 YEAR COVERAGE ANALYSIS:")
    print("=" * 60)
    
    import re
    years = []
    for make, models in manufacturers.items():
        for model in models:
            # Extract years from model names
            found_years = re.findall(r'(19\d{2}|20\d{2})', model)
            years.extend([int(y) for y in found_years])
    
    if years:
        print(f"  Earliest year: {min(years)}")
        print(f"  Latest year: {max(years)}")
        print(f"  Year span: {max(years) - min(years)} years of automotive history!")
        
        # Decade breakdown
        decades = defaultdict(int)
        for y in years:
            decade = (y // 10) * 10
            decades[decade] += 1
        
        print("\n  📊 Decade breakdown:")
        for decade in sorted(decades.keys()):
            bar = "▓" * (decades[decade] // 2)
            print(f"    {decade}s: {bar} ({decades[decade]})")

def display_exotic_cars(manufacturers):
    """Highlight exotic and rare manufacturers"""
    print("\n💎 EXOTIC & RARE MANUFACTURERS:")
    print("=" * 60)
    
    exotic_makes = ["Ferrari", "Lamborghini", "McLaren", "Aston Martin", 
                    "Lotus", "Porsche", "BAC", "Gumpert", "Ariel", "KTM",
                    "Pagani", "Koenigsegg", "Bugatti"]
    
    for make in exotic_makes:
        if make in manufacturers:
            models = manufacturers[make]
            print(f"\n  🌟 {make}:")
            for model in models:
                print(f"      └─ {model}")

def display_motorcycle_section(manufacturers):
    """Show motorcycles in the collection"""
    print("\n🏍️ MOTORCYCLES IN COLLECTION:")
    print("=" * 60)
    
    bike_makes = ["BMW", "Kawasaki", "Aprilia", "Ducati", "Honda", "Yamaha", "KTM"]
    bike_keywords = ["S1000RR", "ZZR", "RSV", "K40", "Panigale"]
    
    bikes_found = []
    for make, models in manufacturers.items():
        for model in models:
            if any(kw in model for kw in bike_keywords):
                bikes_found.append(f"{make} {model}")
    
    for bike in bikes_found:
        print(f"  🏍️ {bike}")

def display_ecu_systems(manufacturers):
    """Show ECU/data logging systems"""
    print("\n🖥️ ECU & DATA LOGGING SYSTEMS:")
    print("=" * 60)
    
    ecu_makes = ["AiM", "Haltech", "Emerald", "DTAFast", "Emtron", 
                 "Life Racing", "MaxxECU", "Hondata", "MoTeC"]
    
    for make in ecu_makes:
        if make in manufacturers:
            models = manufacturers[make]
            print(f"\n  📟 {make}:")
            for model in models:
                print(f"      └─ {model}")

def random_car_spotlight(manufacturers):
    """Spotlight a random car from the collection"""
    print("\n🎲 RANDOM CAR SPOTLIGHT:")
    print("=" * 60)
    
    all_cars = []
    for make, models in manufacturers.items():
        for model in models:
            all_cars.append(f"{make} {model}")
    
    if all_cars:
        spotlight = random.choice(all_cars)
        print(f"\n  ✨ Today's featured vehicle: {spotlight}")
        
        # Add some flair
        make = spotlight.split()[0] if spotlight else ""
        if make in VEHICLE_FACTS:
            print(f"\n  💡 Fun fact: {VEHICLE_FACTS[make]}")

def main():
    """Main entertainment function"""
    display_banner()
    
    ref_dir = Path(__file__).parent / "can_bus_data" / "Vehicle_CAN_Files_REF"
    
    if not ref_dir.exists():
        print(f"❌ REF directory not found: {ref_dir}")
        return
    
    manufacturers, total_files = get_vehicle_stats(ref_dir)
    
    print(f"\n📁 Total REF files found: {total_files}")
    print(f"🏭 Total manufacturers: {len(manufacturers)}")
    
    display_manufacturer_chart(manufacturers)
    display_racing_cars(manufacturers)
    display_exotic_cars(manufacturers)
    display_year_analysis(manufacturers)
    display_motorcycle_section(manufacturers)
    display_ecu_systems(manufacturers)
    random_car_spotlight(manufacturers)
    
    print("\n" + "=" * 60)
    print("🏁 Exploration complete! These REF files contain CAN bus")
    print("   definitions for vehicle diagnostics and data logging.")
    print("=" * 60)

if __name__ == "__main__":
    main()
