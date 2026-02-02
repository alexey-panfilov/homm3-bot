"""
Launcher script for HoMM3 Bot.
Run this from the project root directory.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

# Import and run main
from main import main

if __name__ == '__main__':
    sys.exit(main())
