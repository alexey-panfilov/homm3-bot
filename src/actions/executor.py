"""
Action executor - high-level interface for game actions.
Combines mouse and keyboard control with game-specific actions.
"""

import time
import logging
from typing import Optional, Tuple, Callable
from .mouse import MouseController
from .keyboard import KeyboardController

logger = logging.getLogger(__name__)


class ActionExecutor:
    """High-level action executor for game interactions."""

    def __init__(
        self,
        mouse_controller: Optional[MouseController] = None,
        keyboard_controller: Optional[KeyboardController] = None
    ):
        """
        Initialize action executor.

        Args:
            mouse_controller: MouseController instance (creates new if None)
            keyboard_controller: KeyboardController instance (creates new if None)
        """
        self.mouse = mouse_controller or MouseController()
        self.keyboard = keyboard_controller or KeyboardController()

        self._enabled = True
        logger.info("ActionExecutor initialized")

    def enable(self) -> None:
        """Enable action execution."""
        self._enabled = True
        logger.info("Action execution enabled")

    def disable(self) -> None:
        """Disable action execution."""
        self._enabled = False
        logger.info("Action execution disabled")

    def is_enabled(self) -> bool:
        """Check if action execution is enabled."""
        return self._enabled

    def click_at(
        self,
        x: int,
        y: int,
        button: str = 'left',
        verify: Optional[Callable[[], bool]] = None
    ) -> bool:
        """
        Click at coordinates with optional verification.

        Args:
            x, y: Coordinates to click
            button: Mouse button ('left', 'right', 'middle')
            verify: Optional verification function

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            logger.warning("Action execution is disabled")
            return False

        if verify is not None:
            return self.mouse.click_and_verify(x, y, verify)
        else:
            return self.mouse.click(x, y, button=button)

    def move_and_click(
        self,
        x: int,
        y: int,
        duration: float = 0.2,
        pause_before_click: float = 0.1
    ) -> bool:
        """
        Move to position and click.

        Args:
            x, y: Target coordinates
            duration: Movement duration
            pause_before_click: Pause before clicking

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        if self.mouse.move_to(x, y, duration=duration):
            time.sleep(pause_before_click)
            return self.mouse.click()
        return False

    def drag_from_to(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        duration: float = 0.5
    ) -> bool:
        """
        Drag from one position to another.

        Args:
            from_x, from_y: Starting position
            to_x, to_y: Ending position
            duration: Drag duration

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        if self.mouse.move_to(from_x, from_y):
            time.sleep(0.1)
            return self.mouse.drag(to_x, to_y, duration=duration)
        return False

    def confirm_dialog(self) -> bool:
        """Confirm a dialog (press Enter)."""
        if not self._enabled:
            return False
        return self.keyboard.press_enter()

    def cancel_dialog(self) -> bool:
        """Cancel a dialog (press Escape)."""
        if not self._enabled:
            return False
        return self.keyboard.press_escape()

    def end_turn(self) -> bool:
        """
        End the current turn (press 'E' key in HoMM3).

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        logger.info("Ending turn")
        return self.keyboard.press_key('e')

    def open_kingdom_overview(self) -> bool:
        """Open kingdom overview (K key)."""
        if not self._enabled:
            return False
        return self.keyboard.press_key('k')

    def toggle_grid(self) -> bool:
        """Toggle grid display (G key)."""
        if not self._enabled:
            return False
        return self.keyboard.press_key('g')

    def quick_save(self) -> bool:
        """Quick save (F5 key)."""
        if not self._enabled:
            return False
        logger.info("Quick saving")
        return self.keyboard.press_key('f5')

    def quick_load(self) -> bool:
        """Quick load (F9 key)."""
        if not self._enabled:
            return False
        logger.info("Quick loading")
        return self.keyboard.press_key('f9')

    def wait(self, seconds: float) -> None:
        """
        Wait for specified seconds.

        Args:
            seconds: Time to wait
        """
        logger.debug(f"Waiting {seconds}s")
        time.sleep(seconds)

    def execute_sequence(self, actions: list, stop_on_failure: bool = True) -> bool:
        """
        Execute a sequence of actions.

        Args:
            actions: List of (method_name, args, kwargs) tuples
            stop_on_failure: Stop if any action fails

        Returns:
            True if all successful, False otherwise
        """
        if not self._enabled:
            return False

        logger.info(f"Executing action sequence ({len(actions)} actions)")

        for i, action in enumerate(actions):
            method_name, args, kwargs = action

            try:
                method = getattr(self, method_name)
                success = method(*args, **kwargs)

                if not success and stop_on_failure:
                    logger.error(f"Action sequence failed at step {i+1}: {method_name}")
                    return False

            except Exception as e:
                logger.error(f"Action sequence error at step {i+1}: {e}", exc_info=True)
                if stop_on_failure:
                    return False

        logger.info("Action sequence completed successfully")
        return True

    def emergency_stop(self) -> None:
        """Emergency stop - disable all actions."""
        self.disable()
        self.mouse.emergency_stop()
        logger.warning("EMERGENCY STOP - All actions disabled")

    def reset_emergency_stop(self) -> None:
        """Reset emergency stop."""
        self.enable()
        self.mouse.reset_emergency_stop()
        logger.info("Emergency stop reset")

    def get_stats(self) -> dict:
        """
        Get combined statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "enabled": self._enabled,
            "mouse": self.mouse.get_stats(),
            "keyboard": self.keyboard.get_stats()
        }
