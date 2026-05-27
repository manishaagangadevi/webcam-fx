import cv2
import numpy as np
from .base import BaseEffect

try:
    import mediapipe as mp
    _MP_OK = True
except ImportError:
    _MP_OK = False


class InvisibilityEffect(BaseEffect):
    BLUR = 21

    def __init__(self):
        self._background = None
        self._calibrated = False
        self._seg        = None

    def _init_seg(self):
        if self._seg is None and _MP_OK:
            self._seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

    def reset(self):
        pass

    def process(self, frame: np.ndarray) -> np.ndarray:
        if frame is None or frame.size == 0:
            return frame
        if not self._calibrated or self._background is None:
            return frame

        self._init_seg()
        if self._seg is None:
            return frame

        roi_h, roi_w = frame.shape[:2]

        # Get the matching background crop for this ROI
        bg = cv2.resize(self._background, (roi_w, roi_h))

        # Segment person in the ROI
        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._seg.process(rgb)
        mask   = result.segmentation_mask  # 1.0 = person, 0.0 = background

        # Feather
        mask_blur = cv2.GaussianBlur(mask, (self.BLUR, self.BLUR), 0)
        alpha     = mask_blur[:, :, np.newaxis]

        # Where person is (alpha=1) → show background (invisible effect)
        out = frame.astype(np.float32) * (1.0 - alpha) + \
              bg.astype(np.float32)    * alpha
        return np.clip(out, 0, 255).astype(np.uint8)