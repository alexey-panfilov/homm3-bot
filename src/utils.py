"""
Utility functions and logging setup.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import structlog
from colorama import init as colorama_init, Fore, Style

# Initialize colorama for Windows
colorama_init()


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_structured: bool = True
) -> None:
    """
    Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_structured: Enable structured logging with structlog
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

    file_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(console_handler)

    # Setup file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Configure structlog if enabled
    if enable_structured:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    logging.info(f"Logging initialized (level: {log_level})")


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        """Format log record with colors."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        return super().format(record)


def create_timestamped_filename(prefix: str, extension: str = "log") -> str:
    """
    Create a timestamped filename.

    Args:
        prefix: Filename prefix
        extension: File extension (without dot)

    Returns:
        Timestamped filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def ensure_dir(path: str | Path) -> Path:
    """
    Ensure directory exists, create if it doesn't.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


class PerformanceTimer:
    """Context manager for timing code execution."""

    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize timer.

        Args:
            name: Name of the operation being timed
            logger: Logger to use (uses root logger if None)
        """
        self.name = name
        self.logger = logger or logging.getLogger()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self):
        """Start timing."""
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and log result."""
        import time
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        self.logger.debug(f"{self.name} took {elapsed:.3f}s")

    @property
    def elapsed(self) -> Optional[float]:
        """Get elapsed time."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
