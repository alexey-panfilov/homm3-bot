"""
Vision module for HoMM3 Bot.
Handles template matching, OCR, and game state parsing.
"""

from .template_matcher import TemplateMatcher, MatchResult
from .base_parser import BaseParser, GameScreen, GameState
from .ocr_utils import OCREngine, parse_resource_number, filter_non_numeric
from .screen_detector import ScreenDetector
from .turn_detector import TurnDetector, TurnInfo
from .parsers.resource_parser import ResourceParser, ResourceState
from .parsers.adventure_map_parser import (
    AdventureMapParser,
    AdventureMapState,
    Hero,
    Town,
    MapObject,
)

__all__ = [
    # Core
    'TemplateMatcher',
    'MatchResult',
    'BaseParser',
    'GameScreen',
    'GameState',
    # OCR
    'OCREngine',
    'parse_resource_number',
    'filter_non_numeric',
    # Detectors
    'ScreenDetector',
    'TurnDetector',
    'TurnInfo',
    # Parsers
    'ResourceParser',
    'ResourceState',
    'AdventureMapParser',
    'AdventureMapState',
    'Hero',
    'Town',
    'MapObject',
]
