"""
Screen capture module for capturing game window screenshots.
Uses mss for efficient screen capture on Windows.
"""

import time
from typing import Optional, Tuple
import numpy as np
from PIL import Image
import mss
import logging

logger = logging.getLogger(__name__)


class ScreenCapture:
    """Handles screen capture operations for the game window."""

    def __init__(self, target_fps: float = 2.0):
        """
        Initialize the screen capture module.

        Args:
            target_fps: Target frames per second for capture (default: 2.0)
        """
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        self.last_capture_time = 0.0
        self.sct = mss.mss()
        self._monitor_bounds: Optional[dict] = None

        logger.info(f"ScreenCapture initialized with target FPS: {target_fps}")

    def set_capture_region(self, x: int, y: int, width: int, height: int) -> None:
        """
        Set the region of the screen to capture.

        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of capture region
            height: Height of capture region
        """
        self._monitor_bounds = {
            "top": y,
            "left": x,
            "width": width,
            "height": height
        }
        logger.info(f"Capture region set to: x={x}, y={y}, w={width}, h={height}")

    def capture(self, as_numpy: bool = True) -> Optional[np.ndarray | Image.Image]:
        """
        Capture the current screen region.

        Args:
            as_numpy: If True, return as numpy array; if False, return as PIL Image

        Returns:
            Captured image as numpy array or PIL Image, or None if capture fails
        """
        try:
            # Rate limiting
            current_time = time.time()
            elapsed = current_time - self.last_capture_time
            if elapsed < self.frame_interval:
                time.sleep(self.frame_interval - elapsed)

            # Capture screen
            if self._monitor_bounds is None:
                logger.warning("Capture region not set, capturing primary monitor")
                screenshot = self.sct.grab(self.sct.monitors[1])
            else:
                screenshot = self.sct.grab(self._monitor_bounds)

            self.last_capture_time = time.time()

            # Convert to PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

            if as_numpy:
                # Convert to numpy array (RGB format for OpenCV compatibility)
                return np.array(img)
            else:
                return img

        except Exception as e:
            logger.error(f"Screen capture failed: {e}", exc_info=True)
            return None

    def capture_full_screen(self, monitor_num: int = 1, as_numpy: bool = True) -> Optional[np.ndarray | Image.Image]:
        """
        Capture the full screen of a specific monitor.

        Args:
            monitor_num: Monitor number (1 for primary)
            as_numpy: If True, return as numpy array; if False, return as PIL Image

        Returns:
            Captured image as numpy array or PIL Image, or None if capture fails
        """
        try:
            screenshot = self.sct.grab(self.sct.monitors[monitor_num])
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

            if as_numpy:
                return np.array(img)
            else:
                return img

        except Exception as e:
            logger.error(f"Full screen capture failed: {e}", exc_info=True)
            return None

    def get_monitor_info(self) -> list[dict]:
        """
        Get information about all monitors.

        Returns:
            List of monitor information dictionaries
        """
        return self.sct.monitors

    def save_screenshot(self, filepath: str) -> bool:
        """
        Capture and save a screenshot to file.

        Args:
            filepath: Path where to save the screenshot

        Returns:
            True if successful, False otherwise
        """
        try:
            img = self.capture(as_numpy=False)
            if img is not None:
                img.save(filepath)
                logger.info(f"Screenshot saved to: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}", exc_info=True)
            return False

    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'sct'):
                self.sct.close()
        except:
            pass


class FrameBuffer:
    """Buffer for storing recent frames for temporal analysis."""

    def __init__(self, max_frames: int = 10):
        """
        Initialize frame buffer.

        Args:
            max_frames: Maximum number of frames to store
        """
        self.max_frames = max_frames
        self.frames: list[np.ndarray] = []
        self.timestamps: list[float] = []

    def add_frame(self, frame: np.ndarray) -> None:
        """
        Add a frame to the buffer.

        Args:
            frame: Frame to add as numpy array
        """
        self.frames.append(frame)
        self.timestamps.append(time.time())

        # Remove oldest frame if buffer is full
        if len(self.frames) > self.max_frames:
            self.frames.pop(0)
            self.timestamps.pop(0)

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the most recent frame."""
        return self.frames[-1] if self.frames else None

    def get_frame(self, index: int) -> Optional[np.ndarray]:
        """Get frame at specific index (negative indices work)."""
        try:
            return self.frames[index]
        except IndexError:
            return None

    def get_all_frames(self) -> list[np.ndarray]:
        """Get all frames in the buffer."""
        return self.frames.copy()

    def clear(self) -> None:
        """Clear the frame buffer."""
        self.frames.clear()
        self.timestamps.clear()

    def __len__(self) -> int:
        """Get number of frames in buffer."""
        return len(self.frames)
