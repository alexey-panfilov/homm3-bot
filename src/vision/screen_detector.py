"""
Screen detector for identifying which game screen is currently displayed.
Uses template matching and heuristics to determine screen type.
"""

from typing import Optional, Dict
import numpy as np
from PIL import Image
import structlog

from .base_parser import GameScreen
from .template_matcher import TemplateMatcher

logger = structlog.get_logger(__name__)


class ScreenDetector:
    """
    Detects which game screen is currently displayed.

    Uses template matching for unique UI elements on each screen.
    """

    def __init__(self, template_matcher: TemplateMatcher):
        """
        Initialize screen detector.

        Args:
            template_matcher: TemplateMatcher instance
        """
        self.template_matcher = template_matcher
        self.logger = logger.bind(detector="ScreenDetector")

        # Screen-specific templates (will be loaded from assets)
        self.screen_templates = {
            GameScreen.ADVENTURE_MAP: [
                'adventure_map_indicator',
                'end_turn_button',
                'kingdom_overview_button',
            ],
            GameScreen.TOWN: [
                'town_hall_icon',
                'recruit_button',
                'town_background',
            ],
            GameScreen.COMBAT: [
                'combat_grid',
                'attack_button',
                'defend_button',
            ],
            GameScreen.KINGDOM_OVERVIEW: [
                'kingdom_title',
                'hero_list',
                'town_list',
            ],
            GameScreen.HERO_SCREEN: [
                'hero_portrait',
                'artifact_slots',
                'army_slots',
            ],
            GameScreen.MAIN_MENU: [
                'new_game_button',
                'load_game_button',
                'quit_button',
            ],
        }

    def detect_screen(
        self,
        image: np.ndarray | Image.Image,
        min_confidence: float = 0.7,
    ) -> tuple[GameScreen, float]:
        """
        Detect which screen is currently displayed.

        Args:
            image: Screenshot to analyze
            min_confidence: Minimum confidence threshold

        Returns:
            Tuple of (GameScreen, confidence)
        """
        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Score each screen type
        screen_scores: Dict[GameScreen, float] = {}

        for screen_type, templates in self.screen_templates.items():
            score = self._calculate_screen_score(image, templates)
            screen_scores[screen_type] = score

        # Find best match
        if not screen_scores:
            return GameScreen.UNKNOWN, 0.0

        best_screen = max(screen_scores, key=screen_scores.get)
        best_confidence = screen_scores[best_screen]

        if best_confidence < min_confidence:
            self.logger.debug(
                "Screen detection below threshold",
                detected=best_screen.name,
                confidence=best_confidence,
                threshold=min_confidence,
            )
            return GameScreen.UNKNOWN, best_confidence

        self.logger.debug(
            "Screen detected",
            screen=best_screen.name,
            confidence=best_confidence,
        )

        return best_screen, best_confidence

    def _calculate_screen_score(
        self,
        image: np.ndarray,
        templates: list[str],
    ) -> float:
        """
        Calculate confidence score for a screen type.

        Args:
            image: Screenshot
            templates: List of template names for this screen

        Returns:
            Confidence score (0.0-1.0)
        """
        if not templates:
            return 0.0

        total_score = 0.0
        matches_found = 0

        for template_name in templates:
            try:
                matches = self.template_matcher.match(
                    image,
                    template_name,
                    threshold=0.6,
                    single_best=True,
                )

                if matches:
                    total_score += matches[0].confidence
                    matches_found += 1
            except Exception as e:
                self.logger.debug(
                    "Template matching failed",
                    template=template_name,
                    error=str(e),
                )

        # Average score of found templates
        return total_score / len(templates) if templates else 0.0

    def is_adventure_map(
        self,
        image: np.ndarray | Image.Image,
        threshold: float = 0.7,
    ) -> bool:
        """Quick check if current screen is adventure map."""
        screen, confidence = self.detect_screen(image, threshold)
        return screen == GameScreen.ADVENTURE_MAP

    def is_town(
        self,
        image: np.ndarray | Image.Image,
        threshold: float = 0.7,
    ) -> bool:
        """Quick check if current screen is town."""
        screen, confidence = self.detect_screen(image, threshold)
        return screen == GameScreen.TOWN

    def is_combat(
        self,
        image: np.ndarray | Image.Image,
        threshold: float = 0.7,
    ) -> bool:
        """Quick check if current screen is combat."""
        screen, confidence = self.detect_screen(image, threshold)
        return screen == GameScreen.COMBAT

    def detect_by_color_histogram(
        self,
        image: np.ndarray,
    ) -> GameScreen:
        """
        Alternative detection using color histogram analysis.
        Useful as fallback when template matching fails.

        Args:
            image: Screenshot

        Returns:
            Most likely GameScreen
        """
        # Convert to HSV for better color analysis
        import cv2
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Calculate histogram
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])

        # Normalize
        hist_h = cv2.normalize(hist_h, hist_h).flatten()
        hist_s = cv2.normalize(hist_s, hist_s).flatten()

        # Heuristics based on dominant colors:
        # - Adventure map: Green/brown (terrain)
        # - Town: Stone gray, wood brown
        # - Combat: Hex grid patterns
        # - Menu: Dark background

        # Calculate dominant hue ranges
        green_brown = np.sum(hist_h[20:80])  # Green to brown hues
        gray_range = np.sum(hist_s[:50])      # Low saturation (gray)
        dark_range = np.mean(image) < 100     # Overall darkness

        if green_brown > 0.3:
            return GameScreen.ADVENTURE_MAP
        elif gray_range > 0.4:
            return GameScreen.TOWN
        elif dark_range:
            return GameScreen.MAIN_MENU
        else:
            return GameScreen.UNKNOWN

    def wait_for_screen(
        self,
        target_screen: GameScreen,
        timeout: float = 10.0,
        poll_interval: float = 0.5,
    ) -> bool:
        """
        Wait for a specific screen to appear.

        Args:
            target_screen: Screen to wait for
            timeout: Maximum time to wait (seconds)
            poll_interval: Time between checks (seconds)

        Returns:
            True if screen appeared, False if timeout
        """
        import time
        from ..capture.screen import ScreenCapture

        screen_capture = ScreenCapture()
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Capture current screen
            screenshot = screen_capture.capture()
            if screenshot is None:
                time.sleep(poll_interval)
                continue

            # Check if it's the target screen
            screen, confidence = self.detect_screen(screenshot)
            if screen == target_screen and confidence > 0.7:
                self.logger.info(
                    "Target screen detected",
                    screen=target_screen.name,
                    confidence=confidence,
                )
                return True

            time.sleep(poll_interval)

        self.logger.warning(
            "Timeout waiting for screen",
            target=target_screen.name,
            timeout=timeout,
        )
        return False
