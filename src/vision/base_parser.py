"""
Base parser for game state extraction.
Provides common functionality for all screen parsers.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Any, Dict
from pathlib import Path
import numpy as np
from PIL import Image
import structlog

logger = structlog.get_logger(__name__)


class GameScreen(Enum):
    """Enumeration of different game screens."""
    UNKNOWN = auto()
    MAIN_MENU = auto()
    ADVENTURE_MAP = auto()
    TOWN = auto()
    COMBAT = auto()
    KINGDOM_OVERVIEW = auto()
    HERO_SCREEN = auto()
    MARKETPLACE = auto()
    TAVERN = auto()
    PUZZLE_MAP = auto()
    HIGH_SCORES = auto()


@dataclass
class GameState:
    """Base class for game state information."""
    screen: GameScreen = GameScreen.UNKNOWN
    timestamp: float = 0.0
    confidence: float = 0.0  # How confident we are about this state
    raw_image: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (f"GameState(screen={self.screen.name}, "
                f"confidence={self.confidence:.2f})")


class BaseParser(ABC):
    """
    Abstract base class for screen parsers.

    Each parser is responsible for:
    1. Detecting if current screen matches its type
    2. Extracting relevant information from the screen
    3. Validating the extracted state
    """

    def __init__(
        self,
        template_matcher=None,
        confidence_threshold: float = 0.75,
    ):
        """
        Initialize parser.

        Args:
            template_matcher: TemplateMatcher instance for UI detection
            confidence_threshold: Minimum confidence to accept detection
        """
        self.template_matcher = template_matcher
        self.confidence_threshold = confidence_threshold
        self.logger = logger.bind(parser=self.__class__.__name__)

    @abstractmethod
    def can_parse(self, image: np.ndarray | Image.Image) -> float:
        """
        Check if this parser can handle the given image.

        Args:
            image: Screenshot to analyze

        Returns:
            Confidence score (0.0-1.0) that this is the correct screen type
        """
        pass

    @abstractmethod
    def parse(self, image: np.ndarray | Image.Image) -> GameState:
        """
        Parse game state from image.

        Args:
            image: Screenshot to analyze

        Returns:
            GameState object with extracted information
        """
        pass

    def validate_state(self, state: GameState) -> bool:
        """
        Validate extracted state for consistency.

        Args:
            state: Parsed game state

        Returns:
            True if state appears valid
        """
        # Basic validation: confidence must be above threshold
        if state.confidence < self.confidence_threshold:
            self.logger.debug(
                "State validation failed: low confidence",
                confidence=state.confidence,
                threshold=self.confidence_threshold,
            )
            return False

        return True

    def preprocess_image(
        self,
        image: np.ndarray | Image.Image,
        grayscale: bool = False,
        resize: Optional[tuple[int, int]] = None,
    ) -> np.ndarray:
        """
        Preprocess image before parsing.

        Args:
            image: Input image
            grayscale: Convert to grayscale
            resize: Resize to (width, height)

        Returns:
            Preprocessed numpy array
        """
        # Convert PIL to numpy
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Resize if requested
        if resize:
            import cv2
            image = cv2.resize(image, resize, interpolation=cv2.INTER_AREA)

        # Convert to grayscale if requested
        if grayscale and len(image.shape) == 3:
            import cv2
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        return image

    def extract_region(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> np.ndarray:
        """
        Extract a rectangular region from image.

        Args:
            image: Source image
            x, y: Top-left corner coordinates
            width, height: Region dimensions

        Returns:
            Extracted region as numpy array
        """
        # Clamp coordinates to image bounds
        h, w = image.shape[:2]
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        x2 = max(0, min(x + width, w))
        y2 = max(0, min(y + height, h))

        return image[y:y2, x:x2]

    def find_ui_element(
        self,
        image: np.ndarray,
        template_name: str,
        threshold: Optional[float] = None,
    ) -> Optional[tuple[int, int, int, int]]:
        """
        Find UI element using template matching.

        Args:
            image: Screenshot to search in
            template_name: Name of template to find
            threshold: Optional confidence threshold

        Returns:
            Bounding box (x, y, width, height) or None if not found
        """
        if not self.template_matcher:
            self.logger.warning("Template matcher not available")
            return None

        matches = self.template_matcher.match(
            image,
            template_name,
            threshold=threshold or self.confidence_threshold,
            single_best=True,
        )

        if matches:
            match = matches[0]
            self.logger.debug(
                "UI element found",
                template=template_name,
                confidence=match.confidence,
                position=(match.x, match.y),
            )
            return match.bbox

        return None

    def detect_color_region(
        self,
        image: np.ndarray,
        color_lower: tuple[int, int, int],
        color_upper: tuple[int, int, int],
        min_area: int = 100,
    ) -> list[tuple[int, int, int, int]]:
        """
        Detect regions by color using HSV color space.

        Args:
            image: Input image (RGB)
            color_lower: Lower HSV bound (H, S, V)
            color_upper: Upper HSV bound (H, S, V)
            min_area: Minimum area to consider

        Returns:
            List of bounding boxes (x, y, width, height)
        """
        import cv2

        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Create mask
        mask = cv2.inRange(hsv, np.array(color_lower), np.array(color_upper))

        # Find contours
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        # Filter and extract bounding boxes
        regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_area:
                x, y, w, h = cv2.boundingRect(contour)
                regions.append((x, y, w, h))

        return regions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(threshold={self.confidence_threshold})"
