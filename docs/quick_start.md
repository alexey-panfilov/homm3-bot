# Quick Start Guide

This guide will help you get the HoMM3 Bot up and running quickly.

## Prerequisites

### 1. Install Python 3.10+

Download and install from [python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version
```

### 2. Install Tesseract OCR

1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (choose default installation path)
3. Add Tesseract to your PATH:
   - Default path: `C:\Program Files\Tesseract-OCR`
   - Or set environment variable: `TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata`

Verify installation:
```bash
tesseract --version
```

### 3. Have HoMM3 Installed

- Steam version (HD Edition) or GOG version (Complete)
- Make sure you can launch and run the game

## Installation Steps

### 1. Extract/Clone the Project

```bash
cd C:\Users\YourName\
# Extract the homm3-bot folder here
```

### 2. Create Virtual Environment

```bash
cd homm3-bot
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will take a few minutes. PyTorch is a large package.

### 5. Verify Installation

```bash
python check_dependencies.py
```

This will check that all required packages are installed correctly.

## First Run - Demo Mode

### 1. Launch HoMM3

- Start Heroes of Might and Magic 3 from Steam/GOG
- Let it open in a window (not fullscreen for easier testing)
- Leave it on the main menu or start a game

### 2. Run the Bot Demo

**Easy Method (Windows) - Double-click:**
- Simply double-click `run_demo.bat`

**Command Line - Option 1 (Recommended):**
```bash
python run.py --demo
```

**Command Line - Option 2:**
```bash
python src/main.py --demo
```

### What the Demo Does:

1. **Finds the game window** - Looks for the HoMM3 window
2. **Captures a screenshot** - Saves to `data/logs/demo_screenshot.png`
3. **Moves the mouse** - Moves cursor to center of game window
4. **Displays info** - Shows window information and statistics

### Expected Output:

```
2024-02-01 12:00:00 [INFO] HoMM3Bot - Starting
2024-02-01 12:00:00 [INFO] Found game window: 'Heroes III' (handle: 12345)
2024-02-01 12:00:00 [INFO] Game window found: 1920x1080 at (0, 0)
2024-02-01 12:00:00 [INFO] Bot setup complete
2024-02-01 12:00:00 [INFO] Running demo mode...
2024-02-01 12:00:00 [INFO] Screenshot captured: (1080, 1920, 3)
2024-02-01 12:00:00 [INFO] Demo screenshot saved to: data/logs/demo_screenshot.png
2024-02-01 12:00:00 [INFO] Moving mouse to window center: (960, 540)
2024-02-01 12:00:00 [INFO] Demo complete
```

## Troubleshooting

### Issue: "Could not find game window"

**Solutions:**
1. Make sure HoMM3 is running
2. Check the window title matches expected values
3. Try specifying custom window title in config:
   ```yaml
   window:
     window_title: "Your Exact Window Title"
   ```

### Issue: "ModuleNotFoundError"

**Solution:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Issue: "pytesseract.TesseractNotFoundError"

**Solution:**
- Install Tesseract OCR (see prerequisites)
- Add to PATH or set environment variable

### Issue: Mouse doesn't move

**Solution:**
- The demo only moves the mouse, doesn't click
- Make sure the game window is visible (not minimized)
- Check mouse safety bounds in logs

## Configuration

### Basic Configuration

Edit `config/default.yaml`:

```yaml
# How fast to capture screenshots (higher = more responsive)
capture:
  fps: 2.0

# Mouse movement speed (lower = slower, more human-like)
mouse:
  default_duration: 0.3

# Logging detail level
logging:
  level: DEBUG  # Change to DEBUG for more details
```

### Creating Custom Config

1. Copy `config/default.yaml` to `config/my_config.yaml`
2. Make your changes
3. Run with: `python src/main.py --config config/my_config.yaml --demo`

## Next Steps

Once the demo works successfully:

1. **Review the PRD**: Read `HOMM3_Bot_PRD.md` to understand the full project plan
2. **Check the logs**: Look at log files in `data/logs/` for detailed information
3. **Run tests**: Execute `pytest` to verify all components work
4. **Explore the code**: Browse `src/` to understand the architecture
5. **Wait for Phase 2**: Game state parsing is coming next!

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src tests/

# Run specific test
pytest tests/unit/test_config.py -v
```

## Development Commands

```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/
```

## Getting Help

If you encounter issues:

1. Check the logs in `data/logs/`
2. Enable DEBUG logging: `--log-level DEBUG`
3. Review error messages carefully
4. Check that all prerequisites are installed

## What's Working (Phase 1)

✅ Screen capture from game window
✅ Window detection and management
✅ Mouse control with safety bounds
✅ Keyboard input simulation
✅ Configuration system
✅ Logging and error handling
✅ Basic test suite

## What's Coming Next (Phase 2)

⏳ Adventure map parsing
⏳ Combat screen detection
⏳ Town screen parsing
⏳ Resource reading (OCR)
⏳ Hero detection and tracking
⏳ Turn detection system

---

**Congratulations!** If the demo worked, you've successfully set up the HoMM3 Bot foundation. The bot can now see the game and control the mouse. Next phases will add game understanding and decision-making capabilities.
