"""
Step 2: Extract UI Objects from Screenshots

Analyzes captured screenshots and extracts distinct UI elements.
Each element is saved with metadata for labeling.

Usage:
    python 2_extract_objects.py
"""

import sys
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image

print("=" * 70)
print("HoMM3 UI Object Extraction")
print("=" * 70)
print()

PROJECT_ROOT = Path(__file__).parent
CAPTURES_DIR = PROJECT_ROOT / "data" / "gameplay_captures"
OBJECTS_DIR = PROJECT_ROOT / "data" / "extracted_objects"
OBJECTS_DIR.mkdir(parents=True, exist_ok=True)

# Check for captures
captures = list(CAPTURES_DIR.glob("capture_*.png"))
if not captures:
    print("[X] No gameplay captures found!")
    print(f"    Run: python 1_capture_gameplay.py first")
    print(f"    Looking in: {CAPTURES_DIR}")
    sys.exit(1)

print(f"Found {len(captures)} captured screenshots")
print()

# Extract UI regions that might be buttons/icons
def extract_ui_objects(image_path, screenshot_name):
    """
    Extract distinct UI objects from a screenshot.
    Focuses on common UI positions (edges, corners).
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return []

    h, w = img.shape[:2]
    objects = []

    # Define regions of interest (ROI) where UI elements typically are
    regions = {
        'top_left': (0, 0, 200, 150),           # Minimap area
        'top_center': (w//2 - 100, 0, 200, 100), # Top bar
        'top_right': (w - 200, 0, 200, 150),    # Resources
        'left_panel': (0, 150, 100, h - 150),   # Left buttons
        'bottom_left': (0, h - 150, 200, 150),  # Bottom left UI
        'bottom_center': (w//2 - 150, h - 100, 300, 100), # Bottom center
        'bottom_right': (w - 200, h - 150, 200, 150), # End Turn area
        'right_panel': (w - 100, 150, 100, h - 300), # Right buttons
    }

    for region_name, (rx, ry, rw, rh) in regions.items():
        # Extract region
        roi = img[ry:ry+rh, rx:rx+rw]

        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Edge detection
        edges = cv2.Canny(gray, 30, 100)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w_obj, h_obj = cv2.boundingRect(contour)

            # Filter by size (buttons/icons are typically 20-120 pixels)
            if 20 <= w_obj <= 120 and 20 <= h_obj <= 120:
                # Calculate absolute position
                abs_x = rx + x
                abs_y = ry + y

                # Extract object
                obj_img = img[abs_y:abs_y+h_obj, abs_x:abs_x+w_obj]

                objects.append({
                    'image': obj_img,
                    'region': region_name,
                    'position': (abs_x, abs_y),
                    'size': (w_obj, h_obj),
                    'screenshot': screenshot_name,
                })

    return objects

# Process all captures
print("Extracting UI objects from screenshots...")
print("-" * 70)

all_objects = []
object_id = 0

for i, capture in enumerate(captures, 1):
    print(f"\n[{i}/{len(captures)}] Processing: {capture.name}")

    objects = extract_ui_objects(capture, capture.stem)
    print(f"  Found {len(objects)} potential UI objects")

    # Save each object
    for obj in objects:
        object_id += 1
        obj_filename = f"object_{object_id:04d}.png"
        obj_path = OBJECTS_DIR / obj_filename

        # Save image
        cv2.imwrite(str(obj_path), obj['image'])

        # Store metadata (without image data)
        all_objects.append({
            'id': object_id,
            'filename': obj_filename,
            'region': obj['region'],
            'position': obj['position'],
            'size': obj['size'],
            'screenshot': obj['screenshot'],
            'labeled': False,
            'category': None,
            'name': None,
        })

# Save metadata
metadata_file = OBJECTS_DIR / "objects_metadata.json"
with open(metadata_file, 'w') as f:
    json.dump(all_objects, f, indent=2)

# Summary
print()
print("=" * 70)
print("Extraction Complete!")
print("=" * 70)
print()
print(f"Extracted {len(all_objects)} UI objects")
print(f"Saved to: {OBJECTS_DIR}")
print(f"Metadata: {metadata_file}")
print()

# Group by region
from collections import Counter
region_counts = Counter(obj['region'] for obj in all_objects)
print("Objects by region:")
for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {region:20} {count:4} objects")
print()

print("Next step:")
print("  python 3_label_objects.py")
print()
