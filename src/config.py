"""
Configuration management for the HoMM3 bot.
"""

import yaml
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class CaptureConfig:
    """Screen capture configuration."""
    fps: float = 2.0
    buffer_size: int = 10


@dataclass
class MouseConfig:
    """Mouse control configuration."""
    default_duration: float = 0.2
    click_delay: float = 0.1
    enable_verification: bool = True


@dataclass
class KeyboardConfig:
    """Keyboard control configuration."""
    default_delay: float = 0.1


@dataclass
class WindowConfig:
    """Window management configuration."""
    window_title: Optional[str] = None
    process_name: str = "heroes3.exe"
    auto_focus: bool = True


@dataclass
class AIConfig:
    """AI decision-making configuration."""
    strategy_profile: str = "balanced"
    decision_timeout: float = 5.0
    enable_ml: bool = False
    model_path: Optional[str] = None


@dataclass
class TurnConfig:
    """Turn detection configuration."""
    auto_detect: bool = True
    manual_hotkey: str = "F1"
    detection_interval: float = 0.5


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    log_dir: str = "data/logs"
    enable_file_logging: bool = True
    enable_structured: bool = True


@dataclass
class BotConfig:
    """Main bot configuration."""
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    mouse: MouseConfig = field(default_factory=MouseConfig)
    keyboard: KeyboardConfig = field(default_factory=KeyboardConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    turn: TurnConfig = field(default_factory=TurnConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, filepath: str | Path) -> 'BotConfig':
        """
        Load configuration from YAML file.

        Args:
            filepath: Path to YAML configuration file

        Returns:
            BotConfig instance
        """
        filepath = Path(filepath)

        if not filepath.exists():
            logger.warning(f"Config file not found: {filepath}, using defaults")
            return cls()

        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)

            if data is None:
                return cls()

            config = cls()

            # Load nested configs
            if 'capture' in data:
                config.capture = CaptureConfig(**data['capture'])
            if 'mouse' in data:
                config.mouse = MouseConfig(**data['mouse'])
            if 'keyboard' in data:
                config.keyboard = KeyboardConfig(**data['keyboard'])
            if 'window' in data:
                config.window = WindowConfig(**data['window'])
            if 'ai' in data:
                config.ai = AIConfig(**data['ai'])
            if 'turn' in data:
                config.turn = TurnConfig(**data['turn'])
            if 'logging' in data:
                config.logging = LoggingConfig(**data['logging'])

            logger.info(f"Configuration loaded from {filepath}")
            return config

        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            logger.warning("Using default configuration")
            return cls()

    def to_yaml(self, filepath: str | Path) -> bool:
        """
        Save configuration to YAML file.

        Args:
            filepath: Path where to save configuration

        Returns:
            True if successful, False otherwise
        """
        filepath = Path(filepath)

        try:
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict
            data = {
                'capture': {
                    'fps': self.capture.fps,
                    'buffer_size': self.capture.buffer_size
                },
                'mouse': {
                    'default_duration': self.mouse.default_duration,
                    'click_delay': self.mouse.click_delay,
                    'enable_verification': self.mouse.enable_verification
                },
                'keyboard': {
                    'default_delay': self.keyboard.default_delay
                },
                'window': {
                    'window_title': self.window.window_title,
                    'process_name': self.window.process_name,
                    'auto_focus': self.window.auto_focus
                },
                'ai': {
                    'strategy_profile': self.ai.strategy_profile,
                    'decision_timeout': self.ai.decision_timeout,
                    'enable_ml': self.ai.enable_ml,
                    'model_path': self.ai.model_path
                },
                'turn': {
                    'auto_detect': self.turn.auto_detect,
                    'manual_hotkey': self.turn.manual_hotkey,
                    'detection_interval': self.turn.detection_interval
                },
                'logging': {
                    'level': self.logging.level,
                    'log_dir': self.logging.log_dir,
                    'enable_file_logging': self.logging.enable_file_logging,
                    'enable_structured': self.logging.enable_structured
                }
            }

            with open(filepath, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Configuration saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving config: {e}", exc_info=True)
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., 'capture.fps')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        parts = key.split('.')
        value = self

        try:
            for part in parts:
                value = getattr(value, part)
            return value
        except AttributeError:
            return default
