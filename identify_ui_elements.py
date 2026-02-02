"""
UI Element Identification Script

Interactive script to identify and label extracted UI elements.
Shows each element and helps determine what it is.
"""

import sys
from pathlib import Path
import json
from PIL import Image
import shutil

print("=" * 70)
print("HoMM3 UI Element Identification")
print("=" * 70)
print()

PROJECT_ROOT = Path(__file__).parent
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted_ui_elements"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
METADATA_FILE = EXTRACTED_DIR / "extraction_metadata.json"
LABELS_FILE = EXTRACTED_DIR / "element_labels.json"

# Load metadata
with open(METADATA_FILE, 'r') as f:
    metadata = json.load(f)

# Load existing labels if any
labels = {}
if LABELS_FILE.exists():
    with open(LABELS_FILE, 'r') as f:
        labels = json.load(f)

print("Element Identification Process")
print("-" * 70)
print()
print("For each extracted UI element, we'll:")
print("1. Show you the image filename and details")
print("2. Suggest possible identities based on position/size")
print("3. Ask you to confirm or provide the correct label")
print()
print("Element categories:")
print("  - adventure_map: End Turn button, Kingdom Overview, etc.")
print("  - resources: Gold icon, Wood icon, etc.")
print("  - ui: Minimap, hero portrait, town icons")
print("  - combat: Attack, Defend, Wait buttons")
print("  - town: Town buildings, recruit buttons")
print()

# Heuristics for identification based on position and size
def suggest_element_type(element_data):
    """
    Suggest what a UI element might be based on position and size.
    """
    x = element_data['position']['x']
    y = element_data['position']['y']
    w = element_data['size']['width']
    h = element_data['size']['height']
    aspect = element_data['aspect_ratio']

    suggestions = []

    # Top-right corner (often resource bar)
    if x > 1200 and y < 100:
        suggestions.append(("resource icon", "high"))

    # Bottom-right corner (often End Turn button or map controls)
    if x > 1200 and y > 600:
        suggestions.append(("map control button", "medium"))
        suggestions.append(("end turn button", "medium"))

    # Top-left corner (often minimap or hero portrait)
    if x < 200 and y < 300:
        if w > 100 and h > 100:
            suggestions.append(("minimap", "high"))
        elif w < 50 and h < 50:
            suggestions.append(("small icon/button", "medium"))

    # Left side buttons (adventure map controls)
    if x < 200 and 100 < y < 700:
        suggestions.append(("adventure map button", "medium"))

    # Center area (heroes, towns, map objects)
    if 300 < x < 1000 and 100 < y < 600:
        if aspect < 0.7:  # Tall
            suggestions.append(("hero on map", "medium"))
        elif 0.9 < aspect < 1.1:  # Square
            suggestions.append(("town icon", "medium"))
            suggestions.append(("map object", "low"))

    # Wide elements (likely text or horizontal UI)
    if aspect > 1.8:
        suggestions.append(("text label", "low"))
        suggestions.append(("horizontal UI element", "low"))

    # Small square elements
    if w < 50 and h < 50 and 0.8 < aspect < 1.2:
        suggestions.append(("small icon", "high"))

    if not suggestions:
        suggestions.append(("unknown UI element", "low"))

    return suggestions

# Count elements
total_elements = sum(len(elements) for elements in metadata['extracted_ui_elements'].values())
labeled_count = len(labels)

print(f"Total elements extracted: {total_elements}")
print(f"Already labeled: {labeled_count}")
print(f"Remaining: {total_elements - labeled_count}")
print()

if labeled_count == total_elements:
    print("[OK] All elements already labeled!")
    print()
    response = input("Do you want to review/edit labels? (y/n): ").strip().lower()
    if response != 'y':
        print("Skipping to organization step...")
        sys.exit(0)

print("=" * 70)
print("Starting Interactive Identification")
print("=" * 70)
print()
print("Commands:")
print("  <category>/<name> - Label element (e.g., 'adventure_map/end_turn_button')")
print("  skip             - Skip this element for now")
print("  done             - Finish and save")
print("  help             - Show this help")
print()

labeled_this_session = 0

try:
    for source_file, elements in metadata['extracted_ui_elements'].items():
        print(f"\n{'=' * 70}")
        print(f"Source: {source_file}")
        print(f"{'=' * 70}\n")

        for element in elements:
            filename = element['filename']

            # Skip if already labeled
            if filename in labels:
                continue

            # Show element info
            print(f"\nElement: {filename}")
            print(f"  Size: {element['size']['width']}x{element['size']['height']} px")
            print(f"  Position: ({element['position']['x']}, {element['position']['y']})")
            print(f"  Aspect ratio: {element['aspect_ratio']:.2f}")

            # Suggest possible types
            suggestions = suggest_element_type(element)
            print(f"\n  Suggestions:")
            for suggestion, confidence in suggestions[:3]:
                print(f"    - {suggestion} (confidence: {confidence})")

            # Get image path
            img_path = EXTRACTED_DIR / filename

            # Prompt user
            print(f"\n  Image file: {img_path}")
            print(f"  (You can open this file to view the element)")
            print()

            label = input("  Label (category/name) or command: ").strip()

            if label == 'done':
                print("\nSaving labels and exiting...")
                break

            elif label == 'skip':
                print("  Skipped.")
                continue

            elif label == 'help':
                print("\n  Examples:")
                print("    adventure_map/end_turn_button")
                print("    resources/gold_icon")
                print("    ui/minimap")
                print("    combat/attack_button")
                continue

            elif '/' in label:
                # Valid label
                category, name = label.split('/', 1)

                labels[filename] = {
                    'category': category,
                    'name': name,
                    'source': source_file,
                    'position': element['position'],
                    'size': element['size'],
                }

                print(f"  [OK] Labeled as: {label}")
                labeled_this_session += 1

            else:
                print(f"  [!] Invalid format. Use: category/name")
                # Don't skip, ask again
                continue

        if label == 'done':
            break

except KeyboardInterrupt:
    print("\n\nInterrupted by user. Saving progress...")

# Save labels
with open(LABELS_FILE, 'w') as f:
    json.dump(labels, f, indent=2)

print()
print("=" * 70)
print("Identification Session Complete")
print("=" * 70)
print()
print(f"Labeled this session: {labeled_this_session}")
print(f"Total labeled: {len(labels)}/{total_elements}")
print(f"Remaining: {total_elements - len(labels)}")
print()
print(f"Labels saved to: {LABELS_FILE}")
print()

if len(labels) > 0:
    print("Next step: Run organization script to copy labeled elements to template library")
    print("  python organize_templates.py")
else:
    print("Run this script again to label more elements.")

print()
