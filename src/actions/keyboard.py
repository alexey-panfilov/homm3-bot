"""
Keyboard control module for sending keystrokes to the game.
"""

import time
import logging
from typing import Optional, List
import pyautogui
from pynput.keyboard import Key, Controller

logger = logging.getLogger(__name__)


class KeyboardController:
    """Handles keyboard input for the game."""

    def __init__(self, default_delay: float = 0.1):
        """
        Initialize keyboard controller.

        Args:
            default_delay: Default delay after key presses
        """
        self.default_delay = default_delay
        self.controller = Controller()
        self._action_count = 0

        logger.info("KeyboardController initialized")

    def press_key(self, key: str, delay: Optional[float] = None) -> bool:
        """
        Press and release a single key.

        Args:
            key: Key to press (e.g., 'a', 'enter', 'esc')
            delay: Delay after keypress (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            delay = delay if delay is not None else self.default_delay

            logger.debug(f"Pressing key: {key}")
            pyautogui.press(key)

            time.sleep(delay)
            self._action_count += 1
            return True

        except Exception as e:
            logger.error(f"Key press failed: {e}", exc_info=True)
            return False

    def press_keys(self, keys: List[str], interval: float = 0.1) -> bool:
        """
        Press multiple keys in sequence.

        Args:
            keys: List of keys to press
            interval: Delay between key presses

        Returns:
            True if all successful, False otherwise
        """
        try:
            for key in keys:
                if not self.press_key(key, delay=interval):
                    return False
            return True

        except Exception as e:
            logger.error(f"Multiple key press failed: {e}", exc_info=True)
            return False

    def hotkey(self, *keys: str, delay: Optional[float] = None) -> bool:
        """
        Press a hotkey combination (e.g., ctrl+c).

        Args:
            *keys: Keys to press simultaneously (e.g., 'ctrl', 'c')
            delay: Delay after hotkey

        Returns:
            True if successful, False otherwise
        """
        try:
            delay = delay if delay is not None else self.default_delay

            logger.debug(f"Pressing hotkey: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)

            time.sleep(delay)
            self._action_count += 1
            return True

        except Exception as e:
            logger.error(f"Hotkey press failed: {e}", exc_info=True)
            return False

    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text character by character.

        Args:
            text: Text to type
            interval: Delay between characters

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Typing text: {text[:50]}...")
            pyautogui.write(text, interval=interval)

            time.sleep(self.default_delay)
            self._action_count += len(text)
            return True

        except Exception as e:
            logger.error(f"Text typing failed: {e}", exc_info=True)
            return False

    def hold_key(self, key: str, duration: float = 1.0) -> bool:
        """
        Hold a key down for a duration.

        Args:
            key: Key to hold
            duration: How long to hold the key

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Holding key {key} for {duration}s")

            # Convert string key to pynput Key if needed
            try:
                pynput_key = getattr(Key, key)
            except AttributeError:
                pynput_key = key

            self.controller.press(pynput_key)
            time.sleep(duration)
            self.controller.release(pynput_key)

            time.sleep(self.default_delay)
            self._action_count += 1
            return True

        except Exception as e:
            logger.error(f"Hold key failed: {e}", exc_info=True)
            return False

    def press_enter(self) -> bool:
        """Press Enter key."""
        return self.press_key('enter')

    def press_escape(self) -> bool:
        """Press Escape key."""
        return self.press_key('esc')

    def press_space(self) -> bool:
        """Press Space key."""
        return self.press_key('space')

    def press_tab(self) -> bool:
        """Press Tab key."""
        return self.press_key('tab')

    def get_stats(self) -> dict:
        """
        Get keyboard controller statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "action_count": self._action_count,
            "default_delay": self.default_delay
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._action_count = 0
        logger.info("Keyboard stats reset")
