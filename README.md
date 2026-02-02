# HoMM3 Bot - Autonomous Gaming Bot for Heroes of Might and Magic 3

An intelligent gaming bot that uses computer vision and machine learning to play Heroes of Might and Magic 3 autonomously.

## Features

- **Computer Vision**: Observes the game screen using OpenCV and template matching
- **Mouse/Keyboard Control**: Safely controls mouse and keyboard with bounds checking
- **Machine Learning**: PyTorch-based decision making (planned)
- **GUI Dashboard**: Real-time monitoring and control interface (planned)
- **Multi-mode Support**: Single-player and hot-seat multiplayer
- **Configurable**: Extensive configuration options via YAML

## Current Status

**Phase 1: Foundation** (In Progress)
- ✅ Project structure and setup
- ✅ Screen capture module
- ✅ Window detection and management
- ✅ Mouse/keyboard control with safety features
- ✅ Configuration system
- ✅ Logging infrastructure
- ✅ Basic unit tests

## Installation

### Prerequisites

1. **Python 3.10+**: Download from [python.org](https://www.python.org/)
2. **Tesseract OCR**: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install and add to PATH
   - Default location: `C:\Program Files\Tesseract-OCR`

### Setup

```bash
# Clone or extract the project
cd homm3-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python check_dependencies.py
```

## Usage

### Demo Mode

Test the bot components with a demo:

**Option 1 - Easy (Windows):**
```bash
run_demo.bat
```

**Option 2 - Using launcher script:**
```bash
python run.py --demo
```

**Option 3 - Direct:**
```bash
python src/main.py --demo
```

This will:
- Find the HoMM3 game window
- Capture a screenshot
- Test mouse movement
- Save screenshot to `data/logs/demo_screenshot.png`

### Configuration

Edit `config/default.yaml` to customize bot behavior:

```yaml
capture:
  fps: 2.0                    # Screen capture rate

mouse:
  default_duration: 0.2       # Mouse movement speed
  enable_verification: true   # Verify mouse actions

ai:
  strategy_profile: balanced  # Strategy: balanced, aggressive, defensive, economic
  enable_ml: false            # Use ML models (not yet implemented)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_config.py
```

## Project Structure

```
homm3-bot/
├── src/                      # Source code
│   ├── capture/              # Screen capture and window management
│   ├── vision/               # Computer vision (planned)
│   ├── state/                # Game state management (planned)
│   ├── ai/                   # AI decision making (planned)
│   ├── ml/                   # Machine learning (planned)
│   ├── actions/              # Mouse/keyboard control
│   ├── gui/                  # GUI dashboard (planned)
│   ├── config.py             # Configuration management
│   ├── utils.py              # Utilities and logging
│   └── main.py               # Entry point
├── config/                   # Configuration files
├── tests/                    # Unit and integration tests
├── data/                     # Training data, models, logs
└── docs/                     # Documentation
```

## Development Roadmap

See [HOMM3_Bot_PRD.md](HOMM3_Bot_PRD.md) for the complete Product Requirements Document.

### Upcoming Phases

- **Phase 2**: Game state parsing (adventure map, combat, towns)
- **Phase 3**: Rule-based AI (basic gameplay)
- **Phase 4**: Machine learning integration
- **Phase 5**: GUI dashboard
- **Phase 6**: Testing and polish

## Requirements

### System
- Windows 10/11
- 4GB+ RAM
- Heroes of Might and Magic 3 (Steam/GOG)

### Python Dependencies
- numpy, pillow
- mss, pywin32
- opencv-python, pytesseract
- pyautogui, pynput
- PyTorch (for ML features)
- PyQt6 (for GUI)
- pyyaml, structlog

## Safety Features

- **Mouse Bounds Checking**: Restricts mouse to game window
- **Action Verification**: Verifies actions succeeded
- **Emergency Stop**: Hotkey to immediately stop all actions
- **Rate Limiting**: Prevents excessive action spam

## Contributing

This is currently a single-developer project. Contributions, suggestions, and bug reports are welcome!

## License

This project is for educational and personal use only. Heroes of Might and Magic 3 is owned by Ubisoft.

## Disclaimer

This bot is designed for single-player use and learning purposes. Use responsibly and in accordance with game terms of service.
