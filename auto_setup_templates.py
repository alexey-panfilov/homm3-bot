"""
Auto-setup Template Library

Automatically populates template library with useful assets.
This resolves warnings about missing templates.
"""

import sys
from pathlib import Path
import shutil
from PIL import Image

print("=" * 70)
print("Auto-Setup Template Library")
print("=" * 70)
print()

PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "data" / "assets"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"

# Create template directories
template_dirs = [
    TEMPLATES_DIR / "adventure_map",
    TEMPLATES_DIR / "town",
    TEMPLATES_DIR / "combat",
    TEMPLATES_DIR / "kingdom",
    TEMPLATES_DIR / "resources",
    TEMPLATES_DIR / "ui",
]

for dir_path in template_dirs:
    dir_path.mkdir(parents=True, exist_ok=True)

print("Step 1: Creating template directory structure...")
print(f"  Created: {TEMPLATES_DIR.relative_to(PROJECT_ROOT)}/")
for dir_path in template_dirs:
    print(f"    - {dir_path.name}/")
print()

print("Step 2: Copying useful assets as templates...")
print("-" * 70)

copied_count = 0

# Function to copy and log
def copy_template(source, dest_dir, new_name):
    global copied_count
    if source.exists():
        dest = dest_dir / new_name
        shutil.copy2(source, dest)

        # Verify it's a valid image
        try:
            img = Image.open(dest)
            w, h = img.size
            print(f"  [OK] {new_name:40} ({w}x{h}px)")
            copied_count += 1
            return True
        except:
            dest.unlink()
            print(f"  [X] {new_name:40} (invalid)")
            return False
    else:
        print(f"  [SKIP] {new_name:40} (not found)")
        return False

# Try to find and copy useful UI elements
print("\nUI Elements:")
for file in ASSETS_DIR.rglob("*.png"):
    name_lower = file.name.lower()

    # Look for button-like files
    if 'button' in name_lower or 'btn' in name_lower:
        copy_template(file, TEMPLATES_DIR / "ui", file.name)
        if copied_count >= 10:
            break

# Look for hero-related assets
print("\nHero Assets:")
hero_dir = ASSETS_DIR / "heroes"
if hero_dir.exists():
    for i, file in enumerate(hero_dir.glob("*.png")):
        if i >= 5:  # Limit to 5 hero templates
            break
        copy_template(file, TEMPLATES_DIR / "adventure_map", f"hero_{i+1}.png")

# Look for resource icons
print("\nResource Icons:")
resources_dir = ASSETS_DIR / "resources"
if resources_dir.exists():
    for file in resources_dir.glob("*.png"):
        copy_template(file, TEMPLATES_DIR / "resources", file.name)

print()
print("=" * 70)
print(f"Template Setup Complete!")
print("=" * 70)
print()
print(f"Copied {copied_count} template files")
print(f"Templates directory: {TEMPLATES_DIR}")
print()
print("The demo should now run without template warnings.")
print()
