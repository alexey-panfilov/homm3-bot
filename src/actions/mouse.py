"""
Mouse control module with safety features.
Provides safe mouse movement and clicking with bounds checking and verification.
"""

import time
import logging
from typing import Optional, Tuple, Callable
import pyautogui
from pynput import mouse

logger = logging.getLogger(__name__)

# Disable PyAutoGUI's failsafe (we'll implement our own)
pyautogui.FAILSAFE = False


class SafetyViolationError(Exception):
    """Raised when a mouse action violates safety constraints."""
    pass


class MouseController:
    """Safe mouse controller with bounds checking and action verification."""

    def __init__(
        self,
        allowed_bounds: Optional[Tuple[int, int, int, int]] = None,
        default_duration: float = 0.2,
        click_delay: float = 0.1,
        enable_verification: bool = True
    ):
        """
        Initialize mouse controller.

        Args:
            allowed_bounds: (x, y, width, height) - mouse restricted to this area
            default_duration: Default duration for mouse movements
            click_delay: Delay after clicks
            enable_verification: Enable action verification
        """
        self.allowed_bounds = allowed_bounds
        self.default_duration = default_duration
        self.click_delay = click_delay
        self.enable_verification = enable_verification

        self._emergency_stop = False
        self._action_count = 0
        self._max_actions_per_second = 20  # Rate limiting

        # PyAutoGUI settings
        pyautogui.PAUSE = 0.05  # Small pause between PyAutoGUI calls

        logger.info(f"MouseController initialized (bounds: {allowed_bounds})")

    def set_allowed_bounds(self, x: int, y: int, width: int, height: int) -> None:
        """
        Set the allowed mouse movement bounds.

        Args:
            x, y: Top-left corner coordinates
            width, height: Dimensions of allowed area
        """
        self.allowed_bounds = (x, y, width, height)
        logger.info(f"Mouse bounds updated: {self.allowed_bounds}")

    def emergency_stop(self) -> None:
        """Emergency stop - blocks all mouse actions."""
        self._emergency_stop = True
        logger.warning("EMERGENCY STOP activated - all mouse actions blocked")

    def reset_emergency_stop(self) -> None:
        """Reset emergency stop."""
        self._emergency_stop = False
        logger.info("Emergency stop reset")

    def _check_safety(self, x: int, y: int) -> None:
        """
        Check if coordinates are within allowed bounds.

        Args:
            x, y: Coordinates to check

        Raises:
            SafetyViolationError: If coordinates outside bounds or emergency stop active
        """
        if self._emergency_stop:
            raise SafetyViolationError("Emergency stop is active")

        if self.allowed_bounds is not None:
            bx, by, bw, bh = self.allowed_bounds
            if not (bx <= x <= bx + bw and by <= y <= by + bh):
                raise SafetyViolationError(
                    f"Coordinates ({x}, {y}) outside allowed bounds {self.allowed_bounds}"
                )

    def get_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.

        Returns:
            (x, y) coordinates
        """
        return pyautogui.position()

    def move_to(
        self,
        x: int,
        y: int,
        duration: Optional[float] = None,
        verify: bool = True
    ) -> bool:
        """
        Move mouse to absolute position.

        Args:
            x, y: Target coordinates
            duration: Movement duration (uses default if None)
            verify: Verify the mouse reached target position

        Returns:
            True if successful, False otherwise
        """
        try:
            self._check_safety(x, y)

            duration = duration if duration is not None else self.default_duration

            logger.debug(f"Moving mouse to ({x}, {y}) over {duration}s")
            pyautogui.moveTo(x, y, duration=duration)

            # Verification
            if verify and self.enable_verification:
                time.sleep(0.05)
                actual_x, actual_y = self.get_position()
                if abs(actual_x - x) > 5 or abs(actual_y - y) > 5:
                    logger.warning(
                        f"Mouse position verification failed: "
                        f"target=({x}, {y}), actual=({actual_x}, {actual_y})"
                    )
                    return False

            self._action_count += 1
            return True

        except SafetyViolationError as e:
            logger.error(f"Safety violation: {e}")
            return False
        except Exception as e:
            logger.error(f"Mouse move failed: {e}", exc_info=True)
            return False

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = 'left',
        clicks: int = 1,
        interval: float = 0.1
    ) -> bool:
        """
        Click at specified position or current position.

        Args:
            x, y: Click coordinates (None for current position)
            button: 'left', 'right', or 'middle'
            clicks: Number of clicks
            interval: Interval between multiple clicks

        Returns:
            True if successful, False otherwise
        """
        try:
            # Move to position if specified
            if x is not None and y is not None:
                if not self.move_to(x, y):
                    return False
            else:
                # Check current position is safe
                x, y = self.get_position()
                self._check_safety(x, y)

            logger.debug(f"Clicking {button} button at ({x}, {y}), {clicks} time(s)")
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)

            time.sleep(self.click_delay)
            self._action_count += clicks
            return True

        except SafetyViolationError as e:
            logger.error(f"Safety violation: {e}")
            return False
        except Exception as e:
            logger.error(f"Click failed: {e}", exc_info=True)
            return False

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Double-click at position.

        Args:
            x, y: Click coordinates (None for current position)

        Returns:
            True if successful, False otherwise
        """
        return self.click(x, y, clicks=2, interval=0.1)

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Right-click at position.

        Args:
            x, y: Click coordinates (None for current position)

        Returns:
            True if successful, False otherwise
        """
        return self.click(x, y, button='right')

    def drag(
        self,
        x: int,
        y: int,
        duration: Optional[float] = None,
        button: str = 'left'
    ) -> bool:
        """
        Drag mouse to position (hold button while moving).

        Args:
            x, y: Target coordinates
            duration: Drag duration
            button: Button to hold during drag

        Returns:
            True if successful, False otherwise
        """
        try:
            self._check_safety(x, y)

            duration = duration if duration is not None else self.default_duration

            logger.debug(f"Dragging to ({x}, {y}) with {button} button")
            pyautogui.dragTo(x, y, duration=duration, button=button)

            time.sleep(self.click_delay)
            self._action_count += 1
            return True

        except SafetyViolationError as e:
            logger.error(f"Safety violation: {e}")
            return False
        except Exception as e:
            logger.error(f"Drag failed: {e}", exc_info=True)
            return False

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Scroll mouse wheel.

        Args:
            clicks: Number of scroll clicks (positive = up, negative = down)
            x, y: Position to scroll at (None for current position)

        Returns:
            True if successful, False otherwise
        """
        try:
            if x is not None and y is not None:
                if not self.move_to(x, y):
                    return False

            logger.debug(f"Scrolling {clicks} clicks")
            pyautogui.scroll(clicks)

            self._action_count += 1
            return True

        except Exception as e:
            logger.error(f"Scroll failed: {e}", exc_info=True)
            return False

    def click_and_verify(
        self,
        x: int,
        y: int,
        verification_func: Callable[[], bool],
        max_retries: int = 3,
        retry_delay: float = 0.5
    ) -> bool:
        """
        Click and verify the action succeeded using a verification function.

        Args:
            x, y: Click coordinates
            verification_func: Function that returns True if action succeeded
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries

        Returns:
            True if click verified, False otherwise
        """
        for attempt in range(max_retries):
            if self.click(x, y):
                time.sleep(retry_delay)

                if verification_func():
                    logger.debug(f"Click verified on attempt {attempt + 1}")
                    return True
                else:
                    logger.warning(f"Click verification failed, attempt {attempt + 1}/{max_retries}")
            else:
                logger.warning(f"Click failed, attempt {attempt + 1}/{max_retries}")

            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        logger.error(f"Click and verify failed after {max_retries} attempts")
        return False

    def get_stats(self) -> dict:
        """
        Get mouse controller statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "action_count": self._action_count,
            "emergency_stop": self._emergency_stop,
            "allowed_bounds": self.allowed_bounds,
            "verification_enabled": self.enable_verification
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._action_count = 0
        logger.info("Mouse stats reset")
