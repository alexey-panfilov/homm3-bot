# Phase 2 Setup Guide

Complete guide to setting up Phase 2 vision system for HoMM3 Bot.

## Overview

Phase 2 adds game state parsing capabilities:
- Screen detection
- Resource bar reading (OCR)
- Hero and town detection (template matching)
- Turn detection

## Prerequisites

Before Phase 2 will work fully, you need:

### 1. Tesseract OCR (Optional but Recommended)

**What it does:** Reads text and numbers from the game (resource counts)

**Install on Windows:**
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (use default location: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or bot will auto-detect

**Verify installation:**
```bash
tesseract --version
```

### 2. Template Library (Required for full functionality)

**What it does:** Recognizes UI elements (buttons, heroes, towns)

**Quick Setup:**
```bash
python prepare_templates.py
```

## Setup Steps

### Step 1: Run Simple Demo (No Setup Required)

Test that infrastructure works:

```bash
# Make sure HoMM3 is running
python demo_phase2_simple.py
```

**What it tests:**
- Window detection
- Screenshot capture
- Basic image analysis
- Parser initialization

**Expected output:**
```
[OK] Found: Heroes of Might & Magic III - HD Edition
[OK] Screenshot captured
[OK] Vision infrastructure initialized
```

### Step 2: Install Tesseract OCR (Optional)

For resource number extraction:

1. Download and install Tesseract
2. Rerun demo - you should see resource counts (may be 0 if not on adventure map)

### Step 3: Create Template Library

Templates are small images of UI elements the bot uses for detection.

**RECOMMENDED: Use the 3-step automated workflow**

See [TEMPLATE_WORKFLOW.md](../TEMPLATE_WORKFLOW.md) for the simple approach:
1. `python 1_capture_gameplay.py` - Auto-capture screenshots every 10 seconds
2. `python 2_extract_objects.py` - Extract UI elements from captures
3. `python 3_label_objects.py` - Interactive labeling with quick options

**Option A: Manual Creation**

1. **Take screenshots** while playing HoMM3:
   ```
   - Adventure map with UI visible
   - Heroes (selected and unselected)
   - Towns of different factions
   - Combat screen
   ```

2. **Crop UI elements** using any image editor:

   Example templates needed:
   - `end_turn_button.png` - The End Turn button (~100x30px)
   - `hero_marker.png` - Hero indicator on map (~48x48px)
   - `town_castle.png` - Castle town icon (~48x48px)
   - `resource_gold_icon.png` - Gold coin icon (~24x24px)

3. **Save to templates directory:**
   ```
   data/templates/
     adventure_map/
       end_turn_button.png
       hero_marker.png
       kingdom_button.png
     town/
       castle_icon.png
       rampart_icon.png
     combat/
       attack_button.png
       defend_button.png
     resources/
       gold_icon.png
       wood_icon.png
   ```

**Option B: Use Extracted Assets**

We already extracted 300 game assets. Browse and copy useful ones:

```bash
# Run the preparation script
python prepare_templates.py

# Choose option 2 to browse assets
# Source: data/assets/
# Target: data/templates/
```

Look for:
- Button graphics in `data/assets/ui/`
- Icons in `data/assets/cursors/`
- Artifact icons in `data/assets/artifacts/`

**Option C: Auto-organize (Experimental)**

```bash
python prepare_templates.py
# Choose option 3
```

### Step 4: Run Full Demo

With templates in place:

```bash
# Make sure HoMM3 is on adventure map
python demo_phase2.py
```

**What it tests:**
- Screen type detection
- Resource bar parsing
- Hero/town detection
- Turn state detection

## File Structure

```
homm3-bot/
├── data/
│   ├── assets/           # Extracted game graphics (300 files)
│   ├── templates/        # Templates for detection (you create these)
│   │   ├── adventure_map/
│   │   ├── town/
│   │   ├── combat/
│   │   └── resources/
│   └── logs/             # Screenshots and debug output
├── demo_phase2_simple.py # Works without templates
├── demo_phase2.py        # Full demo (needs templates)
└── prepare_templates.py  # Helper for template setup
```

## Troubleshooting

### "Tesseract not installed"

**Problem:** Resource parsing shows all zeros

**Solution:**
1. Install Tesseract OCR (see above)
2. Or ignore - templates can work without OCR

### "Template not found" warnings

**Problem:** Many warnings about missing templates

**Solution:**
1. Run `demo_phase2_simple.py` instead (works without templates)
2. Or create templates (see Step 3 above)

### "Low confidence" detections

**Problem:** Parsers detect things but with low confidence

**Causes:**
- Wrong resolution (templates from different resolution)
- Wrong screen (not on adventure map)
- Templates need better cropping

**Solution:**
- Make sure you're on the adventure map
- Adjust template coordinates in parsers
- Create higher quality templates

### "Screen detection: UNKNOWN"

**Problem:** Can't identify current screen

**Solution:**
- Add more templates for each screen type
- Check that templates match your game version (HD Edition vs original)

## What Each Parser Does

### Screen Detector
- **Purpose:** Identifies which screen you're on
- **Needs:** Templates for unique UI elements per screen
- **Example:** Finds "End Turn" button → Adventure Map

### Resource Parser
- **Purpose:** Reads resource counts from top bar
- **Needs:** Tesseract OCR
- **Example:** Extracts gold: 15000, wood: 20, etc.

### Adventure Map Parser
- **Purpose:** Finds heroes and towns on map
- **Needs:** Hero/town icon templates
- **Example:** Detects hero at position (640, 480)

### Turn Detector
- **Purpose:** Knows when it's player's turn
- **Needs:** End Turn button templates
- **Example:** Button active = player turn, grayed = AI turn

## Next Steps

Once Phase 2 is set up:

1. **Test with real gameplay**
   - Run demo while playing
   - Verify detections are accurate
   - Adjust thresholds if needed

2. **Calibrate for your setup**
   - Different resolutions may need coordinate adjustments
   - HD Edition vs original may need different templates

3. **Move to Phase 3**
   - Rule-based AI (decision making)
   - Automate simple actions (end turn, visit buildings)
   - Strategic planning (resource management, hero movement)

## Quick Reference

```bash
# No setup required - test infrastructure
python demo_phase2_simple.py

# Setup templates interactively
python prepare_templates.py

# Full demo with all features
python demo_phase2.py

# Extract more game assets
python extract_game_assets.py
```

## Tips

- **Start simple:** Use `demo_phase2_simple.py` first
- **Quality over quantity:** 5-10 good templates better than 100 poor ones
- **Test incrementally:** Add templates one at a time, test each
- **Use actual screenshots:** Templates from your game work best
- **Transparent PNGs:** Better for template matching

## Support

If you get stuck:
1. Check the demo output - it explains what's missing
2. Look at example templates in `data/assets/`
3. Run `troubleshoot_window.py` for window detection issues
4. Check logs in `data/logs/`
