"""
Troubleshoot window detection issues.
Run this with HoMM3 open to find the exact window title.
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

import win32gui
import win32process
import psutil

print("=" * 70)
print("HoMM3 Bot - Window Detection Troubleshooter")
print("=" * 70)
print()
print("Make sure Heroes of Might and Magic 3 is running before proceeding!")
print()

# Get all visible windows
def get_all_windows():
    """Get all visible windows with their titles and process names."""
    windows = []

    def callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Only include windows with titles
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name()
                    except:
                        process_name = "Unknown"

                    results.append({
                        'hwnd': hwnd,
                        'title': title,
                        'pid': pid,
                        'process': process_name
                    })
                except:
                    pass
        return True

    win32gui.EnumWindows(callback, windows)
    return windows

print("Step 1: Listing all visible windows...")
print("-" * 70)

all_windows = get_all_windows()

# Filter for potential game windows
print(f"\nFound {len(all_windows)} visible windows")
print("\nAll windows with titles:")
print("-" * 70)

for i, win in enumerate(all_windows, 1):
    print(f"{i:3}. Title: {win['title'][:60]}")
    print(f"     Process: {win['process']} (PID: {win['pid']})")
    print()

# Look for potential HoMM3 windows
print("\n" + "=" * 70)
print("Step 2: Searching for potential HoMM3 windows...")
print("-" * 70)

search_terms = ['heroes', 'homm', 'h3', 'might', 'magic']
potential_matches = []

for win in all_windows:
    title_lower = win['title'].lower()
    process_lower = win['process'].lower()

    # Check if any search term is in the title or process name
    for term in search_terms:
        if term in title_lower or term in process_lower:
            potential_matches.append(win)
            break

if potential_matches:
    print(f"\n[OK] Found {len(potential_matches)} potential HoMM3 window(s):\n")
    for i, win in enumerate(potential_matches, 1):
        print(f"{i}. Window Title: '{win['title']}'")
        print(f"   Process: {win['process']}")
        print(f"   Handle: {win['hwnd']}")
        print()

    print("=" * 70)
    print("SOLUTION:")
    print("-" * 70)
    print("\nAdd the EXACT window title to your config/default.yaml:")
    print("\nwindow:")
    print(f"  window_title: \"{potential_matches[0]['title']}\"")
    print(f"  process_name: {potential_matches[0]['process']}")
    print()
else:
    print("\n[X] No potential HoMM3 windows found!")
    print("\nTroubleshooting steps:")
    print("1. Make sure Heroes of Might and Magic 3 is running")
    print("2. Check if the game window is visible (not minimized)")
    print("3. Look through the window list above for your game window")
    print()
    print("If you see your game window in the list above, copy its exact title")
    print("and add it to config/default.yaml like this:")
    print()
    print("window:")
    print("  window_title: \"Exact Window Title Here\"")
    print()

# Check what our bot is currently searching for
print("=" * 70)
print("Step 3: Current bot search configuration")
print("-" * 70)

try:
    from capture.window import WindowManager
    wm = WindowManager()
    print("\nThe bot is searching for windows with these titles:")
    for title in wm.WINDOW_TITLES:
        print(f"  - \"{title}\"")

    print(f"\nOr process name: '{wm.WINDOW_TITLES[0]}'")

    # Try to find the window using current logic
    print("\n" + "-" * 70)
    print("Testing current detection logic...")
    print("-" * 70)

    if wm.find_game_window():
        print(f"\n[OK] SUCCESS! Window found: '{wm.window_title}'")
        print(f"  Handle: {wm.window_handle}")
        bounds = wm.get_window_bounds()
        if bounds:
            print(f"  Position: ({bounds[0]}, {bounds[1]})")
            print(f"  Size: {bounds[2]}x{bounds[3]}")
    else:
        print("\n[X] Window detection FAILED using current logic")
        print("\nTo fix this:")
        print("1. Find your game window in the list above")
        print("2. Copy the exact window title")
        print("3. Update config/default.yaml with the exact title")

except Exception as e:
    print(f"\n[X] Error testing detection: {e}")

print("\n" + "=" * 70)
print("Troubleshooting complete!")
print("=" * 70)
