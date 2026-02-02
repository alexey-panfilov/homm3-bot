"""
HoMM3 Bot - Main Entry Point

A gaming bot for Heroes of Might and Magic 3 that uses computer vision
and machine learning to play the game autonomously.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from config import BotConfig
from utils import setup_logging, create_timestamped_filename
from capture.screen import ScreenCapture
from capture.window import WindowManager
from actions.executor import ActionExecutor

logger = logging.getLogger(__name__)


class HoMM3Bot:
    """Main bot controller."""

    def __init__(self, config: BotConfig):
        """
        Initialize the bot.

        Args:
            config: Bot configuration
        """
        self.config = config
        self.running = False

        # Initialize components
        self.window_manager = WindowManager()
        self.screen_capture = ScreenCapture(target_fps=config.capture.fps)
        self.action_executor = ActionExecutor()

        logger.info("HoMM3Bot initialized")

    def setup(self) -> bool:
        """
        Setup the bot (find window, configure screen capture, etc.).

        Returns:
            True if setup successful, False otherwise
        """
        logger.info("Setting up bot...")

        # Find game window
        if self.config.window.window_title:
            found = self.window_manager.find_game_window(self.config.window.window_title)
        else:
            # Try by process name first
            found = self.window_manager.find_window_by_process_name(self.config.window.process_name)
            if not found:
                # Fallback to title search
                found = self.window_manager.find_game_window()

        if not found:
            logger.error("Could not find game window")
            return False

        # Get window bounds
        bounds = self.window_manager.get_client_bounds()
        if bounds is None:
            logger.error("Could not get window bounds")
            return False

        x, y, width, height = bounds
        logger.info(f"Game window found: {width}x{height} at ({x}, {y})")

        # Configure screen capture
        self.screen_capture.set_capture_region(x, y, width, height)

        # Configure mouse safety bounds
        self.action_executor.mouse.set_allowed_bounds(x, y, width, height)

        # Focus window if configured
        if self.config.window.auto_focus:
            self.window_manager.focus_window()

        logger.info("Bot setup complete")
        return True

    def run_demo(self) -> None:
        """Run a simple demo to test the bot components."""
        logger.info("Running demo mode...")

        # Capture screenshot
        logger.info("Capturing screenshot...")
        screenshot = self.screen_capture.capture()

        if screenshot is not None:
            logger.info(f"Screenshot captured: {screenshot.shape}")

            # Save demo screenshot
            demo_file = Path("data/logs/demo_screenshot.png")
            demo_file.parent.mkdir(parents=True, exist_ok=True)

            if self.screen_capture.save_screenshot(str(demo_file)):
                logger.info(f"Demo screenshot saved to: {demo_file}")
        else:
            logger.error("Failed to capture screenshot")

        # Display window info
        info = self.window_manager.get_window_info()
        logger.info(f"Window info: {info}")

        # Test mouse movement (move to center of window)
        bounds = self.window_manager.get_client_bounds()
        if bounds:
            x, y, w, h = bounds
            center_x = x + w // 2
            center_y = y + h // 2

            logger.info(f"Moving mouse to window center: ({center_x}, {center_y})")
            self.action_executor.mouse.move_to(center_x, center_y)

        logger.info("Demo complete")

    def start(self) -> None:
        """Start the bot."""
        if not self.setup():
            logger.error("Bot setup failed, cannot start")
            return

        self.running = True
        logger.info("Bot started (demo mode)")

        try:
            self.run_demo()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error during bot execution: {e}", exc_info=True)
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the bot."""
        self.running = False
        logger.info("Bot stopped")

        # Display statistics
        stats = self.action_executor.get_stats()
        logger.info(f"Action statistics: {stats}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='HoMM3 Bot - Autonomous gaming bot for Heroes of Might and Magic 3'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Override logging level'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode (test components)'
    )

    args = parser.parse_args()

    # Load configuration
    config = BotConfig.from_yaml(args.config)

    # Override log level if specified
    if args.log_level:
        config.logging.level = args.log_level

    # Setup logging
    log_file = None
    if config.logging.enable_file_logging:
        log_dir = Path(config.logging.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_filename = create_timestamped_filename('homm3_bot', 'log')
        log_file = str(log_dir / log_filename)

    setup_logging(
        log_level=config.logging.level,
        log_file=log_file,
        enable_structured=config.logging.enable_structured
    )

    logger.info("=" * 60)
    logger.info("HoMM3 Bot - Starting")
    logger.info("=" * 60)
    logger.info(f"Configuration: {args.config}")
    logger.info(f"Log level: {config.logging.level}")
    if log_file:
        logger.info(f"Log file: {log_file}")

    # Create and run bot
    try:
        bot = HoMM3Bot(config)
        bot.start()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
