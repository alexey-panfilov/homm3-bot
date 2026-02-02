"""
Unit tests for screen capture module.
"""

import pytest
import numpy as np
from PIL import Image
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from capture.screen import ScreenCapture, FrameBuffer


class TestScreenCapture:
    """Test ScreenCapture class."""

    def test_initialization(self):
        """Test screen capture initialization."""
        capture = ScreenCapture(target_fps=2.0)

        assert capture.target_fps == 2.0
        assert capture.frame_interval == 0.5
        assert capture._monitor_bounds is None

    def test_set_capture_region(self):
        """Test setting capture region."""
        capture = ScreenCapture()
        capture.set_capture_region(100, 100, 800, 600)

        assert capture._monitor_bounds == {
            'top': 100,
            'left': 100,
            'width': 800,
            'height': 600
        }

    def test_get_monitor_info(self):
        """Test getting monitor information."""
        capture = ScreenCapture()
        monitors = capture.get_monitor_info()

        assert isinstance(monitors, list)
        assert len(monitors) >= 1  # At least one monitor

    def test_capture_full_screen_numpy(self):
        """Test full screen capture as numpy array."""
        capture = ScreenCapture()
        screenshot = capture.capture_full_screen(monitor_num=1, as_numpy=True)

        if screenshot is not None:
            assert isinstance(screenshot, np.ndarray)
            assert len(screenshot.shape) == 3  # Height x Width x Channels
            assert screenshot.shape[2] == 3  # RGB

    def test_capture_full_screen_pil(self):
        """Test full screen capture as PIL Image."""
        capture = ScreenCapture()
        screenshot = capture.capture_full_screen(monitor_num=1, as_numpy=False)

        if screenshot is not None:
            assert isinstance(screenshot, Image.Image)
            assert screenshot.mode == 'RGB'


class TestFrameBuffer:
    """Test FrameBuffer class."""

    def test_initialization(self):
        """Test frame buffer initialization."""
        buffer = FrameBuffer(max_frames=5)

        assert buffer.max_frames == 5
        assert len(buffer) == 0

    def test_add_frame(self):
        """Test adding frames to buffer."""
        buffer = FrameBuffer(max_frames=3)
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8)

        buffer.add_frame(frame1)
        assert len(buffer) == 1

        buffer.add_frame(frame2)
        assert len(buffer) == 2

    def test_buffer_overflow(self):
        """Test buffer removes oldest frames when full."""
        buffer = FrameBuffer(max_frames=2)
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8)
        frame3 = np.full((100, 100, 3), 128, dtype=np.uint8)

        buffer.add_frame(frame1)
        buffer.add_frame(frame2)
        buffer.add_frame(frame3)

        assert len(buffer) == 2
        # First frame should be removed
        assert np.array_equal(buffer.get_frame(0), frame2)
        assert np.array_equal(buffer.get_frame(1), frame3)

    def test_get_latest_frame(self):
        """Test getting the latest frame."""
        buffer = FrameBuffer()
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8)

        assert buffer.get_latest_frame() is None

        buffer.add_frame(frame1)
        assert np.array_equal(buffer.get_latest_frame(), frame1)

        buffer.add_frame(frame2)
        assert np.array_equal(buffer.get_latest_frame(), frame2)

    def test_get_frame_by_index(self):
        """Test getting frame by index."""
        buffer = FrameBuffer()
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8)

        buffer.add_frame(frame1)
        buffer.add_frame(frame2)

        assert np.array_equal(buffer.get_frame(0), frame1)
        assert np.array_equal(buffer.get_frame(1), frame2)
        assert np.array_equal(buffer.get_frame(-1), frame2)
        assert buffer.get_frame(10) is None

    def test_clear(self):
        """Test clearing the buffer."""
        buffer = FrameBuffer()
        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        buffer.add_frame(frame)
        assert len(buffer) == 1

        buffer.clear()
        assert len(buffer) == 0
        assert buffer.get_latest_frame() is None

    def test_get_all_frames(self):
        """Test getting all frames."""
        buffer = FrameBuffer()
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8)

        buffer.add_frame(frame1)
        buffer.add_frame(frame2)

        frames = buffer.get_all_frames()
        assert len(frames) == 2
        assert np.array_equal(frames[0], frame1)
        assert np.array_equal(frames[1], frame2)
