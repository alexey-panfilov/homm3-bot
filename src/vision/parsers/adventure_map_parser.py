"""
Adventure map parser for detecting and tracking heroes, towns, and map objects.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
import numpy as np
from PIL import Image
import structlog

from ..base_parser import BaseParser, GameState, GameScreen
from ..template_matcher import MatchResult

logger = structlog.get_logger(__name__)


@dataclass
class Hero:
    """Information about a hero on the adventure map."""
    position: Tuple[int, int]  # (x, y) pixel coordinates
    is_selected: bool = False
    can_move: bool = True
    name: Optional[str] = None
    confidence: float = 0.0


@dataclass
class Town:
    """Information about a town on the adventure map."""
    position: Tuple[int, int]
    is_owned: bool = False
    name: Optional[str] = None
    confidence: float = 0.0


@dataclass
class MapObject:
    """Generic map object (resource pile, artifact, monster, etc.)"""
    position: Tuple[int, int]
    object_type: str = "unknown"
    confidence: float = 0.0


@dataclass
class AdventureMapState(GameState):
    """Complete adventure map state."""
    screen: GameScreen = GameScreen.ADVENTURE_MAP
    heroes: List[Hero] = field(default_factory=list)
    towns: List[Town] = field(default_factory=list)
    objects: List[MapObject] = field(default_factory=list)
    selected_hero: Optional[Hero] = None
    map_center: Tuple[int, int] = (0, 0)
    is_player_turn: bool = False

    def __repr__(self) -> str:
        return (f"AdventureMapState(heroes={len(self.heroes)}, "
                f"towns={len(self.towns)}, "
                f"selected={self.selected_hero is not None})")


class AdventureMapParser(BaseParser):
    """
    Parser for adventure map screen.

    Extracts hero positions, town locations, and map objects.
    """

    # Map viewport area (excluding UI) - adjust for HD Edition
    MAP_VIEWPORT = {
        '1366x768': (0, 0, 1366, 648),  # Full screen minus bottom UI
        'default': (0, 0, -1, -120),     # -1 = full width, -120 = bottom UI
    }

    def __init__(
        self,
        template_matcher=None,
        confidence_threshold: float = 0.75,
    ):
        """
        Initialize adventure map parser.

        Args:
            template_matcher: TemplateMatcher instance
            confidence_threshold: Minimum confidence threshold
        """
        super().__init__(template_matcher, confidence_threshold)

        # Load hero and town templates when available
        self.hero_templates = [
            'hero_marker',
            'hero_selected',
            'hero_blue',
            'hero_red',
        ]

        self.town_templates = [
            'town_castle',
            'town_rampart',
            'town_tower',
            'town_inferno',
            'town_owned',
            'town_enemy',
        ]

    def can_parse(self, image: np.ndarray | Image.Image) -> float:
        """
        Check if this is the adventure map screen.

        Args:
            image: Screenshot to analyze

        Returns:
            Confidence score (0.0-1.0)
        """
        if isinstance(image, Image.Image):
            image = np.array(image)

        confidence = 0.0

        if not self.template_matcher:
            # Fallback: check for map-like features
            # Adventure map has lots of green (grass) and varied colors
            import cv2
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hist_h = hist_h.flatten() / hist_h.sum()

            # Green terrain (hue 35-85 for grass)
            green_amount = np.sum(hist_h[35:85])
            if green_amount > 0.2:
                confidence = 0.6
        else:
            # Look for adventure map UI elements
            ui_elements = [
                'end_turn_button',
                'kingdom_overview_button',
                'minimap',
            ]

            matches_found = 0
            total_confidence = 0.0

            for template_name in ui_elements:
                try:
                    matches = self.template_matcher.match(
                        image,
                        template_name,
                        threshold=0.6,
                        single_best=True,
                    )
                    if matches:
                        matches_found += 1
                        total_confidence += matches[0].confidence
                except:
                    pass

            if matches_found > 0:
                confidence = total_confidence / len(ui_elements)

        return confidence

    def parse(self, image: np.ndarray | Image.Image) -> AdventureMapState:
        """
        Parse adventure map state from image.

        Args:
            image: Screenshot to analyze

        Returns:
            AdventureMapState with detected objects
        """
        if isinstance(image, Image.Image):
            image = np.array(image)

        state = AdventureMapState()
        state.raw_image = image

        # Extract map viewport
        viewport = self._get_map_viewport(image)

        # Detect heroes
        state.heroes = self._detect_heroes(viewport)

        # Detect towns
        state.towns = self._detect_towns(viewport)

        # Detect selected hero
        state.selected_hero = self._find_selected_hero(state.heroes)

        # Calculate confidence
        if state.heroes or state.towns:
            state.confidence = 0.8
        else:
            state.confidence = 0.4

        self.logger.debug(
            "Adventure map parsed",
            heroes=len(state.heroes),
            towns=len(state.towns),
            selected=state.selected_hero is not None,
        )

        return state

    def _get_map_viewport(self, image: np.ndarray) -> np.ndarray:
        """
        Extract the map viewport (excluding UI panels).

        Args:
            image: Full screenshot

        Returns:
            Map viewport region
        """
        h, w = image.shape[:2]
        res_key = f"{w}x{h}"

        if res_key in self.MAP_VIEWPORT:
            x1, y1, x2, y2 = self.MAP_VIEWPORT[res_key]
        else:
            x1, y1, x2, y2 = self.MAP_VIEWPORT['default']

        # Handle negative coordinates
        if x2 < 0:
            x2 = w + x2
        elif x2 == -1:
            x2 = w

        if y2 < 0:
            y2 = h + y2
        elif y2 == -1:
            y2 = h

        return image[y1:y2, x1:x2]

    def _detect_heroes(self, viewport: np.ndarray) -> List[Hero]:
        """
        Detect heroes on the map.

        Args:
            viewport: Map viewport image

        Returns:
            List of detected heroes
        """
        heroes = []

        if not self.template_matcher:
            return heroes

        # Try each hero template
        for template_name in self.hero_templates:
            try:
                matches = self.template_matcher.match(
                    viewport,
                    template_name,
                    threshold=0.7,
                    single_best=False,
                )

                for match in matches:
                    hero = Hero(
                        position=match.center,
                        is_selected='selected' in template_name.lower(),
                        confidence=match.confidence,
                    )
                    heroes.append(hero)
            except Exception as e:
                self.logger.debug(
                    "Hero template matching failed",
                    template=template_name,
                    error=str(e),
                )

        return heroes

    def _detect_towns(self, viewport: np.ndarray) -> List[Town]:
        """
        Detect towns on the map.

        Args:
            viewport: Map viewport image

        Returns:
            List of detected towns
        """
        towns = []

        if not self.template_matcher:
            return towns

        # Try each town template
        for template_name in self.town_templates:
            try:
                matches = self.template_matcher.match(
                    viewport,
                    template_name,
                    threshold=0.7,
                    single_best=False,
                )

                for match in matches:
                    town = Town(
                        position=match.center,
                        is_owned='owned' in template_name.lower(),
                        confidence=match.confidence,
                    )
                    towns.append(town)
            except Exception as e:
                self.logger.debug(
                    "Town template matching failed",
                    template=template_name,
                    error=str(e),
                )

        return towns

    def _find_selected_hero(self, heroes: List[Hero]) -> Optional[Hero]:
        """
        Find the currently selected hero.

        Args:
            heroes: List of detected heroes

        Returns:
            Selected hero or None
        """
        for hero in heroes:
            if hero.is_selected:
                return hero
        return None

    def get_hero_at_position(
        self,
        state: AdventureMapState,
        x: int,
        y: int,
        tolerance: int = 50,
    ) -> Optional[Hero]:
        """
        Find hero near a specific position.

        Args:
            state: Adventure map state
            x, y: Position to check
            tolerance: Distance tolerance in pixels

        Returns:
            Hero near position or None
        """
        for hero in state.heroes:
            hx, hy = hero.position
            distance = np.sqrt((hx - x) ** 2 + (hy - y) ** 2)
            if distance <= tolerance:
                return hero
        return None

    def get_nearest_hero(
        self,
        state: AdventureMapState,
        x: int,
        y: int,
    ) -> Optional[Hero]:
        """
        Find nearest hero to a position.

        Args:
            state: Adventure map state
            x, y: Position

        Returns:
            Nearest hero or None
        """
        if not state.heroes:
            return None

        nearest = None
        min_distance = float('inf')

        for hero in state.heroes:
            hx, hy = hero.position
            distance = np.sqrt((hx - x) ** 2 + (hy - y) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest = hero

        return nearest

    def get_nearest_town(
        self,
        state: AdventureMapState,
        x: int,
        y: int,
    ) -> Optional[Town]:
        """
        Find nearest town to a position.

        Args:
            state: Adventure map state
            x, y: Position

        Returns:
            Nearest town or None
        """
        if not state.towns:
            return None

        nearest = None
        min_distance = float('inf')

        for town in state.towns:
            tx, ty = town.position
            distance = np.sqrt((tx - x) ** 2 + (ty - y) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest = town

        return nearest
