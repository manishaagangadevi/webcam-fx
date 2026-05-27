import cv2
import numpy as np
from .base import BaseEffect


class ScanlineEffect(BaseEffect):

    def __init__(self, line_gap=3, line_alpha=0.55, chroma_shift=3,
                 noise_sigma=18, wave_speed=0.04, vignette_strength=0.55,
                 interlace=True):
        self.line_gap          = line_gap
        self.line_alpha        = line_alpha
        self.chroma_shift      = chroma_shift
        self.noise_sigma       = noise_sigma
        self.wave_speed        = wave_speed
        self.vignette_strength = vignette_strength
        self.interlace         = interlace
        self._frame_idx        = 0
        self._vignette         = None

    def reset(self):
        self._frame_idx = 0
        self._vignette  = None

    def process(self, frame: np.ndarray) -> np.ndarray:
        if frame is None or frame.size == 0 or frame.shape[0] < 5 or frame.shape[1] < 5:
            return frame
        h, w = frame.shape[:2]
        out  = frame.astype(np.float32)
        out  = self._chroma_aberration(out, w)
        out  = self._apply_scanlines(out, h, w)
        if self.interlace:
            out = self._interlace(out, h)
        out  = self._rolling_wave(out, h)
        noise = np.random.normal(0, self.noise_sigma, out.shape).astype(np.float32)
        out   = out + noise
        out   = self._apply_vignette(out, h, w)
        self._frame_idx += 1
        return np.clip(out, 0, 255).astype(np.uint8)

    def _chroma_aberration(self, f, w):
        s = self.chroma_shift
        if s == 0:
            return f
        out = f.copy()
        out[:, s:,  2] = f[:, :w-s, 2]
        out[:, :s,  2] = f[:, 0:1,  2]
        out[:, :w-s,0] = f[:, s:,   0]
        out[:, w-s:,0] = f[:, -1:,  0]
        return out

    def _apply_scanlines(self, f, h, w):
        mask = np.ones((h, 1, 1), dtype=np.float32)
        mask[::self.line_gap] = 1.0 - self.line_alpha
        return f * mask

    def _interlace(self, f, h):
        offset = self._frame_idx % 2
        f[offset::2] *= 0.85
        return f

    def _rolling_wave(self, f, h):
        import math
        phase = self._frame_idx * self.wave_speed * 2 * math.pi
        rows  = np.arange(h, dtype=np.float32)
        wave  = 1.0 + 0.06 * np.sin(rows * 0.04 + phase)
        return f * wave[:, np.newaxis, np.newaxis]

    def _apply_vignette(self, f, h, w):
        if self._vignette is None or self._vignette.shape[:2] != (h, w):
            self._vignette = self._build_vignette(h, w)
        return f * self._vignette

    def _build_vignette(self, h, w):
        cx, cy = w/2, h/2
        Y, X   = np.ogrid[:h, :w]
        dist   = np.sqrt(((X-cx)/cx)**2 + ((Y-cy)/cy)**2)
        vign   = 1.0 - self.vignette_strength * np.clip(dist, 0, 1)
        return vign[:, :, np.newaxis].astype(np.float32)