"""
Extract and organize HoMM3 game assets for bot training and template matching.
This script copies relevant UI elements from the game installation to our project.
"""

import sys
from pathlib import Path
import shutil
import json

# Add src to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

# Game installation path (found by find_game_path.py)
GAME_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Heroes of Might & Magic III - HD Edition")
GAME_DATA = GAME_PATH / "data"

# Project paths
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "data" / "assets"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference_screenshots"

print("=" * 70)
print("HoMM3 Asset Extraction Tool")
print("=" * 70)
print()

# Verify game path exists
if not GAME_DATA.exists():
    print(f"[X] Game data directory not found: {GAME_DATA}")
    print("\nPlease update GAME_PATH in this script to match your installation.")
    sys.exit(1)

print(f"[OK] Game data found: {GAME_DATA}")
print()

# Create project directories
print("Creating project asset directories...")
print("-" * 70)

dirs_to_create = [
    ASSETS_DIR,
    ASSETS_DIR / "ui",
    ASSETS_DIR / "cursors",
    ASSETS_DIR / "artifacts",
    ASSETS_DIR / "heroes",
    ASSETS_DIR / "creatures",
    ASSETS_DIR / "resources",
    ASSETS_DIR / "buttons",
    TEMPLATES_DIR,
    TEMPLATES_DIR / "adventure_map",
    TEMPLATES_DIR / "town",
    TEMPLATES_DIR / "combat",
    TEMPLATES_DIR / "kingdom",
    REFERENCE_DIR,
]

for dir_path in dirs_to_create:
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"  [OK] {dir_path.relative_to(PROJECT_ROOT)}")

print()

# Asset categories and their patterns
# We'll organize by looking at filenames and paths
ASSET_PATTERNS = {
    'cursors': {
        'source': 'bitmaps/Cursor_x2',
        'pattern': '*.png',
        'dest': 'cursors',
        'description': 'Mouse cursor graphics',
    },
    'artifacts': {
        'source': 'bitmaps/Cursor_x2/Artifact_HD',
        'pattern': '*.png',
        'dest': 'artifacts',
        'description': 'Artifact icons',
    },
    'ui_elements': {
        'source': 'bitmaps',
        'pattern': '*.png',
        'dest': 'ui',
        'description': 'UI elements (buttons, borders, panels)',
    },
}

print("Extracting game assets...")
print("-" * 70)
print()

asset_catalog = {
    'game_path': str(GAME_PATH),
    'extraction_date': str(Path(__file__).stat().st_mtime),
    'categories': {}
}

total_copied = 0

for category, config in ASSET_PATTERNS.items():
    print(f"Category: {category}")
    print(f"  Description: {config['description']}")

    source_dir = GAME_DATA / config['source']
    dest_dir = ASSETS_DIR / config['dest']

    if not source_dir.exists():
        print(f"  [!] Source not found: {source_dir}")
        print()
        continue

    # Find all matching files
    files = list(source_dir.rglob(config['pattern']))

    print(f"  Found: {len(files)} files")

    # Copy files (limit to reasonable amount for UI elements)
    copied = 0
    file_list = []

    for file in files[:100]:  # Limit to first 100 per category to avoid bloat
        # Create relative path structure
        rel_path = file.relative_to(source_dir)
        dest_file = dest_dir / rel_path

        # Create subdirectories if needed
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        try:
            shutil.copy2(file, dest_file)
            file_list.append({
                'filename': file.name,
                'relative_path': str(rel_path),
                'size': file.stat().st_size,
            })
            copied += 1
        except Exception as e:
            print(f"  [!] Error copying {file.name}: {e}")

    print(f"  Copied: {copied} files to {dest_dir.relative_to(PROJECT_ROOT)}")
    print()

    asset_catalog['categories'][category] = {
        'source': str(source_dir),
        'destination': str(dest_dir),
        'file_count': copied,
        'files': file_list[:20],  # Store first 20 for reference
    }

    total_copied += copied

# Save asset catalog
catalog_file = ASSETS_DIR / "asset_catalog.json"
with open(catalog_file, 'w') as f:
    json.dump(asset_catalog, f, indent=2)

print("=" * 70)
print(f"Extraction complete!")
print("-" * 70)
print(f"Total files copied: {total_copied}")
print(f"Asset catalog saved: {catalog_file.relative_to(PROJECT_ROOT)}")
print()

# Create README in assets directory
readme_content = f"""# HoMM3 Game Assets

This directory contains game assets extracted from Heroes of Might and Magic III HD Edition.

## Source
Game Installation: {GAME_PATH}

## Structure

- **ui/** - User interface elements (buttons, panels, borders)
- **cursors/** - Mouse cursor graphics
- **artifacts/** - Artifact icons
- **heroes/** - Hero portraits and icons
- **creatures/** - Creature sprites
- **resources/** - Resource icons (gold, wood, etc.)
- **buttons/** - Button graphics

## Usage

These assets are used for:
1. **Template Matching** - Identifying UI elements in screenshots
2. **State Detection** - Recognizing game screens (adventure, town, combat)
3. **Object Recognition** - Finding heroes, towns, resources on the map
4. **Training Data** - Reference images for ML models

## Catalog

See `asset_catalog.json` for a detailed manifest of all extracted files.

## License

These assets are property of Ubisoft Entertainment. They are used here under fair use
for development of a personal gaming bot. Do not redistribute.
"""

readme_file = ASSETS_DIR / "README.md"
with open(readme_file, 'w') as f:
    f.write(readme_content)

print(f"[OK] Documentation created: {readme_file.relative_to(PROJECT_ROOT)}")
print()

# Show next steps
print("=" * 70)
print("Next Steps for Phase 2:")
print("-" * 70)
print()
print("1. Take reference screenshots of different game screens:")
print("   - Adventure map with hero")
print("   - Town screen")
print("   - Combat screen")
print("   - Kingdom overview")
print()
print("2. Run the bot in demo mode to capture current screen:")
print("   python run.py --demo")
print()
print("3. Start building template matching for UI elements:")
print("   - Adventure map turn button")
print("   - Hero selection")
print("   - Resource bar")
print()
print("=" * 70)
