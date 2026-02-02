"""
UI Element Extraction Script

Analyzes screenshots and game assets to extract UI elements for template library.
Uses computer vision to detect buttons, icons, and UI components.
"""

import sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import json

# Add src to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

print("=" * 70)
print("HoMM3 UI Element Extraction")
print("=" * 70)
print()

PROJECT_ROOT = Path(__file__).parent
SCREENSHOTS_DIR = PROJECT_ROOT / "data" / "logs"
ASSETS_DIR = PROJECT_ROOT / "data" / "assets"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extracted_ui_elements"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Step 1: Load screenshots
print("Step 1: Loading screenshots...")
print("-" * 70)

screenshots = list(SCREENSHOTS_DIR.glob("*.png"))
print(f"Found {len(screenshots)} screenshots:")
for screenshot in screenshots:
    img = Image.open(screenshot)
    print(f"  - {screenshot.name:40} ({img.size[0]}x{img.size[1]})")
print()

# Step 2: Detect UI regions in screenshots
print("Step 2: Detecting UI regions...")
print("-" * 70)

def detect_ui_regions(image_path):
    """
    Detect rectangular UI elements in a screenshot.
    Uses edge detection and contour analysis.
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    ui_elements = []

    for contour in contours:
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)

        # Filter by size (UI elements are typically 20-200 pixels)
        if 20 <= w <= 200 and 20 <= h <= 200:
            # Calculate aspect ratio
            aspect_ratio = w / h

            # UI buttons/icons typically have aspect ratios between 0.5 and 3.0
            if 0.5 <= aspect_ratio <= 3.0:
                ui_elements.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'aspect_ratio': aspect_ratio,
                })

    return ui_elements

extracted_count = 0
all_extractions = {}

for screenshot in screenshots:
    print(f"\nAnalyzing: {screenshot.name}")

    ui_elements = detect_ui_regions(screenshot)
    print(f"  Detected {len(ui_elements)} potential UI elements")

    # Load image for cropping
    img = cv2.imread(str(screenshot))

    # Extract and save top 20 elements (by size)
    ui_elements.sort(key=lambda e: e['width'] * e['height'], reverse=True)

    screenshot_extractions = []

    for i, element in enumerate(ui_elements[:20], 1):
        # Crop element
        x, y, w, h = element['x'], element['y'], element['width'], element['height']

        # Add padding
        padding = 2
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img.shape[1] - x, w + 2*padding)
        h = min(img.shape[0] - y, h + 2*padding)

        cropped = img[y:y+h, x:x+w]

        # Save
        output_name = f"{screenshot.stem}_element_{i:02d}.png"
        output_path = OUTPUT_DIR / output_name

        cv2.imwrite(str(output_path), cropped)

        screenshot_extractions.append({
            'filename': output_name,
            'source': screenshot.name,
            'position': {'x': x, 'y': y},
            'size': {'width': w, 'height': h},
            'aspect_ratio': element['aspect_ratio'],
        })

        extracted_count += 1

    all_extractions[screenshot.name] = screenshot_extractions

    print(f"  Extracted top 20 elements to: {OUTPUT_DIR}")

print()
print(f"Total UI elements extracted: {extracted_count}")
print()

# Step 3: Analyze game assets
print("Step 3: Analyzing game assets...")
print("-" * 70)

def analyze_asset(asset_path):
    """
    Analyze a game asset to determine if it's a useful UI element.
    """
    img = cv2.imread(str(asset_path))
    if img is None:
        return None

    h, w = img.shape[:2]

    # Check if it's a reasonable size for a UI element
    if 10 <= w <= 300 and 10 <= h <= 300:
        # Check if it has transparency (alpha channel)
        has_alpha = False
        try:
            pil_img = Image.open(asset_path)
            has_alpha = pil_img.mode == 'RGBA'
        except:
            pass

        return {
            'path': asset_path,
            'size': (w, h),
            'has_alpha': has_alpha,
            'category': asset_path.parent.name,
        }

    return None

# Analyze all assets
print("Scanning assets...")
useful_assets = []

for asset_file in ASSETS_DIR.rglob("*.png"):
    analysis = analyze_asset(asset_file)
    if analysis:
        useful_assets.append(analysis)

print(f"Found {len(useful_assets)} potentially useful assets")

# Group by category
by_category = {}
for asset in useful_assets:
    cat = asset['category']
    if cat not in by_category:
        by_category[cat] = []
    by_category[cat].append(asset)

print("\nAssets by category:")
for cat, assets in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {cat:20} {len(assets):4} files")

print()

# Step 4: Save metadata
print("Step 4: Saving metadata...")
print("-" * 70)

metadata = {
    'extracted_ui_elements': all_extractions,
    'asset_categories': {cat: len(assets) for cat, assets in by_category.items()},
    'total_extracted': extracted_count,
    'total_assets': len(useful_assets),
}

metadata_path = OUTPUT_DIR / "extraction_metadata.json"
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Metadata saved to: {metadata_path}")
print()

# Summary
print("=" * 70)
print("Extraction Complete!")
print("=" * 70)
print()
print(f"Extracted {extracted_count} UI elements from screenshots")
print(f"Identified {len(useful_assets)} useful game assets")
print()
print("Output directory:", OUTPUT_DIR)
print()
print("Next steps:")
print("1. Review extracted elements in:", OUTPUT_DIR)
print("2. Run identification script to label elements")
print("3. Organize into template library")
print()
