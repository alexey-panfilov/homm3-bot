"""
Automatic UI Element Identification

Uses visual analysis and HoMM3 UI knowledge to automatically identify common elements.
User reviews and confirms auto-labels afterward.
"""

import sys
from pathlib import Path
import json
import numpy as np
import cv2
from PIL import Image

print("=" * 70)
print("HoMM3 Auto-Identification of UI Elements")
print("=" * 70)
print()

PROJECT_ROOT = Path(__file__).parent
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted_ui_elements"
METADATA_FILE = EXTRACTED_DIR / "extraction_metadata.json"
AUTO_LABELS_FILE = EXTRACTED_DIR / "auto_labels.json"

# Load metadata
with open(METADATA_FILE, 'r') as f:
    metadata = json.load(f)

print("Step 1: Analyzing extracted UI elements...")
print("-" * 70)

def analyze_element_visually(img_path):
    """
    Analyze visual characteristics of an element.
    """
    img = cv2.imread(str(img_path))
    if img is None:
        return {}

    # Convert to HSV for color analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Calculate color statistics
    mean_h = np.mean(hsv[:, :, 0])
    mean_s = np.mean(hsv[:, :, 1])
    mean_v = np.mean(hsv[:, :, 2])

    # Detect edges (for determining if it's a button)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size

    # Dominant colors
    dominant_colors = []
    if mean_h < 20 or mean_h > 160:  # Red range
        dominant_colors.append('red')
    elif 20 <= mean_h < 40:  # Orange/yellow
        dominant_colors.append('gold')
    elif 40 <= mean_h < 80:  # Green
        dominant_colors.append('green')
    elif 80 <= mean_h < 140:  # Blue/cyan
        dominant_colors.append('blue')
    elif 140 <= mean_h < 160:  # Purple
        dominant_colors.append('purple')

    return {
        'mean_brightness': float(mean_v),
        'mean_saturation': float(mean_s),
        'edge_density': float(edge_density),
        'dominant_colors': dominant_colors,
    }

def auto_identify_element(element_data, visual_features):
    """
    Automatically identify element based on multiple factors.
    """
    x = element_data['position']['x']
    y = element_data['position']['y']
    w = element_data['size']['width']
    h = element_data['size']['height']
    aspect = element_data['aspect_ratio']

    confidence = 0.0
    category = "unknown"
    name = "unknown_element"

    # Rule 1: Top-right corner resources (x > 1200, y < 100)
    if x > 1200 and y < 200:
        if 'gold' in visual_features.get('dominant_colors', []):
            category = "resources"
            name = "gold_icon"
            confidence = 0.8
        elif w < 50 and h < 50:
            category = "resources"
            name = f"resource_icon_{y//50}"
            confidence = 0.6

    # Rule 2: Bottom-right corner (End Turn area)
    elif x > 1200 and y > 600:
        if w > 50:
            category = "adventure_map"
            name = "end_turn_button"
            confidence = 0.7
        else:
            category = "adventure_map"
            name = f"map_control_button_{y//50}"
            confidence = 0.5

    # Rule 3: Top-left corner (< 200, < 300)
    elif x < 200 and y < 300:
        if w > 100 or h > 100:
            category = "ui"
            name = "minimap"
            confidence = 0.9
        elif w < 50 and h < 50:
            category = "adventure_map"
            name = f"left_panel_button_{y//50}"
            confidence = 0.6
        else:
            category = "ui"
            name = f"left_panel_element_{y//50}"
            confidence = 0.5

    # Rule 4: Center tall elements (likely heroes)
    elif 300 < x < 1000 and aspect < 0.7 and h > 100:
        category = "adventure_map"
        name = "hero_on_map"
        confidence = 0.7

    # Rule 5: Center square elements (likely towns)
    elif 300 < x < 1000 and 0.8 < aspect < 1.2 and 80 < w < 150:
        category = "adventure_map"
        name = "town_icon"
        confidence = 0.6

    # Rule 6: Wide elements (likely UI bars or text)
    elif aspect > 2.0:
        category = "ui"
        name = "horizontal_ui_element"
        confidence = 0.4

    # Rule 7: Small square elements
    elif w < 50 and h < 50 and 0.8 < aspect < 1.2:
        if 'gold' in visual_features.get('dominant_colors', []):
            category = "resources"
            name = "resource_icon"
            confidence = 0.5
        else:
            category = "ui"
            name = "small_icon"
            confidence = 0.4

    return {
        'category': category,
        'name': name,
        'confidence': confidence,
        'visual_features': visual_features,
    }

# Process all elements
auto_labels = {}
stats = {'high_confidence': 0, 'medium_confidence': 0, 'low_confidence': 0}

print("\nAnalyzing elements...")

for source_file, elements in metadata['extracted_ui_elements'].items():
    print(f"\n  Source: {source_file}")

    for element in elements:
        filename = element['filename']
        img_path = EXTRACTED_DIR / filename

        # Visual analysis
        visual_features = analyze_element_visually(img_path)

        # Auto-identify
        identification = auto_identify_element(element, visual_features)

        # Store
        auto_labels[filename] = {
            'category': identification['category'],
            'name': identification['name'],
            'confidence': identification['confidence'],
            'source': source_file,
            'position': element['position'],
            'size': element['size'],
            'aspect_ratio': element['aspect_ratio'],
            'visual_features': identification['visual_features'],
        }

        # Stats
        if identification['confidence'] > 0.7:
            stats['high_confidence'] += 1
            conf_label = "HIGH"
        elif identification['confidence'] > 0.4:
            stats['medium_confidence'] += 1
            conf_label = "MED"
        else:
            stats['low_confidence'] += 1
            conf_label = "LOW"

        print(f"    {filename:40} -> {identification['category']}/{identification['name']:25} [{conf_label}]")

# Save auto-labels
with open(AUTO_LABELS_FILE, 'w') as f:
    json.dump(auto_labels, f, indent=2)

print()
print("=" * 70)
print("Auto-Identification Complete!")
print("=" * 70)
print()
print(f"Total elements analyzed: {len(auto_labels)}")
print(f"  High confidence (> 70%): {stats['high_confidence']}")
print(f"  Medium confidence (40-70%): {stats['medium_confidence']}")
print(f"  Low confidence (< 40%): {stats['low_confidence']}")
print()
print(f"Auto-labels saved to: {AUTO_LABELS_FILE}")
print()
print("Next steps:")
print("1. Review auto-labels file to check accuracy")
print("2. Run organize_templates.py to copy elements to template library")
print("3. Or run identify_ui_elements.py for manual correction")
print()
