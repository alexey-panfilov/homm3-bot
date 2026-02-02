"""
Find HoMM3 installation path from running process.
"""
import psutil
import win32process
import win32gui
from pathlib import Path

print("=" * 70)
print("Finding HoMM3 Installation Path")
print("=" * 70)
print()

# Method 1: Find from running process
print("Method 1: Checking running processes...")
print("-" * 70)

found_paths = []

for proc in psutil.process_iter(['name', 'exe']):
    try:
        name = proc.info['name']
        if name and ('homm' in name.lower() or 'heroes' in name.lower() or 'h3' in name.lower()):
            exe_path = proc.info['exe']
            if exe_path:
                install_dir = Path(exe_path).parent
                found_paths.append((name, exe_path, install_dir))
                print(f"[OK] Found process: {name}")
                print(f"     Executable: {exe_path}")
                print(f"     Install Dir: {install_dir}")
                print()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# Method 2: Common Steam library locations
print("\nMethod 2: Checking common Steam library locations...")
print("-" * 70)

common_steam_paths = [
    Path("C:/Program Files (x86)/Steam/steamapps/common"),
    Path("C:/Program Files/Steam/steamapps/common"),
    Path("D:/SteamLibrary/steamapps/common"),
    Path("E:/SteamLibrary/steamapps/common"),
]

for steam_path in common_steam_paths:
    if steam_path.exists():
        print(f"Checking: {steam_path}")
        for item in steam_path.iterdir():
            if item.is_dir() and 'heroes' in item.name.lower():
                print(f"  [OK] Found: {item}")
                found_paths.append(("Directory", None, item))
    else:
        print(f"Not found: {steam_path}")

print()

# Method 3: Search for HOMM3 2.0.exe on C: drive
print("\nMethod 3: Quick search in Program Files...")
print("-" * 70)

program_files = [
    Path("C:/Program Files (x86)"),
    Path("C:/Program Files"),
]

for pf in program_files:
    if pf.exists():
        # Quick check for Heroes folders
        for item in pf.rglob("*Heroes*"):
            if item.is_dir():
                # Check if it has the executable
                for exe in ["HOMM3 2.0.exe", "heroes3.exe", "h3hd.exe"]:
                    exe_path = item / exe
                    if exe_path.exists():
                        print(f"[OK] Found: {exe_path}")
                        found_paths.append(("Search", str(exe_path), item))
                        break

print()
print("=" * 70)
print("Summary")
print("=" * 70)

if found_paths:
    print(f"\n[OK] Found {len(found_paths)} potential installation(s):\n")
    for i, (method, exe, install_dir) in enumerate(found_paths, 1):
        print(f"{i}. Installation Directory:")
        print(f"   {install_dir}")
        if exe:
            print(f"   Executable: {exe}")
        print()

    # Use the first one found
    main_install = found_paths[0][2]
    print("=" * 70)
    print("RECOMMENDED PATH:")
    print("-" * 70)
    print(f"\n{main_install}\n")

    # List key files
    print("Looking for game asset files...")
    print("-" * 70)

    asset_extensions = ['.lod', '.def', '.pcx', '.bmp', '.txt']
    asset_files = []

    for ext in asset_extensions:
        for file in main_install.rglob(f"*{ext}"):
            asset_files.append(file)

    if asset_files:
        print(f"\n[OK] Found {len(asset_files)} asset files")
        print("\nKey asset files:")
        for file in sorted(asset_files)[:20]:  # Show first 20
            print(f"  - {file.name}")
        if len(asset_files) > 20:
            print(f"  ... and {len(asset_files) - 20} more")

else:
    print("\n[X] No HoMM3 installation found!")
    print("\nPlease ensure:")
    print("1. Heroes of Might and Magic 3 is installed")
    print("2. The game process is running")
    print("3. Or manually locate your installation folder")

print()
print("=" * 70)
