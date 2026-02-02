"""
Step 3: Interactive Object Labeling

Shows each extracted object and lets you label it quickly.
Provides smart suggestions based on region and context.

Usage:
    python 3_label_objects.py
"""

import sys
from pathlib import Path
import json
from PIL import Image

print("=" * 70)
print("HoMM3 Interactive Object Labeling")
print("=" * 70)
print()

PROJECT_ROOT = Path(__file__).parent
OBJECTS_DIR = PROJECT_ROOT / "data" / "extracted_objects"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
METADATA_FILE = OBJECTS_DIR / "objects_metadata.json"

# Load metadata
if not METADATA_FILE.exists():
    print("[X] No objects metadata found!")
    print("    Run: python 2_extract_objects.py first")
    sys.exit(1)

with open(METADATA_FILE, 'r') as f:
    objects = json.load(f)

# Count labeled vs unlabeled
labeled_count = sum(1 for obj in objects if obj.get('labeled', False))
unlabeled_count = len(objects) - labeled_count

print(f"Total objects: {len(objects)}")
print(f"Labeled: {labeled_count}")
print(f"Unlabeled: {unlabeled_count}")
print()

if unlabeled_count == 0:
    print("[OK] All objects already labeled!")
    print()
    response = input("Review labels? (y/n): ").strip().lower()
    if response != 'y':
        print("\nDone! Use templates in:", TEMPLATES_DIR)
        sys.exit(0)

print("=" * 70)
print("Interactive Labeling")
print("=" * 70)
print()
print("For each object, you'll see:")
print("  - The extracted image (filename)")
print("  - Region it was found in")
print("  - Suggested category")
print("  - Quick selection options")
print()
print("Commands:")
print("  1-9        Select from quick options")
print("  custom     Type custom category/name")
print("  skip       Skip this object")
print("  done       Finish and save progress")
print("  help       Show this help again")
print()
input("Press Enter to start labeling...")
print()

# Common categories and names based on region
REGION_SUGGESTIONS = {
    'top_right': [
        ('resources', 'gold_icon'),
        ('resources', 'wood_icon'),
        ('resources', 'ore_icon'),
        ('resources', 'resource_icon'),
        ('ui', 'date_indicator'),
    ],
    'bottom_right': [
        ('adventure_map', 'end_turn_button'),
        ('adventure_map', 'sleep_hero_button'),
        ('adventure_map', 'next_hero_button'),
        ('ui', 'map_controls'),
    ],
    'top_left': [
        ('ui', 'minimap'),
        ('ui', 'minimap_icon'),
        ('adventure_map', 'hero_portrait'),
    ],
    'left_panel': [
        ('adventure_map', 'kingdom_overview_button'),
        ('adventure_map', 'underworld_button'),
        ('adventure_map', 'puzzle_map_button'),
        ('adventure_map', 'view_world_button'),
        ('ui', 'left_panel_button'),
    ],
    'bottom_left': [
        ('adventure_map', 'hero_info_panel'),
        ('ui', 'info_panel'),
    ],
    'top_center': [
        ('ui', 'top_bar_element'),
    ],
    'bottom_center': [
        ('ui', 'bottom_bar_element'),
    ],
    'right_panel': [
        ('adventure_map', 'map_zoom_button'),
        ('ui', 'right_panel_button'),
    ],
}

def show_suggestions(region):
    """Show labeling suggestions for a region."""
    suggestions = REGION_SUGGESTIONS.get(region, [('ui', 'unknown_element')])
    print("\n  Quick options:")
    for i, (category, name) in enumerate(suggestions, 1):
        print(f"    [{i}] {category}/{name}")
    return suggestions

# Label objects
labeled_this_session = 0
saved_count = 0

try:
    for obj in objects:
        # Skip if already labeled
        if obj.get('labeled', False):
            continue

        # Show object info
        print("\n" + "=" * 70)
        print(f"Object ID: {obj['id']}")
        print(f"File: {obj['filename']}")
        print(f"Region: {obj['region']}")
        print(f"Position: ({obj['position'][0]}, {obj['position'][1]})")
        print(f"Size: {obj['size'][0]}x{obj['size'][1]} px")
        print(f"From: {obj['screenshot']}")

        # Show image path so user can open it
        img_path = OBJECTS_DIR / obj['filename']
        print(f"\nImage location: {img_path}")
        print("(You can open this file to see the object)")

        # Show suggestions
        suggestions = show_suggestions(obj['region'])

        # Get user input
        print()
        choice = input("Label (1-9, custom, skip, done): ").strip().lower()

        if choice == 'done':
            print("\nSaving and exiting...")
            break

        elif choice == 'skip':
            print("Skipped.")
            continue

        elif choice == 'help':
            print("\n  Commands:")
            print("    1-9: Select from quick options above")
            print("    custom: Type 'category/name' manually")
            print("    skip: Skip this object for now")
            print("    done: Finish and save all labels")
            continue

        elif choice == 'custom':
            custom_label = input("  Enter category/name (e.g., 'adventure_map/end_turn_button'): ").strip()
            if '/' not in custom_label:
                print("  [!] Invalid format. Use: category/name")
                continue
            category, name = custom_label.split('/', 1)

        elif choice.isdigit() and 1 <= int(choice) <= len(suggestions):
            # Quick selection
            idx = int(choice) - 1
            category, name = suggestions[idx]

        else:
            print("  [!] Invalid choice. Try again.")
            continue

        # Label the object
        obj['labeled'] = True
        obj['category'] = category
        obj['name'] = name

        print(f"  [OK] Labeled as: {category}/{name}")
        labeled_this_session += 1

        # Save to template library
        category_dir = TEMPLATES_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Copy to templates with name
        src = OBJECTS_DIR / obj['filename']
        dst = category_dir / f"{name}.png"

        # Check if exists
        if dst.exists():
            overwrite = input(f"  Template {name}.png already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print(f"  Kept existing template")
                continue

        Image.open(src).save(dst)
        saved_count += 1
        print(f"  Saved to: {category}/{name}.png")

        # Save progress after each label
        with open(METADATA_FILE, 'w') as f:
            json.dump(objects, f, indent=2)

except KeyboardInterrupt:
    print("\n\nInterrupted. Saving progress...")

# Final save
with open(METADATA_FILE, 'w') as f:
    json.dump(objects, f, indent=2)

# Summary
print()
print("=" * 70)
print("Labeling Session Complete!")
print("=" * 70)
print()
print(f"Labeled this session: {labeled_this_session}")
print(f"Saved to templates: {saved_count}")
print(f"Total labeled: {sum(1 for obj in objects if obj['labeled'])}/{len(objects)}")
print()

if saved_count > 0:
    print("Templates saved to:", TEMPLATES_DIR)

    # Show template counts
    from collections import Counter
    categories = Counter(obj['category'] for obj in objects if obj.get('labeled'))
    print("\nTemplates by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat:20} {count:3} templates")
    print()

print("To continue labeling, run:")
print("  python 3_label_objects.py")
print()
print("To test templates:")
print("  python demo_phase2.py")
print()
