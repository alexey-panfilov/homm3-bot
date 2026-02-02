"""
Template matching engine for detecting UI elements and game objects.
Uses OpenCV's template matching with multiple scales and methods.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class MatchResult:
    """Result of a template match operation."""
    template_name: str
    confidence: float
    x: int  # Top-left corner X
    y: int  # Top-left corner Y
    width: int
    height: int
    method: str
    scale: float = 1.0

    @property
    def center(self) -> Tuple[int, int]:
        """Get center point of the match."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        """Get bounding box (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def __repr__(self) -> str:
        return (f"MatchResult(template={self.template_name}, "
                f"confidence={self.confidence:.3f}, "
                f"pos=({self.x}, {self.y}), "
                f"size=({self.width}x{self.height}))")


class TemplateMatcher:
    """
    Advanced template matching with multi-scale search.

    Supports various OpenCV matching methods and can handle
    templates at different scales for resolution independence.
    """

    # OpenCV template matching methods
    METHODS = {
        'TM_CCOEFF_NORMED': cv2.TM_CCOEFF_NORMED,  # Best for most cases
        'TM_CCORR_NORMED': cv2.TM_CCORR_NORMED,
        'TM_SQDIFF_NORMED': cv2.TM_SQDIFF_NORMED,
    }

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        method: str = 'TM_CCOEFF_NORMED',
        threshold: float = 0.8,
        scales: Optional[List[float]] = None,
    ):
        """
        Initialize template matcher.

        Args:
            template_dir: Directory containing template images
            method: OpenCV matching method name
            threshold: Minimum confidence threshold (0.0-1.0)
            scales: List of scales to try (default: [0.8, 0.9, 1.0, 1.1, 1.2])
        """
        self.template_dir = template_dir
        self.method_name = method
        self.method = self.METHODS[method]
        self.threshold = threshold
        self.scales = scales or [0.8, 0.9, 1.0, 1.1, 1.2]

        # Template cache: {template_name: {scale: numpy_array}}
        self.template_cache: dict[str, dict[float, np.ndarray]] = {}

        logger.info(
            "Template matcher initialized",
            method=method,
            threshold=threshold,
            scales=len(self.scales),
        )

    def load_template(
        self,
        template_path: Path | str,
        name: Optional[str] = None,
    ) -> None:
        """
        Load a template image and cache it at all scales.

        Args:
            template_path: Path to template image file
            name: Optional name for template (defaults to filename)
        """
        template_path = Path(template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        template_name = name or template_path.stem

        # Load template in grayscale
        template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise ValueError(f"Failed to load template: {template_path}")

        # Cache at all scales
        self.template_cache[template_name] = {}
        for scale in self.scales:
            if scale == 1.0:
                scaled = template
            else:
                new_width = int(template.shape[1] * scale)
                new_height = int(template.shape[0] * scale)
                scaled = cv2.resize(
                    template,
                    (new_width, new_height),
                    interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
                )
            self.template_cache[template_name][scale] = scaled

        logger.debug(
            "Template loaded",
            name=template_name,
            path=str(template_path),
            size=template.shape,
            scales=len(self.scales),
        )

    def load_templates_from_dir(
        self,
        directory: Path | str,
        pattern: str = "*.png",
    ) -> int:
        """
        Load all templates matching pattern from directory.

        Args:
            directory: Directory containing templates
            pattern: Glob pattern for template files

        Returns:
            Number of templates loaded
        """
        directory = Path(directory)
        if not directory.exists():
            logger.debug("Template directory not found (will be created when templates added)", path=str(directory))
            return 0

        count = 0
        for template_file in directory.glob(pattern):
            try:
                self.load_template(template_file)
                count += 1
            except Exception as e:
                logger.warning(
                    "Failed to load template",
                    file=template_file.name,
                    error=str(e),
                )

        logger.info(
            "Templates loaded from directory",
            directory=str(directory),
            count=count,
        )
        return count

    def match(
        self,
        image: np.ndarray | Image.Image,
        template_name: str,
        threshold: Optional[float] = None,
        single_best: bool = True,
    ) -> List[MatchResult]:
        """
        Find template in image at multiple scales.

        Args:
            image: Input image (numpy array or PIL Image)
            template_name: Name of cached template
            threshold: Override default threshold
            single_best: Return only the best match

        Returns:
            List of MatchResult objects
        """
        # Convert PIL Image to numpy if needed
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            image_gray = image

        if template_name not in self.template_cache:
            logger.debug("Template not loaded (expected if not yet created)", name=template_name)
            return []

        threshold = threshold or self.threshold
        matches = []

        # Try all scales
        for scale, template in self.template_cache[template_name].items():
            # Template must be smaller than image
            if (template.shape[0] > image_gray.shape[0] or
                template.shape[1] > image_gray.shape[1]):
                continue

            # Perform template matching
            result = cv2.matchTemplate(image_gray, template, self.method)

            # Find locations above threshold
            if self.method == cv2.TM_SQDIFF_NORMED:
                # For SQDIFF, lower is better
                locations = np.where(result <= 1.0 - threshold)
                confidences = 1.0 - result[locations]
            else:
                # For other methods, higher is better
                locations = np.where(result >= threshold)
                confidences = result[locations]

            # Create match results
            for (y, x), confidence in zip(zip(*locations), confidences):
                match = MatchResult(
                    template_name=template_name,
                    confidence=float(confidence),
                    x=int(x),
                    y=int(y),
                    width=template.shape[1],
                    height=template.shape[0],
                    method=self.method_name,
                    scale=scale,
                )
                matches.append(match)

        if not matches:
            return []

        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)

        if single_best:
            # Apply non-maximum suppression to get single best match
            return [self._non_max_suppression(matches, overlap_threshold=0.3)[0]]

        # Apply NMS to remove overlapping detections
        return self._non_max_suppression(matches)

    def match_multiple(
        self,
        image: np.ndarray | Image.Image,
        template_names: List[str],
        threshold: Optional[float] = None,
    ) -> dict[str, List[MatchResult]]:
        """
        Match multiple templates in one image.

        Args:
            image: Input image
            template_names: List of template names to match
            threshold: Override default threshold

        Returns:
            Dictionary mapping template names to match results
        """
        results = {}
        for template_name in template_names:
            matches = self.match(image, template_name, threshold, single_best=False)
            if matches:
                results[template_name] = matches

        logger.debug(
            "Multiple template matching complete",
            templates_searched=len(template_names),
            templates_found=len(results),
        )
        return results

    def _non_max_suppression(
        self,
        matches: List[MatchResult],
        overlap_threshold: float = 0.3,
    ) -> List[MatchResult]:
        """
        Remove overlapping matches using non-maximum suppression.

        Args:
            matches: List of match results
            overlap_threshold: Maximum allowed overlap (IoU)

        Returns:
            Filtered list of matches
        """
        if not matches:
            return []

        # Sort by confidence (highest first)
        matches = sorted(matches, key=lambda m: m.confidence, reverse=True)

        keep = []
        while matches:
            # Keep the best match
            best = matches.pop(0)
            keep.append(best)

            # Remove overlapping matches
            matches = [
                m for m in matches
                if self._compute_iou(best, m) < overlap_threshold
            ]

        return keep

    def _compute_iou(self, match1: MatchResult, match2: MatchResult) -> float:
        """
        Compute Intersection over Union (IoU) between two matches.

        Args:
            match1: First match
            match2: Second match

        Returns:
            IoU value (0.0-1.0)
        """
        x1_min, y1_min = match1.x, match1.y
        x1_max = x1_min + match1.width
        y1_max = y1_min + match1.height

        x2_min, y2_min = match2.x, match2.y
        x2_max = x2_min + match2.width
        y2_max = y2_min + match2.height

        # Compute intersection
        x_inter_min = max(x1_min, x2_min)
        y_inter_min = max(y1_min, y2_min)
        x_inter_max = min(x1_max, x2_max)
        y_inter_max = min(y1_max, y2_max)

        if x_inter_max <= x_inter_min or y_inter_max <= y_inter_min:
            return 0.0

        inter_area = (x_inter_max - x_inter_min) * (y_inter_max - y_inter_min)

        # Compute union
        area1 = match1.width * match1.height
        area2 = match2.width * match2.height
        union_area = area1 + area2 - inter_area

        return inter_area / union_area if union_area > 0 else 0.0

    def visualize_matches(
        self,
        image: np.ndarray,
        matches: List[MatchResult],
        output_path: Optional[Path] = None,
    ) -> np.ndarray:
        """
        Draw bounding boxes around matches for visualization.

        Args:
            image: Input image
            matches: List of match results
            output_path: Optional path to save visualization

        Returns:
            Image with bounding boxes drawn
        """
        # Convert to BGR for OpenCV drawing
        if len(image.shape) == 2:
            vis_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 3:
            vis_image = image.copy()
        else:
            vis_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        # Draw each match
        for match in matches:
            # Color based on confidence (green = high, red = low)
            color_intensity = int(match.confidence * 255)
            color = (0, color_intensity, 255 - color_intensity)  # BGR

            # Draw rectangle
            cv2.rectangle(
                vis_image,
                (match.x, match.y),
                (match.x + match.width, match.y + match.height),
                color,
                2,
            )

            # Draw label
            label = f"{match.template_name}: {match.confidence:.2f}"
            cv2.putText(
                vis_image,
                label,
                (match.x, match.y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        if output_path:
            cv2.imwrite(str(output_path), vis_image)
            logger.info("Visualization saved", path=str(output_path))

        return vis_image
