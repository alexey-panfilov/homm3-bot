"""
OCR utilities for text extraction from game UI.
Uses Tesseract OCR with preprocessing for better accuracy.
"""

from typing import Optional, List, Tuple
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import pytesseract
import structlog

logger = structlog.get_logger(__name__)


class OCREngine:
    """
    Optical Character Recognition engine for game text extraction.

    Handles preprocessing, text extraction, and result validation.
    """

    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        lang: str = 'eng',
    ):
        """
        Initialize OCR engine.

        Args:
            tesseract_cmd: Path to tesseract executable (auto-detect if None)
            lang: Language for OCR (default: 'eng')
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        self.lang = lang

        # Test OCR availability
        try:
            version = pytesseract.get_tesseract_version()
            logger.info("OCR engine initialized", version=str(version), lang=lang)
        except Exception as e:
            logger.warning("Tesseract OCR not available", error=str(e))

    def extract_text(
        self,
        image: np.ndarray | Image.Image,
        preprocess: bool = True,
        config: str = '',
    ) -> str:
        """
        Extract text from image.

        Args:
            image: Input image
            preprocess: Apply preprocessing for better accuracy
            config: Custom Tesseract configuration

        Returns:
            Extracted text string
        """
        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Preprocess if requested
        if preprocess:
            image = self.preprocess_for_ocr(image)

        # Extract text
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=config,
            )
            return text.strip()
        except Exception as e:
            logger.warning("OCR extraction failed", error=str(e))
            return ""

    def extract_numbers(
        self,
        image: np.ndarray | Image.Image,
        preprocess: bool = True,
    ) -> List[int]:
        """
        Extract numbers from image (useful for resource counts).

        Args:
            image: Input image
            preprocess: Apply preprocessing

        Returns:
            List of extracted numbers
        """
        # Use digits-only configuration
        config = '--psm 7 -c tessedit_char_whitelist=0123456789'
        text = self.extract_text(image, preprocess, config)

        # Extract all numbers
        numbers = []
        current_num = ""
        for char in text:
            if char.isdigit():
                current_num += char
            elif current_num:
                numbers.append(int(current_num))
                current_num = ""

        if current_num:
            numbers.append(int(current_num))

        return numbers

    def extract_single_number(
        self,
        image: np.ndarray | Image.Image,
        preprocess: bool = True,
        default: int = 0,
    ) -> int:
        """
        Extract a single number from image.

        Args:
            image: Input image
            preprocess: Apply preprocessing
            default: Default value if extraction fails

        Returns:
            Extracted number or default
        """
        numbers = self.extract_numbers(image, preprocess)
        return numbers[0] if numbers else default

    def preprocess_for_ocr(
        self,
        image: np.ndarray,
        method: str = 'adaptive',
    ) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.

        Args:
            image: Input image
            method: Preprocessing method ('adaptive', 'threshold', 'denoise')

        Returns:
            Preprocessed image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()

        if method == 'adaptive':
            # Adaptive thresholding (best for varying lighting)
            processed = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2,
            )
        elif method == 'threshold':
            # Simple thresholding
            _, processed = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            )
        elif method == 'denoise':
            # Denoise then threshold
            denoised = cv2.fastNlMeansDenoising(gray)
            _, processed = cv2.threshold(
                denoised,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            )
        else:
            processed = gray

        # Resize for better OCR (Tesseract works best with ~300 DPI)
        scale = 2.0
        if scale != 1.0:
            new_width = int(processed.shape[1] * scale)
            new_height = int(processed.shape[0] * scale)
            processed = cv2.resize(
                processed,
                (new_width, new_height),
                interpolation=cv2.INTER_CUBIC,
            )

        return processed

    def extract_text_from_region(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        preprocess: bool = True,
    ) -> str:
        """
        Extract text from a specific region of the image.

        Args:
            image: Source image
            x, y: Top-left corner
            width, height: Region size
            preprocess: Apply preprocessing

        Returns:
            Extracted text
        """
        # Extract region
        h, w = image.shape[:2]
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        x2 = min(x + width, w)
        y2 = min(y + height, h)

        region = image[y:y2, x:x2]

        return self.extract_text(region, preprocess)

    def find_text_positions(
        self,
        image: np.ndarray | Image.Image,
        target_text: str,
    ) -> List[Tuple[int, int, int, int]]:
        """
        Find positions of specific text in image.

        Args:
            image: Input image
            target_text: Text to find

        Returns:
            List of bounding boxes (x, y, width, height)
        """
        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Get detailed OCR data
        try:
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                output_type=pytesseract.Output.DICT,
            )
        except Exception as e:
            logger.warning("OCR data extraction failed", error=str(e))
            return []

        positions = []
        target_lower = target_text.lower()

        # Search through detected text
        for i, text in enumerate(data['text']):
            if text and target_lower in text.lower():
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                positions.append((x, y, w, h))

        return positions


def parse_resource_number(text: str) -> Optional[int]:
    """
    Parse resource number from OCR text.
    Handles various formats: "1234", "1,234", "1.234", etc.

    Args:
        text: Text containing number

    Returns:
        Parsed number or None if invalid
    """
    if not text:
        return None

    # Remove non-digit characters except for k/K (thousands)
    cleaned = ''.join(c for c in text if c.isdigit() or c.lower() == 'k')

    if not cleaned:
        return None

    try:
        # Handle 'k' suffix for thousands
        if cleaned.lower().endswith('k'):
            num = int(cleaned[:-1]) * 1000
        else:
            num = int(cleaned)
        return num
    except ValueError:
        return None


def filter_non_numeric(text: str) -> str:
    """
    Filter out non-numeric characters from text.

    Args:
        text: Input text

    Returns:
        Text with only digits
    """
    return ''.join(c for c in text if c.isdigit())
