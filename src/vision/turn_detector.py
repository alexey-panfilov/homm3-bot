"""
Turn detector for identifying when it's the player's turn in HoMM3.
Monitors UI elements and game state changes.
"""

from typing import Optional, Callable
from dataclasses import dataclass
import time
import numpy as np
from PIL import Image
import structlog

from .template_matcher import TemplateMatcher
from .base_parser import GameScreen

logger = structlog.get_logger(__name__)


@dataclass
class TurnInfo:
    """Information about current turn state."""
    is_player_turn: bool = False
    turn_number: int = 0
    day: int = 1
    week: int = 1
    month: int = 1
    confidence: float = 0.0
    timestamp: float = 0.0


class TurnDetector:
    """
    Detects when it's the player's turn.

    Uses multiple detection methods:
    1. End Turn button visibility and state
    2. Movement indicators on heroes
    3. UI element accessibility
    4. Screen activity detection
    """

    def __init__(
        self,
        template_matcher: Optional[TemplateMatcher] = None,
    ):
        """
        Initialize turn detector.

        Args:
            template_matcher: TemplateMatcher instance
        """
        self.template_matcher = template_matcher
        self.logger = logger.bind(detector="TurnDetector")

        # Last known state for change detection
        self.last_state: Optional[TurnInfo] = None
        self.last_screenshot_hash: Optional[int] = None

    def is_player_turn(
        self,
        image: np.ndarray | Image.Image,
        current_screen: GameScreen = GameScreen.ADVENTURE_MAP,
    ) -> TurnInfo:
        """
        Detect if it's currently the player's turn.

        Args:
            image: Current screenshot
            current_screen: Which screen is displayed

        Returns:
            TurnInfo with detection results
        """
        if isinstance(image, Image.Image):
            image = np.array(image)

        turn_info = TurnInfo(timestamp=time.time())

        # Only check on adventure map
        if current_screen != GameScreen.ADVENTURE_MAP:
            turn_info.is_player_turn = False
            turn_info.confidence = 0.9
            return turn_info

        # Method 1: Check for active End Turn button
        end_turn_confidence = self._check_end_turn_button(image)

        # Method 2: Check for hero movement indicators
        hero_movement_confidence = self._check_hero_movement(image)

        # Method 3: Check for AI turn indicator
        ai_turn_confidence = self._check_ai_turn_indicator(image)

        # Combine confidences
        # If AI turn detected, definitely not player turn
        if ai_turn_confidence > 0.7:
            turn_info.is_player_turn = False
            turn_info.confidence = ai_turn_confidence
        # If End Turn button is visible, likely player turn
        elif end_turn_confidence > 0.7:
            turn_info.is_player_turn = True
            turn_info.confidence = end_turn_confidence
        # If heroes can move, probably player turn
        elif hero_movement_confidence > 0.6:
            turn_info.is_player_turn = True
            turn_info.confidence = hero_movement_confidence
        else:
            # Uncertain
            turn_info.is_player_turn = False
            turn_info.confidence = 0.3

        self.logger.debug(
            "Turn detection",
            is_player_turn=turn_info.is_player_turn,
            confidence=turn_info.confidence,
            methods={
                'end_turn': end_turn_confidence,
                'hero_movement': hero_movement_confidence,
                'ai_turn': ai_turn_confidence,
            }
        )

        self.last_state = turn_info
        return turn_info

    def _check_end_turn_button(self, image: np.ndarray) -> float:
        """
        Check if End Turn button is visible and active.

        Args:
            image: Screenshot

        Returns:
            Confidence that button is active (0.0-1.0)
        """
        if not self.template_matcher:
            return 0.5  # Unknown

        try:
            # Look for active End Turn button
            matches = self.template_matcher.match(
                image,
                'end_turn_button',
                threshold=0.7,
                single_best=True,
            )

            if matches:
                return matches[0].confidence

            # Try inactive/grayed out button
            inactive_matches = self.template_matcher.match(
                image,
                'end_turn_button_inactive',
                threshold=0.7,
                single_best=True,
            )

            if inactive_matches:
                # Inactive button means AI turn
                return 0.0

        except Exception as e:
            self.logger.debug("End turn button detection failed", error=str(e))

        return 0.5  # Unknown

    def _check_hero_movement(self, image: np.ndarray) -> float:
        """
        Check for hero movement indicators.

        Args:
            image: Screenshot

        Returns:
            Confidence that heroes can move (0.0-1.0)
        """
        if not self.template_matcher:
            return 0.5

        try:
            # Look for movement arrow/indicator on heroes
            matches = self.template_matcher.match(
                image,
                'hero_can_move',
                threshold=0.6,
                single_best=False,
            )

            if matches:
                # More heroes that can move = higher confidence
                confidence = min(len(matches) * 0.3, 1.0)
                return confidence

        except Exception as e:
            self.logger.debug("Hero movement detection failed", error=str(e))

        return 0.5

    def _check_ai_turn_indicator(self, image: np.ndarray) -> float:
        """
        Check for AI turn indicator (hourglass, AI hero animation, etc.)

        Args:
            image: Screenshot

        Returns:
            Confidence that it's AI turn (0.0-1.0)
        """
        if not self.template_matcher:
            return 0.0

        try:
            # Look for hourglass or AI turn indicator
            indicators = [
                'ai_turn_hourglass',
                'ai_hero_moving',
                'enemy_turn_text',
            ]

            for indicator in indicators:
                try:
                    matches = self.template_matcher.match(
                        image,
                        indicator,
                        threshold=0.7,
                        single_best=True,
                    )

                    if matches:
                        return matches[0].confidence
                except:
                    continue

        except Exception as e:
            self.logger.debug("AI turn detection failed", error=str(e))

        return 0.0

    def wait_for_player_turn(
        self,
        max_wait: float = 60.0,
        poll_interval: float = 0.5,
        screenshot_callback: Optional[Callable[[], np.ndarray]] = None,
    ) -> bool:
        """
        Wait until it's the player's turn.

        Args:
            max_wait: Maximum time to wait (seconds)
            poll_interval: Time between checks (seconds)
            screenshot_callback: Function to get current screenshot

        Returns:
            True if player turn detected, False if timeout
        """
        if not screenshot_callback:
            from ..capture.screen import ScreenCapture
            screen_capture = ScreenCapture()
            screenshot_callback = lambda: screen_capture.capture()

        start_time = time.time()

        while time.time() - start_time < max_wait:
            screenshot = screenshot_callback()
            if screenshot is None:
                time.sleep(poll_interval)
                continue

            turn_info = self.is_player_turn(screenshot)

            if turn_info.is_player_turn and turn_info.confidence > 0.7:
                self.logger.info(
                    "Player turn detected",
                    wait_time=time.time() - start_time,
                    confidence=turn_info.confidence,
                )
                return True

            time.sleep(poll_interval)

        self.logger.warning(
            "Timeout waiting for player turn",
            max_wait=max_wait,
        )
        return False

    def detect_turn_change(
        self,
        before_image: np.ndarray,
        after_image: np.ndarray,
    ) -> bool:
        """
        Detect if turn changed between two screenshots.

        Args:
            before_image: Screenshot before
            after_image: Screenshot after

        Returns:
            True if turn changed
        """
        before_info = self.is_player_turn(before_image)
        after_info = self.is_player_turn(after_image)

        return before_info.is_player_turn != after_info.is_player_turn

    def detect_screen_activity(
        self,
        image1: np.ndarray,
        image2: np.ndarray,
        threshold: float = 0.05,
    ) -> bool:
        """
        Detect significant screen activity (AI moving, animations, etc.)

        Args:
            image1: First screenshot
            image2: Second screenshot
            threshold: Minimum change threshold

        Returns:
            True if significant activity detected
        """
        import cv2

        # Convert to grayscale
        gray1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)

        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)

        # Calculate change percentage
        change_ratio = np.sum(diff > 30) / diff.size

        return change_ratio > threshold

    def get_turn_timing(self) -> Optional[float]:
        """
        Get the duration of the last turn.

        Returns:
            Turn duration in seconds or None
        """
        if not self.last_state:
            return None

        return time.time() - self.last_state.timestamp
