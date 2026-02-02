"""
Phase 2 Demo - Simplified (No Templates Required)

Tests vision system capabilities without needing template library.
This demonstrates the infrastructure is working.

Run this with HoMM3 open on the adventure map.
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from capture.window import WindowManager
from capture.screen import ScreenCapture
from vision import ResourceParser, AdventureMapParser
from utils import setup_logging

# Setup logging (set to WARNING to reduce noise)
setup_logging(log_level='WARNING')

print("=" * 70)
print("HoMM3 Bot - Phase 2 Simple Demo")
print("Game State Parsing (No Templates Required)")
print("=" * 70)
print()

# Step 1: Find game window
print("Step 1: Finding game window...")
print("-" * 70)

window_mgr = WindowManager()
if not window_mgr.find_game_window():
    print("[X] Game window not found!")
    print("\nMake sure Heroes of Might and Magic 3 is running.")
    sys.exit(1)

print(f"[OK] Found: {window_mgr.window_title}")
bounds = window_mgr.get_window_bounds()
print(f"     Resolution: {bounds[2]}x{bounds[3]}")
print()

# Step 2: Capture screenshot
print("Step 2: Capturing screenshot...")
print("-" * 70)

screen_capture = ScreenCapture()
screen_capture.set_capture_region(bounds[0], bounds[1], bounds[2], bounds[3])
screenshot = screen_capture.capture()

if screenshot is None:
    print("[X] Failed to capture screenshot!")
    sys.exit(1)

print(f"[OK] Screenshot captured: {screenshot.shape}")

# Save screenshot
output_dir = Path(__file__).parent / 'data' / 'logs'
output_dir.mkdir(parents=True, exist_ok=True)
screenshot_path = output_dir / 'phase2_simple_demo.png'

from PIL import Image
Image.fromarray(screenshot).save(screenshot_path)
print(f"     Saved to: {screenshot_path}")
print()

# Step 3: Test Resource Parser (OCR-based)
print("Step 3: Testing Resource Parser...")
print("-" * 70)

# Initialize without template matcher (pure OCR mode)
resource_parser = ResourceParser(template_matcher=None)
print("[OK] Resource parser initialized (OCR mode)")

try:
    resource_state = resource_parser.parse(screenshot)
    print(f"\nExtracted Resources:")
    print(f"  Gold:    {resource_state.gold:>6}")
    print(f"  Wood:    {resource_state.wood:>6}")
    print(f"  Ore:     {resource_state.ore:>6}")
    print(f"  Mercury: {resource_state.mercury:>6}")
    print(f"  Sulfur:  {resource_state.sulfur:>6}")
    print(f"  Crystal: {resource_state.crystal:>6}")
    print(f"  Gems:    {resource_state.gems:>6}")
    print(f"\nParser Confidence: {resource_state.confidence:.2f}")

    if resource_state.confidence < 0.3:
        print("\n[!] Low confidence - OCR may need calibration")
        print("    Reasons:")
        print("    - Tesseract not installed or not in PATH")
        print("    - Resource bar coordinates need adjustment for your resolution")
        print("    - Screenshot doesn't show adventure map")
except Exception as e:
    print(f"\n[!] Resource parsing failed: {e}")
    print("    This is expected if Tesseract OCR is not installed")
    print("    Install from: https://github.com/UB-Mannheim/tesseract/wiki")

print()

# Step 4: Test Adventure Map Parser (basic heuristics)
print("Step 4: Testing Adventure Map Parser...")
print("-" * 70)

adventure_parser = AdventureMapParser(template_matcher=None)
print("[OK] Adventure map parser initialized (heuristic mode)")

try:
    # Check if this looks like adventure map
    confidence = adventure_parser.can_parse(screenshot)
    print(f"\nAdventure Map Detection: {confidence:.2f}")

    if confidence > 0.5:
        print("[OK] This appears to be the adventure map")
    else:
        print("[!] May not be adventure map, or detection needs calibration")

    # Note about template matching
    print("\n[Note] Hero/Town detection requires template library")
    print("       Run 'python prepare_templates.py' to set up templates")
except Exception as e:
    print(f"\n[!] Map parsing failed: {e}")

print()

# Step 5: Image Analysis
print("Step 5: Basic Image Analysis...")
print("-" * 70)

import numpy as np
import cv2

# Convert to HSV for color analysis
hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)

# Calculate some basic statistics
mean_brightness = np.mean(screenshot)
color_variance = np.std(screenshot)

print(f"Mean Brightness: {mean_brightness:.1f}")
print(f"Color Variance:  {color_variance:.1f}")

# Detect dominant colors
hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
dominant_hue = np.argmax(hist_h)
print(f"Dominant Hue:    {dominant_hue} (0=red, 60=green, 120=blue)")

# Heuristic screen detection
if mean_brightness < 80:
    detected_screen = "MAIN_MENU (dark background)"
elif 35 < dominant_hue < 85:
    detected_screen = "ADVENTURE_MAP (green terrain)"
elif mean_brightness > 120:
    detected_screen = "TOWN or BRIGHT_SCREEN"
else:
    detected_screen = "UNKNOWN"

print(f"\nHeuristic Detection: {detected_screen}")
print()

# Summary
print("=" * 70)
print("Demo Complete!")
print("=" * 70)
print()
print("What Worked:")
print("-" * 70)
print("[OK] Window detection")
print("[OK] Screenshot capture")
print("[OK] Basic image analysis")
print("[OK] Vision infrastructure initialized")
print()

print("What Needs Setup:")
print("-" * 70)
print("[ ] Tesseract OCR for resource parsing")
print("[ ] Template library for UI element detection")
print("[ ] Resolution-specific calibration")
print()

print("Next Steps:")
print("-" * 70)
print("1. Install Tesseract OCR (if not already):")
print("   https://github.com/UB-Mannheim/tesseract/wiki")
print()
print("2. Prepare template library:")
print("   python prepare_templates.py")
print()
print("3. Run full demo with templates:")
print("   python demo_phase2.py")
print()
print(f"Screenshot saved: {screenshot_path}")
print()
