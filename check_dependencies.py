"""
Check if all dependencies are properly installed.
Run this script to verify your installation.
"""

import sys
from pathlib import Path

print("=" * 60)
print("HoMM3 Bot - Dependency Checker")
print("=" * 60)
print()

# Check Python version
print(f"✓ Python version: {sys.version.split()[0]}")
if sys.version_info < (3, 10):
    print("  ⚠ WARNING: Python 3.10+ recommended")
print()

# List of required packages
required_packages = [
    ('numpy', 'numpy'),
    ('PIL', 'pillow'),
    ('mss', 'mss'),
    ('win32gui', 'pywin32'),
    ('cv2', 'opencv-python'),
    ('pytesseract', 'pytesseract'),
    ('pyautogui', 'pyautogui'),
    ('pynput', 'pynput'),
    ('torch', 'torch'),
    ('yaml', 'pyyaml'),
    ('structlog', 'structlog'),
    ('colorama', 'colorama'),
    ('psutil', 'psutil'),
]

missing_packages = []
installed_packages = []

print("Checking required packages:")
print("-" * 60)

for import_name, package_name in required_packages:
    try:
        __import__(import_name)
        print(f"✓ {package_name}")
        installed_packages.append(package_name)
    except ImportError:
        print(f"✗ {package_name} - NOT FOUND")
        missing_packages.append(package_name)

print()
print("-" * 60)
print(f"Installed: {len(installed_packages)}/{len(required_packages)}")

if missing_packages:
    print()
    print("⚠ Missing packages:")
    for pkg in missing_packages:
        print(f"  - {pkg}")
    print()
    print("To install missing packages:")
    print(f"  pip install {' '.join(missing_packages)}")
    sys.exit(1)
else:
    print()
    print("✓ All required packages are installed!")

# Check Tesseract
print()
print("Checking Tesseract OCR:")
print("-" * 60)
try:
    import pytesseract
    version = pytesseract.get_tesseract_version()
    print(f"✓ Tesseract version: {version}")
except Exception as e:
    print(f"✗ Tesseract not properly configured")
    print(f"  Error: {e}")
    print()
    print("  Please install Tesseract OCR:")
    print("  https://github.com/UB-Mannheim/tesseract/wiki")

# Check project structure
print()
print("Checking project structure:")
print("-" * 60)

required_dirs = [
    'src',
    'src/capture',
    'src/actions',
    'config',
    'data/logs',
]

project_root = Path(__file__).parent

for dir_path in required_dirs:
    full_path = project_root / dir_path
    if full_path.exists():
        print(f"✓ {dir_path}/")
    else:
        print(f"✗ {dir_path}/ - NOT FOUND")

# Check config file
config_file = project_root / 'config' / 'default.yaml'
if config_file.exists():
    print(f"✓ config/default.yaml")
else:
    print(f"✗ config/default.yaml - NOT FOUND")

print()
print("=" * 60)
print("Dependency check complete!")
print("=" * 60)
