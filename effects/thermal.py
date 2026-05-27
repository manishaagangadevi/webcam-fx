import cv2
import numpy as np
from .base import BaseEffect


class ThermalEffect(BaseEffect):
    COLORMAP = cv2.COLORMAP_JET

    def __init__(self):
        self._prev  = None
        self._alpha = 0.65

    def reset(self):
        self._prev = None

    def process(self, frame: np.ndarray) -> np.ndarray:
        if frame is None or frame.size == 0 or frame.shape[0] < 5 or frame.shape[1] < 5:
            return frame
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        gray    = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        clahe   = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray    = clahe.apply(gray)
        gray    = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
        thermal = cv2.applyColorMap(gray, self.COLORMAP)
        tf      = thermal.astype(np.float32)
        if self._prev is None or self._prev.shape != tf.shape:
            self._prev = tf
        blended    = cv2.addWeighted(tf, self._alpha, self._prev, 1.0 - self._alpha, 0)
        self._prev = blended
        return np.clip(blended, 0, 255).astype(np.uint8)