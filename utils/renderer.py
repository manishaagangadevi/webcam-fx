import cv2
import numpy as np
import time

EFFECT_COLORS = {
    "thermal":      (0,  80,  255),
    "scanlines":    (180,180, 180),
    "invisibility": (0,  255, 200),
    None:           (100,100, 100),
}
EFFECT_LABELS = {
    "thermal":      "THERMAL",
    "scanlines":    "SCAN LINES",
    "invisibility": "INVISIBILITY",
    None:           "PASSTHROUGH",
}
LEGEND = "[T] Thermal  [S] Scanlines  [I] Invisibility  [R] Reset  [Q] Quit"


class Renderer:
    FONT = cv2.FONT_HERSHEY_SIMPLEX

    def __init__(self):
        self._ts  = time.time()
        self._cnt = 0
        self._fps = 0.0

    def overlay_hud(self, frame, active_effect, num_hands=0, min_hands=2):
        self._update_fps()
        out  = frame.copy()
        h, w = out.shape[:2]
        color = EFFECT_COLORS.get(active_effect, (200, 200, 200))
        label = EFFECT_LABELS.get(active_effect, "")

        badge = f"FX: {label}"
        (tw, th), bl = cv2.getTextSize(badge, self.FONT, 0.7, 2)
        pad = 8
        cv2.rectangle(out, (10, 10), (10+tw+pad*2, 10+th+bl+pad*2), (0,0,0), cv2.FILLED)
        cv2.putText(out, badge, (10+pad, 10+th+pad), self.FONT, 0.7, color, 2, cv2.LINE_AA)

        fps_txt = f"{self._fps:.1f} fps"
        (fw, fh), _ = cv2.getTextSize(fps_txt, self.FONT, 0.55, 1)
        cv2.putText(out, fps_txt, (w-fw-14, fh+14), self.FONT, 0.55, (220,220,220), 1, cv2.LINE_AA)

        if num_hands < min_hands:
            msg = f"Show {min_hands} hand{'s' if min_hands>1 else ''} to activate"
            (mw, mh), _ = cv2.getTextSize(msg, self.FONT, 0.6, 1)
            cx = (w - mw) // 2
            cv2.rectangle(out, (cx-8, h//2-mh-12), (cx+mw+8, h//2+8), (0,0,0), cv2.FILLED)
            cv2.putText(out, msg, (cx, h//2), self.FONT, 0.6, (0,220,255), 1, cv2.LINE_AA)
        else:
            cv2.circle(out, (w-14, fh+30), 6, (0,255,100), -1)

        (lw, lh), _ = cv2.getTextSize(LEGEND, self.FONT, 0.42, 1)
        cv2.rectangle(out, (0, h-lh-18), (w, h), (0,0,0), cv2.FILLED)
        cv2.putText(out, LEGEND, ((w-lw)//2, h-8), self.FONT, 0.42, (200,200,200), 1, cv2.LINE_AA)

        return out

    def _update_fps(self):
        self._cnt += 1
        now = time.time()
        if now - self._ts >= 0.5:
            self._fps = self._cnt / (now - self._ts)
            self._cnt = 0
            self._ts  = now
