"""
Template Preparation Script

Organizes extracted game assets into template library for detection.
This script helps you identify and copy useful UI elements.
"""

import sys
from pathlib import Path
import shutil

print("=" * 70)
print("HoMM3 Bot - Template Preparation")
print("=" * 70)
print()

PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "data" / "assets"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"

# Check if assets were extracted
if not ASSETS_DIR.exists() or not any(ASSETS_DIR.iterdir()):
    print("[X] Game assets not found!")
    print()
    print("You need to extract game assets first:")
    print("  python extract_game_assets.py")
    print()
    sys.exit(1)

print(f"[OK] Assets directory found: {ASSETS_DIR}")
print()

# Count available assets
asset_count = sum(1 for _ in ASSETS_DIR.rglob("*.png"))
print(f"Available assets: {asset_count} PNG files")
print()

print("Template Categories Needed:")
print("-" * 70)
print()

# Define what templates we need for each parser
template_needs = {
    "Adventure Map": [
        "end_turn_button.png - The 'End Turn' button",
        "kingdom_overview_button.png - Kingdom overview icon",
        "hero_marker.png - Hero indicator on map",
        "hero_selected.png - Selected hero indicator",
        "town_castle.png - Castle town icon",
        "town_rampart.png - Rampart town icon",
    ],
    "Resource Bar": [
        "resource_gold_icon.png - Gold coin icon",
        "resource_wood_icon.png - Wood resource icon",
        "resource_ore_icon.png - Ore resource icon",
    ],
    "Turn Detection": [
        "end_turn_button.png - Active End Turn button",
        "end_turn_button_inactive.png - Grayed out End Turn",
        "ai_turn_hourglass.png - Hourglass during AI turn",
    ],
}

for category, templates in template_needs.items():
    print(f"\n{category}:")
    for template in templates:
        print(f"  • {template}")

print()
print("=" * 70)
print("Options:")
print("=" * 70)
print()
print("Option 1: MANUAL TEMPLATE CREATION (Recommended)")
print("-" * 70)
print("1. Start HoMM3 and take screenshots of:")
print("   - Adventure map with UI visible")
print("   - Various towns and heroes")
print("   - Combat screen")
print()
print("2. Use an image editor to crop UI elements:")
print("   - End Turn button (~100x30 pixels)")
print("   - Hero markers (~48x48 pixels)")
print("   - Resource icons (~24x24 pixels)")
print()
print("3. Save cropped images to:")
print(f"   {TEMPLATES_DIR}/")
print()
print("   With names like:")
print("   - adventure_map/end_turn_button.png")
print("   - adventure_map/hero_marker.png")
print("   - resources/gold_icon.png")
print()

print("Option 2: USE EXISTING ASSETS")
print("-" * 70)
print("Browse extracted assets and copy useful ones:")
print(f"  Source: {ASSETS_DIR}/")
print(f"  Target: {TEMPLATES_DIR}/")
print()
print("Look for files like:")
print("  - Button graphics in ui/")
print("  - Cursor graphics in cursors/")
print("  - Icons in artifacts/")
print()

print("Option 3: AUTO-ORGANIZE (EXPERIMENTAL)")
print("-" * 70)
print("Let the script try to organize assets automatically.")
print()

choice = input("Choose option (1/2/3) or 'q' to quit: ").strip()

if choice == 'q':
    print("\nExiting. Run this script again when ready.")
    sys.exit(0)

elif choice == '1':
    print()
    print("Manual Template Creation Guide:")
    print("-" * 70)
    print()
    print("STEP 1: Take Screenshots")
    print("  - Run HoMM3 in windowed mode")
    print("  - Press F12 or use Snipping Tool")
    print("  - Save to data/reference_screenshots/")
    print()
    print("STEP 2: Crop UI Elements")
    print("  - Use Paint.NET, GIMP, or Photoshop")
    print("  - Crop just the UI element (no background)")
    print("  - Save as PNG with transparency if possible")
    print()
    print("STEP 3: Name and Organize")
    print("  Templates directory structure:")
    print(f"  {TEMPLATES_DIR}/")
    print("    adventure_map/")
    print("      end_turn_button.png")
    print("      hero_marker.png")
    print("      kingdom_button.png")
    print("    town/")
    print("      castle_icon.png")
    print("      town_hall.png")
    print("    combat/")
    print("      attack_button.png")
    print("      defend_button.png")
    print()
    print(f"Create directories manually or script will create them")
    print()

elif choice == '2':
    print()
    print(f"Opening assets directory: {ASSETS_DIR}")
    print(f"Templates should go to: {TEMPLATES_DIR}")
    print()
    print("Copy useful files manually, renaming them descriptively.")
    print()

    # Create template directories
    template_dirs = [
        TEMPLATES_DIR / "adventure_map",
        TEMPLATES_DIR / "town",
        TEMPLATES_DIR / "combat",
        TEMPLATES_DIR / "kingdom",
        TEMPLATES_DIR / "resources",
    ]

    for dir_path in template_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created: {dir_path.relative_to(PROJECT_ROOT)}")

    print()
    # Open file explorer (Windows)
    import subprocess
    try:
        subprocess.run(['explorer', str(ASSETS_DIR)])
        subprocess.run(['explorer', str(TEMPLATES_DIR)])
        print("[OK] Opened folders in Windows Explorer")
    except:
        print("[!] Could not open Explorer automatically")

elif choice == '3':
    print()
    print("Auto-organizing assets...")
    print("-" * 70)

    # Create directories
    (TEMPLATES_DIR / "adventure_map").mkdir(parents=True, exist_ok=True)
    (TEMPLATES_DIR / "resources").mkdir(parents=True, exist_ok=True)
    (TEMPLATES_DIR / "ui").mkdir(parents=True, exist_ok=True)

    # Try to find and copy potentially useful files
    copied = 0

    # Look for button-like files
    for file in ASSETS_DIR.rglob("*.png"):
        name_lower = file.name.lower()

        # Skip very large or very small files (likely not UI elements)
        try:
            from PIL import Image
            img = Image.open(file)
            w, h = img.size

            if w < 10 or h < 10 or w > 500 or h > 500:
                continue

            # Copy potentially useful files
            if any(keyword in name_lower for keyword in ['button', 'icon', 'ui']):
                dest = TEMPLATES_DIR / "ui" / file.name
                shutil.copy2(file, dest)
                print(f"  Copied: {file.name}")
                copied += 1

                if copied >= 20:  # Limit to avoid copying too much
                    break
        except:
            continue

    print()
    print(f"[OK] Copied {copied} potential UI elements")
    print()
    print("These need to be reviewed and renamed appropriately.")
    print(f"Check: {TEMPLATES_DIR}/ui/")

else:
    print("\nInvalid choice. Exiting.")
    sys.exit(1)

print()
print("=" * 70)
print("Template Preparation Complete!")
print("=" * 70)
print()
print("Once you have templates ready:")
print("  python demo_phase2.py")
print()
