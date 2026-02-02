"""
Setup script for HoMM3 Bot.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="homm3-bot",
    version="0.1.0",
    author="Your Name",
    description="Autonomous gaming bot for Heroes of Might and Magic 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/homm3-bot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "pillow>=10.0.0",
        "mss>=9.0.0",
        "pywin32>=306",
        "opencv-python>=4.8.0",
        "pytesseract>=0.3.10",
        "pyautogui>=0.9.54",
        "pynput>=1.7.6",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "PyQt6>=6.5.0",
        "pyqtgraph>=0.13.0",
        "pyyaml>=6.0",
        "structlog>=23.1.0",
        "colorama>=0.4.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "homm3-bot=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
    ],
)
