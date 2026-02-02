"""
Window detection and management module.
Handles finding and focusing the HoMM3 game window on Windows.
"""

import time
import logging
from typing import Optional, Tuple
import win32gui
import win32con
import win32process
import psutil

logger = logging.getLogger(__name__)


class WindowManager:
    """Manages game window detection and focus."""

    # Common window titles for HoMM3
    WINDOW_TITLES = [
        "Heroes of Might & Magic III - HD Edition",  # Steam HD Edition (most common)
        "Heroes of Might & Magic III",               # GOG/standard version
        "Heroes of Might and Magic III",             # Alternative spelling
        "Heroes® of Might & Magic® III - HD Edition",  # With trademark symbols
        "Heroes III",
        "HOMM3",
        "H3"
    ]

    def __init__(self):
        """Initialize the window manager."""
        self.window_handle: Optional[int] = None
        self.window_title: Optional[str] = None
        self._cached_bounds: Optional[Tuple[int, int, int, int]] = None
        self._last_check_time: float = 0.0
        self._check_interval: float = 1.0  # Check window every second

        logger.info("WindowManager initialized")

    def find_game_window(self, custom_title: Optional[str] = None) -> bool:
        """
        Find the HoMM3 game window.

        Args:
            custom_title: Custom window title to search for (optional)

        Returns:
            True if window found, False otherwise
        """
        titles_to_check = [custom_title] if custom_title else self.WINDOW_TITLES

        def enum_windows_callback(hwnd, results):
            """Callback for enumerating windows."""
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                for title in titles_to_check:
                    if title.lower() in window_text.lower():
                        results.append((hwnd, window_text))
            return True

        results = []
        win32gui.EnumWindows(enum_windows_callback, results)

        if results:
            # Take the first match
            self.window_handle, self.window_title = results[0]
            logger.info(f"Found game window: '{self.window_title}' (handle: {self.window_handle})")
            return True
        else:
            logger.warning(f"Could not find game window with titles: {titles_to_check}")
            return False

    def find_window_by_process_name(self, process_name: str = "heroes3.exe") -> bool:
        """
        Find window by process name.

        Args:
            process_name: Name of the game process

        Returns:
            True if window found, False otherwise
        """
        try:
            # Find all processes with the given name
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    pid = proc.info['pid']

                    # Find window with this PID
                    def callback(hwnd, hwnds):
                        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                        if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                            hwnds.append(hwnd)
                        return True

                    hwnds = []
                    win32gui.EnumWindows(callback, hwnds)

                    if hwnds:
                        self.window_handle = hwnds[0]
                        self.window_title = win32gui.GetWindowText(self.window_handle)
                        logger.info(f"Found window by process: '{self.window_title}' (PID: {pid})")
                        return True

            logger.warning(f"Process '{process_name}' not found")
            return False

        except Exception as e:
            logger.error(f"Error finding window by process: {e}", exc_info=True)
            return False

    def is_window_valid(self) -> bool:
        """
        Check if the current window handle is still valid.

        Returns:
            True if window is valid and visible, False otherwise
        """
        if self.window_handle is None:
            return False

        try:
            return win32gui.IsWindow(self.window_handle) and win32gui.IsWindowVisible(self.window_handle)
        except Exception:
            return False

    def get_window_bounds(self, force_refresh: bool = False) -> Optional[Tuple[int, int, int, int]]:
        """
        Get window bounds (x, y, width, height).

        Args:
            force_refresh: Force refresh even if cached

        Returns:
            Tuple of (x, y, width, height) or None if window not found
        """
        current_time = time.time()

        # Use cache if available and not forcing refresh
        if not force_refresh and self._cached_bounds is not None:
            if current_time - self._last_check_time < self._check_interval:
                return self._cached_bounds

        if not self.is_window_valid():
            logger.warning("Window not valid, attempting to find it again")
            if not self.find_game_window():
                return None

        try:
            rect = win32gui.GetWindowRect(self.window_handle)
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y

            self._cached_bounds = (x, y, width, height)
            self._last_check_time = current_time

            return self._cached_bounds

        except Exception as e:
            logger.error(f"Error getting window bounds: {e}", exc_info=True)
            return None

    def get_client_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get client area bounds (excludes window decorations).

        Returns:
            Tuple of (x, y, width, height) or None if window not found
        """
        if not self.is_window_valid():
            return None

        try:
            # Get client rect
            client_rect = win32gui.GetClientRect(self.window_handle)
            left, top, right, bottom = client_rect

            # Convert to screen coordinates
            point = win32gui.ClientToScreen(self.window_handle, (left, top))
            x, y = point

            width = right - left
            height = bottom - top

            return (x, y, width, height)

        except Exception as e:
            logger.error(f"Error getting client bounds: {e}", exc_info=True)
            return None

    def focus_window(self) -> bool:
        """
        Bring the game window to the foreground.

        Returns:
            True if successful, False otherwise
        """
        if not self.is_window_valid():
            logger.warning("Cannot focus invalid window")
            return False

        try:
            # Restore if minimized
            if win32gui.IsIconic(self.window_handle):
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)

            # Set foreground
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.1)  # Small delay for window to focus

            logger.info(f"Focused window: '{self.window_title}'")
            return True

        except Exception as e:
            logger.error(f"Error focusing window: {e}", exc_info=True)
            return False

    def is_window_focused(self) -> bool:
        """
        Check if the game window is currently focused.

        Returns:
            True if focused, False otherwise
        """
        if not self.is_window_valid():
            return False

        try:
            foreground = win32gui.GetForegroundWindow()
            return foreground == self.window_handle
        except Exception:
            return False

    def minimize_window(self) -> bool:
        """
        Minimize the game window.

        Returns:
            True if successful, False otherwise
        """
        if not self.is_window_valid():
            return False

        try:
            win32gui.ShowWindow(self.window_handle, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            logger.error(f"Error minimizing window: {e}", exc_info=True)
            return False

    def maximize_window(self) -> bool:
        """
        Maximize the game window.

        Returns:
            True if successful, False otherwise
        """
        if not self.is_window_valid():
            return False

        try:
            win32gui.ShowWindow(self.window_handle, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            logger.error(f"Error maximizing window: {e}", exc_info=True)
            return False

    def get_window_info(self) -> dict:
        """
        Get comprehensive window information.

        Returns:
            Dictionary with window information
        """
        if not self.is_window_valid():
            return {"valid": False}

        bounds = self.get_window_bounds()
        client_bounds = self.get_client_bounds()

        return {
            "valid": True,
            "handle": self.window_handle,
            "title": self.window_title,
            "focused": self.is_window_focused(),
            "minimized": win32gui.IsIconic(self.window_handle),
            "bounds": bounds,
            "client_bounds": client_bounds
        }
