"""
Vision module for HoMM3 Bot.
Handles template matching, OCR, and game state parsing.
"""

from .template_matcher import TemplateMatcher, MatchResult
from .base_parser import BaseParser, GameScreen, GameState

__all__ = [
    'TemplateMatcher',
    'MatchResult',
    'BaseParser',
    'GameScreen',
    'GameState',
]
