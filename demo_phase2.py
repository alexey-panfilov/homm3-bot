"""
Phase 2 Demo - Game State Parsing

Demonstrates the new vision capabilities:
- Screen detection
- Resource bar parsing
- Adventure map parsing
- Turn detection
- Template matching

Run this with HoMM3 open on the adventure map.
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from capture.window import WindowManager
from capture.screen import ScreenCapture
from vision import (
    TemplateMatcher,
    ScreenDetector,
    ResourceParser,
    AdventureMapParser,
    TurnDetector,
    GameScreen,
)
from utils import setup_logging
import structlog

# Setup logging
setup_logging(log_level='INFO')
logger = structlog.get_logger(__name__)

print("=" * 70)
print("HoMM3 Bot - Phase 2 Demo")
print("Game State Parsing & Vision System")
print("=" * 70)
print()

# Step 1: Find game window
print("Step 1: Finding game window...")
print("-" * 70)

window_mgr = WindowManager()
if not window_mgr.find_game_window():
    print("[X] Game window not found!")
    print("\nMake sure Heroes of Might and Magic 3 is running.")
    print("Run troubleshoot_window.py for help.")
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

# Save for reference
output_dir = Path(__file__).parent / 'data' / 'logs'
output_dir.mkdir(parents=True, exist_ok=True)
screenshot_path = output_dir / 'phase2_demo_screenshot.png'

from PIL import Image
Image.fromarray(screenshot).save(screenshot_path)
print(f"     Saved to: {screenshot_path}")
print()

# Step 3: Initialize vision system
print("Step 3: Initializing vision system...")
print("-" * 70)

# Template matcher (no templates loaded yet, but structure is ready)
template_matcher = TemplateMatcher(
    template_dir=Path(__file__).parent / 'data' / 'templates',
    threshold=0.75,
)
print("[OK] Template matcher initialized")

# Screen detector
screen_detector = ScreenDetector(template_matcher)
print("[OK] Screen detector initialized")

# Resource parser
resource_parser = ResourceParser(template_matcher)
print("[OK] Resource parser initialized")

# Adventure map parser
adventure_parser = AdventureMapParser(template_matcher)
print("[OK] Adventure map parser initialized")

# Turn detector
turn_detector = TurnDetector(template_matcher)
print("[OK] Turn detector initialized")
print()

# Step 4: Detect current screen
print("Step 4: Detecting current screen...")
print("-" * 70)

current_screen, screen_confidence = screen_detector.detect_screen(screenshot)
print(f"Detected Screen: {current_screen.name}")
print(f"Confidence: {screen_confidence:.2f}")

if current_screen == GameScreen.UNKNOWN:
    print("\n[!] Screen type unknown - template library not yet populated")
    print("    This is expected for Phase 2 initial demo")
    print("    Screen detection will improve as we add template images")
print()

# Step 5: Parse resources
print("Step 5: Parsing resource bar...")
print("-" * 70)

resource_confidence = resource_parser.can_parse(screenshot)
print(f"Resource bar detection confidence: {resource_confidence:.2f}")

if resource_confidence > 0.5:
    resource_state = resource_parser.parse(screenshot)
    print(f"\nResources extracted:")
    print(f"  Gold:    {resource_state.gold}")
    print(f"  Wood:    {resource_state.wood}")
    print(f"  Ore:     {resource_state.ore}")
    print(f"  Mercury: {resource_state.mercury}")
    print(f"  Sulfur:  {resource_state.sulfur}")
    print(f"  Crystal: {resource_state.crystal}")
    print(f"  Gems:    {resource_state.gems}")
    print(f"\nConfidence: {resource_state.confidence:.2f}")
else:
    print("[!] Resource bar not detected")
    print("    This is expected - OCR needs to be calibrated")
    print("    Resource positions may need adjustment for your resolution")
print()

# Step 6: Parse adventure map
print("Step 6: Parsing adventure map...")
print("-" * 70)

map_confidence = adventure_parser.can_parse(screenshot)
print(f"Adventure map detection confidence: {map_confidence:.2f}")

if map_confidence > 0.5:
    map_state = adventure_parser.parse(screenshot)
    print(f"\nMap objects found:")
    print(f"  Heroes: {len(map_state.heroes)}")
    print(f"  Towns:  {len(map_state.towns)}")

    if map_state.selected_hero:
        print(f"  Selected hero at: {map_state.selected_hero.position}")

    print(f"\nConfidence: {map_state.confidence:.2f}")
else:
    print("[!] Adventure map parsing incomplete")
    print("    Templates for heroes and towns need to be added")
print()

# Step 7: Detect turn state
print("Step 7: Detecting turn state...")
print("-" * 70)

turn_info = turn_detector.is_player_turn(screenshot, current_screen)
print(f"Is player turn: {turn_info.is_player_turn}")
print(f"Confidence: {turn_info.confidence:.2f}")

if turn_info.confidence < 0.7:
    print("\n[!] Turn detection uncertain")
    print("    UI element templates needed for accurate detection")
print()

# Step 8: Summary
print("=" * 70)
print("Phase 2 Demo Complete!")
print("=" * 70)
print()
print("Summary:")
print("-" * 70)
print(f"  Screen Detection:     {'✓' if screen_confidence > 0.5 else '○'}")
print(f"  Resource Parsing:     {'✓' if resource_confidence > 0.5 else '○'}")
print(f"  Adventure Map Parse:  {'✓' if map_confidence > 0.5 else '○'}")
print(f"  Turn Detection:       {'✓' if turn_info.confidence > 0.7 else '○'}")
print()

print("Phase 2 Status:")
print("-" * 70)
print("[✓] Vision infrastructure complete")
print("[✓] Parser framework implemented")
print("[✓] OCR engine ready")
print("[○] Template library needs population")
print("[○] UI element detection needs calibration")
print()

print("Next Steps:")
print("-" * 70)
print("1. Populate template library with UI elements")
print("   - Extract buttons, icons, indicators from game assets")
print("   - Take reference screenshots of different game states")
print()
print("2. Calibrate OCR for resource numbers")
print("   - Adjust preprocessing for better digit recognition")
print("   - Fine-tune region coordinates for your resolution")
print()
print("3. Test with various game scenarios")
print("   - Different screen types (town, combat, etc.)")
print("   - Different map sizes and zoom levels")
print("   - Different hero and town counts")
print()
print("=" * 70)
print()
print(f"Screenshot saved: {screenshot_path}")
print("Review the logs for detailed analysis.")
print()
