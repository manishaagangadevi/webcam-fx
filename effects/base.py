"""Base class for all webcam effects."""

import numpy as np
import cv2
from abc import ABC, abstractmethod


class BaseEffect(ABC):
    """All effects inherit from this. Override process() and optionally reset()."""

    def reset(self):
        """Called when the effect is re-activated. Override for stateful effects."""
        pass

    @abstractmethod
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply the effect to a BGR frame.

        Args:
            frame: uint8 BGR image from cv2.VideoCapture.

        Returns:
            uint8 BGR image of the same dimensions.
        """
        ...

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def ensure_bgr(frame: np.ndarray) -> np.ndarray:
        if frame.ndim == 2:
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        return frame

    @staticmethod
    def resize_like(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
        h, w = ref.shape[:2]
        return cv2.resize(src, (w, h))
