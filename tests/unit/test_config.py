"""
Unit tests for configuration module.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from config import BotConfig, CaptureConfig, MouseConfig, AIConfig


class TestBotConfig:
    """Test BotConfig class."""

    def test_default_config(self):
        """Test creating default configuration."""
        config = BotConfig()

        assert config.capture.fps == 2.0
        assert config.mouse.default_duration == 0.2
        assert config.ai.strategy_profile == "balanced"
        assert config.logging.level == "INFO"

    def test_from_yaml_nonexistent(self):
        """Test loading from non-existent file uses defaults."""
        config = BotConfig.from_yaml("nonexistent.yaml")

        assert config.capture.fps == 2.0
        assert config.mouse.default_duration == 0.2

    def test_from_yaml_valid(self):
        """Test loading from valid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_data = {
                'capture': {'fps': 5.0, 'buffer_size': 20},
                'mouse': {'default_duration': 0.5},
                'ai': {'strategy_profile': 'aggressive'}
            }
            yaml.dump(yaml_data, f)
            temp_path = f.name

        try:
            config = BotConfig.from_yaml(temp_path)

            assert config.capture.fps == 5.0
            assert config.capture.buffer_size == 20
            assert config.mouse.default_duration == 0.5
            assert config.ai.strategy_profile == 'aggressive'
        finally:
            Path(temp_path).unlink()

    def test_to_yaml(self):
        """Test saving configuration to YAML."""
        config = BotConfig()
        config.capture.fps = 3.0
        config.ai.strategy_profile = 'defensive'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            success = config.to_yaml(temp_path)
            assert success

            # Load and verify
            loaded_config = BotConfig.from_yaml(temp_path)
            assert loaded_config.capture.fps == 3.0
            assert loaded_config.ai.strategy_profile == 'defensive'
        finally:
            Path(temp_path).unlink()

    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        config = BotConfig()

        assert config.get('capture.fps') == 2.0
        assert config.get('mouse.default_duration') == 0.2
        assert config.get('nonexistent.key', 'default') == 'default'


class TestCaptureConfig:
    """Test CaptureConfig class."""

    def test_default_values(self):
        """Test default capture configuration."""
        config = CaptureConfig()

        assert config.fps == 2.0
        assert config.buffer_size == 10

    def test_custom_values(self):
        """Test custom capture configuration."""
        config = CaptureConfig(fps=5.0, buffer_size=20)

        assert config.fps == 5.0
        assert config.buffer_size == 20


class TestMouseConfig:
    """Test MouseConfig class."""

    def test_default_values(self):
        """Test default mouse configuration."""
        config = MouseConfig()

        assert config.default_duration == 0.2
        assert config.click_delay == 0.1
        assert config.enable_verification is True


class TestAIConfig:
    """Test AIConfig class."""

    def test_default_values(self):
        """Test default AI configuration."""
        config = AIConfig()

        assert config.strategy_profile == "balanced"
        assert config.decision_timeout == 5.0
        assert config.enable_ml is False
        assert config.model_path is None
