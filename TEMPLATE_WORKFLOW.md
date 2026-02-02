# Template Library Creation - Simple 3-Step Workflow

## Overview

Build your template library by capturing gameplay and labeling UI elements interactively.

## The Process

### Step 1: Capture Gameplay (10-second intervals)

```bash
python 1_capture_gameplay.py
```

**What it does:**
- Captures screenshots every 10 seconds while you play
- Saves to `data/gameplay_captures/`
- Press Ctrl+C to stop

**What you should do:**
- Play Heroes 3 normally
- Visit different screens: adventure map, town, combat, hero screen
- Let it capture for 2-5 minutes to get variety
- Focus on screens with important UI elements (End Turn button, resource bar, etc.)

### Step 2: Extract UI Objects

```bash
python 2_extract_objects.py
```

**What it does:**
- Analyzes all captured screenshots
- Extracts distinct UI elements from key regions:
  - Top-left: Minimap area
  - Top-right: Resources
  - Bottom-right: End Turn button area
  - Left panel: Control buttons
  - Right panel: Map controls
- Saves each object to `data/extracted_objects/`
- Creates metadata with position, size, region info

**Output:**
- Individual PNG files for each UI element
- `objects_metadata.json` with details

### Step 3: Label Objects Interactively

```bash
python 3_label_objects.py
```

**What it does:**
- Shows you each extracted object one by one
- Provides quick selection based on region
- Lets you label or skip
- Automatically copies labeled objects to template library

**How to use:**
1. For each object, you'll see:
   - Image filename (you can open it to view)
   - Region it was found in
   - Suggested labels with quick numbers [1-9]

2. Options:
   - **1-9**: Select from quick suggestions
   - **custom**: Type `category/name` manually
   - **skip**: Skip this object
   - **done**: Finish and save

**Example session:**
```
Object ID: 42
File: object_0042.png
Region: bottom_right
Position: (1450, 780)
Size: 85x42 px

Image location: data/extracted_objects/object_0042.png

Quick options:
  [1] adventure_map/end_turn_button
  [2] adventure_map/sleep_hero_button
  [3] adventure_map/next_hero_button
  [4] ui/map_controls

Label (1-9, custom, skip, done): 1

[OK] Labeled as: adventure_map/end_turn_button
Saved to: adventure_map/end_turn_button.png
```

## Template Library Structure

Templates are organized by category:

```
data/templates/
├── adventure_map/
│   ├── end_turn_button.png
│   ├── kingdom_overview_button.png
│   ├── hero_portrait.png
│   └── ...
├── resources/
│   ├── gold_icon.png
│   ├── wood_icon.png
│   └── ...
├── combat/
│   ├── attack_button.png
│   ├── defend_button.png
│   └── ...
├── town/
│   ├── town_hall_button.png
│   ├── recruit_button.png
│   └── ...
└── ui/
    ├── minimap.png
    ├── info_panel.png
    └── ...
```

## Categories

**adventure_map**: Adventure map specific UI
- end_turn_button, kingdom_overview_button, sleep_hero_button, etc.

**resources**: Resource bar icons
- gold_icon, wood_icon, ore_icon, mercury_icon, sulfur_icon, crystal_icon, gems_icon

**combat**: Combat screen UI
- attack_button, defend_button, wait_button, auto_button, etc.

**town**: Town screen UI
- town_hall_button, recruit_button, marketplace_button, etc.

**ui**: General UI elements
- minimap, info_panel, hero_portrait, etc.

## Tips

### Getting Good Templates

1. **Capture variety**: Play through different game phases
2. **Multiple resolutions**: Capture at your actual play resolution
3. **Clean screenshots**: Avoid capturing during animations
4. **Key moments**: Pause at important screens (adventure map with visible UI)

### Labeling Strategy

1. **Start with critical templates**:
   - end_turn_button (most important!)
   - Resource icons (gold, wood, ore, etc.)
   - Kingdom overview button

2. **Skip unclear objects**: If you can't identify it, skip it
3. **Consistent naming**: Use descriptive, lowercase names with underscores
4. **Check before overwriting**: Review existing templates before replacing

### Quick Workflow

**5-minute setup:**
```bash
# 1. Capture while playing (2-3 minutes)
python 1_capture_gameplay.py
# Play game, visit adventure map, town, combat
# Press Ctrl+C when done

# 2. Extract objects (30 seconds)
python 2_extract_objects.py

# 3. Label important ones (2-3 minutes)
python 3_label_objects.py
# Label 10-20 critical templates, skip the rest

# 4. Test
python demo_phase2.py
```

**Iterative approach:**
- Capture 10-20 screenshots
- Extract and label just the critical templates
- Test with demo
- Repeat to improve coverage

## Testing Your Templates

After labeling, test with:

```bash
python demo_phase2.py
```

This shows:
- Which templates are being matched
- Match confidence scores
- What's detected on screen

## Troubleshooting

**"No objects extracted"**
- Make sure captures show the game UI (not menus/loading screens)
- Check that `data/gameplay_captures/` has PNG files

**"Template not matching"**
- Template might be from wrong resolution
- Re-capture at your actual game resolution
- Make sure template shows the element clearly

**"Too many objects to label"**
- You don't need to label everything!
- Focus on critical templates first
- Skip objects you don't recognize
- You can always run labeling again later

## Progressive Enhancement

You don't need all templates at once:

**Minimum viable (5-10 templates):**
- end_turn_button
- 2-3 resource icons
- 1-2 map control buttons

**Good coverage (20-30 templates):**
- All resource icons
- Key adventure map buttons
- Hero and town indicators

**Complete (50+ templates):**
- All UI elements
- Combat buttons
- Town buildings
- Multiple variations

Build iteratively - start small, test, add more as needed!
