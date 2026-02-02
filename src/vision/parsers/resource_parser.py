"""
Resource bar parser for extracting resource counts (gold, wood, ore, etc.)
"""

from dataclasses import dataclass
from typing import Optional, Dict
import numpy as np
from PIL import Image
import structlog

from ..base_parser import BaseParser, GameState, GameScreen
from ..ocr_utils import OCREngine, parse_resource_number

logger = structlog.get_logger(__name__)


@dataclass
class ResourceState(GameState):
    """Game state with resource information."""
    screen: GameScreen = GameScreen.ADVENTURE_MAP
    gold: int = 0
    wood: int = 0
    ore: int = 0
    mercury: int = 0
    sulfur: int = 0
    crystal: int = 0
    gems: int = 0

    def __repr__(self) -> str:
        return (f"ResourceState(gold={self.gold}, wood={self.wood}, "
                f"ore={self.ore}, mercury={self.mercury})")


class ResourceParser(BaseParser):
    """
    Parser for extracting resource counts from the UI.

    The resource bar is typically at the top-right of the adventure map screen.
    """

    # Resource bar coordinates (relative to 800x600 base resolution)
    # These will need to be adjusted based on actual HD Edition layout
    RESOURCE_BAR_REGIONS = {
        # Assuming 1366x768 resolution (HD Edition default)
        '1366x768': {
            'gold': (1180, 8, 90, 25),
            'wood': (1180, 35, 60, 25),
            'ore': (1250, 35, 60, 25),
            'mercury': (1180, 62, 60, 25),
            'sulfur': (1250, 62, 60, 25),
            'crystal': (1180, 89, 60, 25),
            'gems': (1250, 89, 60, 25),
        },
        # Fallback for other resolutions
        'default': {
            'gold': (-186, 8, 90, 25),  # Negative = from right edge
            'wood': (-186, 35, 60, 25),
            'ore': (-116, 35, 60, 25),
            'mercury': (-186, 62, 60, 25),
            'sulfur': (-116, 62, 60, 25),
            'crystal': (-186, 89, 60, 25),
            'gems': (-116, 89, 60, 25),
        },
    }

    def __init__(
        self,
        template_matcher=None,
        confidence_threshold: float = 0.75,
        tesseract_cmd: Optional[str] = None,
    ):
        """
        Initialize resource parser.

        Args:
            template_matcher: TemplateMatcher instance
            confidence_threshold: Minimum confidence threshold
            tesseract_cmd: Path to tesseract executable
        """
        super().__init__(template_matcher, confidence_threshold)
        self.ocr = OCREngine(tesseract_cmd)
        self.resolution = (1366, 768)  # Default, will be updated

    def can_parse(self, image: np.ndarray | Image.Image) -> float:
        """
        Check if resource bar is visible in image.

        Args:
            image: Screenshot to analyze

        Returns:
            Confidence score (0.0-1.0)
        """
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Update resolution
        self.resolution = (image.shape[1], image.shape[0])

        # Try to find resource icons
        if self.template_matcher:
            try:
                gold_icon = self.template_matcher.match(
                    image,
                    'resource_gold_icon',
                    threshold=0.7,
                    single_best=True,
                )
                if gold_icon:
                    return gold_icon[0].confidence
            except:
                pass

        # Fallback: check if top-right region has appropriate colors
        # Resource bar typically has dark background with yellow/white text
        h, w = image.shape[:2]
        top_right = image[:120, w-250:]

        # Check for dark background (resource bar has dark UI)
        mean_brightness = np.mean(top_right)
        if mean_brightness < 80:  # Dark region
            return 0.6  # Moderate confidence

        return 0.3

    def parse(self, image: np.ndarray | Image.Image) -> ResourceState:
        """
        Parse resource counts from image.

        Args:
            image: Screenshot to analyze

        Returns:
            ResourceState with extracted resource counts
        """
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Update resolution
        self.resolution = (image.shape[1], image.shape[0])

        state = ResourceState()
        state.raw_image = image

        # Get appropriate region definitions
        regions = self._get_regions_for_resolution()

        # Extract each resource
        resources = ['gold', 'wood', 'ore', 'mercury', 'sulfur', 'crystal', 'gems']

        for resource in resources:
            if resource not in regions:
                continue

            region_coords = regions[resource]
            value = self._extract_resource_value(image, region_coords)

            if value is not None:
                setattr(state, resource, value)

        # Calculate confidence based on successful extractions
        extracted_count = sum(
            1 for r in resources if getattr(state, r, 0) > 0
        )
        state.confidence = extracted_count / len(resources)

        self.logger.debug(
            "Resources parsed",
            confidence=state.confidence,
            gold=state.gold,
            wood=state.wood,
            ore=state.ore,
        )

        return state

    def _get_regions_for_resolution(self) -> Dict[str, tuple]:
        """
        Get resource bar regions for current resolution.

        Returns:
            Dictionary of resource regions
        """
        res_key = f"{self.resolution[0]}x{self.resolution[1]}"

        if res_key in self.RESOURCE_BAR_REGIONS:
            return self.RESOURCE_BAR_REGIONS[res_key]

        # Use default with adjustments for resolution
        default_regions = self.RESOURCE_BAR_REGIONS['default']
        adjusted_regions = {}

        for resource, (x, y, w, h) in default_regions.items():
            # Handle negative coordinates (from right edge)
            if x < 0:
                x = self.resolution[0] + x

            adjusted_regions[resource] = (x, y, w, h)

        return adjusted_regions

    def _extract_resource_value(
        self,
        image: np.ndarray,
        region: tuple[int, int, int, int],
    ) -> Optional[int]:
        """
        Extract resource value from a specific region.

        Args:
            image: Full screenshot
            region: (x, y, width, height) of resource number

        Returns:
            Extracted number or None
        """
        x, y, w, h = region

        # Extract region
        region_img = self.extract_region(image, x, y, w, h)

        if region_img.size == 0:
            return None

        # Use OCR to extract number
        value = self.ocr.extract_single_number(region_img, preprocess=True)

        return value if value > 0 else None

    def get_resource(self, resource_name: str, image: np.ndarray) -> Optional[int]:
        """
        Get a single resource value.

        Args:
            resource_name: Name of resource ('gold', 'wood', etc.)
            image: Screenshot

        Returns:
            Resource value or None
        """
        state = self.parse(image)
        return getattr(state, resource_name, None)

    def has_sufficient_resources(
        self,
        required: Dict[str, int],
        image: np.ndarray,
    ) -> bool:
        """
        Check if player has sufficient resources for a purchase.

        Args:
            required: Dictionary of required resources
            image: Screenshot

        Returns:
            True if all resources are sufficient
        """
        state = self.parse(image)

        for resource, amount in required.items():
            current = getattr(state, resource, 0)
            if current < amount:
                self.logger.debug(
                    "Insufficient resources",
                    resource=resource,
                    required=amount,
                    current=current,
                )
                return False

        return True

    def monitor_resource_change(
        self,
        before_image: np.ndarray,
        after_image: np.ndarray,
    ) -> Dict[str, int]:
        """
        Monitor resource changes between two screenshots.

        Args:
            before_image: Screenshot before action
            after_image: Screenshot after action

        Returns:
            Dictionary of resource changes (positive = gained, negative = spent)
        """
        before_state = self.parse(before_image)
        after_state = self.parse(after_image)

        changes = {}
        resources = ['gold', 'wood', 'ore', 'mercury', 'sulfur', 'crystal', 'gems']

        for resource in resources:
            before_val = getattr(before_state, resource, 0)
            after_val = getattr(after_state, resource, 0)
            change = after_val - before_val

            if change != 0:
                changes[resource] = change

        return changes
