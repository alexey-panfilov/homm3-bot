"""
Organize Templates Script

Copies identified UI elements to the template library with proper organization.
"""

import sys
from pathlib import Path
import json
import shutil
from collections import defaultdict

print("=" * 70)
print("HoMM3 Template Organization")
print("=" * 70)
print()

PROJECT_ROOT = Path(__file__).parent
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted_ui_elements"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
AUTO_LABELS_FILE = EXTRACTED_DIR / "auto_labels.json"

# Load auto-labels
if not AUTO_LABELS_FILE.exists():
    print("[X] No auto-labels file found!")
    print("    Run: python auto_identify_ui_elements.py first")
    sys.exit(1)

with open(AUTO_LABELS_FILE, 'r') as f:
    labels = json.load(f)

print(f"Loaded {len(labels)} labeled elements")
print()

# Group by category
by_category = defaultdict(list)
for filename, data in labels.items():
    category = data['category']
    if category != 'unknown':  # Skip unknown elements
        by_category[category].append((filename, data))

print("Elements by category:")
for category, elements in sorted(by_category.items()):
    print(f"  {category:20} {len(elements):3} elements")
print()

# Ask user to confirm
print("This will copy labeled elements to:")
print(f"  {TEMPLATES_DIR}/")
print()
response = input("Proceed with organization? (y/n): ").strip().lower()

if response != 'y':
    print("Canceled.")
    sys.exit(0)

print()
print("Organizing templates...")
print("-" * 70)

# Copy files
copied_count = 0
skipped_count = 0

for category, elements in sorted(by_category.items()):
    category_dir = TEMPLATES_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{category}/")

    for filename, data in elements:
        source = EXTRACTED_DIR / filename
        target_name = f"{data['name']}.png"
        target = category_dir / target_name

        # Check if already exists
        if target.exists():
            # Check if we should overwrite
            if data['confidence'] > 0.6:  # Only overwrite if high confidence
                shutil.copy2(source, target)
                print(f"  [REPLACE] {target_name}")
                copied_count += 1
            else:
                print(f"  [SKIP] {target_name} (already exists, low confidence)")
                skipped_count += 1
        else:
            shutil.copy2(source, target)
            print(f"  [OK] {target_name}")
            copied_count += 1

print()
print("=" * 70)
print("Organization Complete!")
print("=" * 70)
print()
print(f"Copied: {copied_count} templates")
print(f"Skipped: {skipped_count} templates (duplicates or low confidence)")
print()
print(f"Template library: {TEMPLATES_DIR}")
print()

# Count files in each category
print("Template library contents:")
for category_dir in sorted(TEMPLATES_DIR.iterdir()):
    if category_dir.is_dir():
        count = len(list(category_dir.glob("*.png")))
        print(f"  {category_dir.name:20} {count:3} templates")
print()

print("Next steps:")
print("1. Review templates in:", TEMPLATES_DIR)
print("2. Test with demo: python demo_phase2.py")
print("3. Manually correct any incorrect labels if needed")
print()
