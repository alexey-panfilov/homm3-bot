"""
Step 1: Auto-Capture Gameplay Screenshots

Captures game screenshots every 10 seconds while HoMM3 is running.
Press Ctrl+C to stop.

Usage:
    python 1_capture_gameplay.py
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from PIL import Image

# Add src to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from capture.window import WindowManager
from capture.screen import ScreenCapture

print("=" * 70)
print("HoMM3 Gameplay Auto-Capture")
print("=" * 70)
print()

# Setup output directory
output_dir = Path(__file__).parent / "data" / "gameplay_captures"
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Output directory: {output_dir}")
print()
print("Instructions:")
print("1. Make sure Heroes of Might and Magic 3 is running")
print("2. Play the game normally - navigate different screens")
print("3. Screenshots will be captured every 10 seconds")
print("4. Press Ctrl+C to stop capturing")
print()

# Find game window
print("Looking for game window...")
window_mgr = WindowManager()
if not window_mgr.find_game_window():
    print("[X] Game window not found!")
    print("    Please start Heroes of Might and Magic 3 first.")
    sys.exit(1)

print(f"[OK] Found: {window_mgr.window_title}")
bounds = window_mgr.get_window_bounds()
print(f"     Resolution: {bounds[2]}x{bounds[3]}")
print()

# Setup screen capture
screen_capture = ScreenCapture()
screen_capture.set_capture_region(bounds[0], bounds[1], bounds[2], bounds[3])

print("=" * 70)
print("Starting capture... (Ctrl+C to stop)")
print("=" * 70)
print()

capture_count = 0
try:
    while True:
        # Capture screenshot
        screenshot = screen_capture.capture()

        if screenshot is not None:
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.png"
            filepath = output_dir / filename

            Image.fromarray(screenshot).save(filepath)
            capture_count += 1

            print(f"[{capture_count:3d}] Captured: {filename} ({screenshot.shape[1]}x{screenshot.shape[0]})")
        else:
            print(f"[!] Failed to capture screenshot")

        # Wait 10 seconds
        time.sleep(10)

except KeyboardInterrupt:
    print()
    print()
    print("=" * 70)
    print("Capture stopped by user")
    print("=" * 70)
    print()
    print(f"Total captures: {capture_count}")
    print(f"Saved to: {output_dir}")
    print()
    print("Next step:")
    print("  python 2_extract_objects.py")
    print()
