# webcam-fx

Real-time webcam effects in Python + OpenCV, inspired by [wxll.hx on TikTok](https://www.tiktok.com/@wxll.hx).

![demo](https://img.shields.io/badge/OpenCV-4.8+-green) ![Python](https://img.shields.io/badge/Python-3.11+-blue)

---

## Effects

| Key | Effect | Description |
|-----|--------|-------------|
| `T` | **Thermal Camera** | CLAHE + bilateral filter + JET colormap + temporal smoothing |
| `S` | **TV Scan Lines** | Chromatic aberration, scan-line mask, interlace flicker, rolling wave, vignette |
| `I` | **Invisibility Cloak** | HSV background subtraction with feathered edge blending |
| `R` | Reset | Passthrough (raw camera) |
| `Q` / `ESC` | Quit | |

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/webcam-fx
cd webcam-fx
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
# Default: thermal effect, camera 0, 1280x720
python main.py

# Custom options
python main.py --camera 1 --effect scanlines --width 1920 --height 1080
```

---

## Project Structure

```
webcam-fx/
├── main.py                  # Entry point, key handling, capture loop
├── effects/
│   ├── base.py              # Abstract BaseEffect
│   ├── thermal.py           # ThermalEffect
│   ├── scanlines.py         # ScanlineEffect
│   └── invisibility.py      # InvisibilityEffect
├── utils/
│   └── renderer.py          # HUD overlay + FPS counter
└── requirements.txt
```

---

## Extending

Add a new effect by:

1. Creating `effects/my_effect.py` extending `BaseEffect`
2. Implementing `process(self, frame) -> np.ndarray`
3. Registering it in `main.py`'s `EFFECTS` dict and `KEYBINDINGS`

```python
# effects/my_effect.py
from .base import BaseEffect

class MyEffect(BaseEffect):
    def process(self, frame):
        # your pipeline here
        return frame
```

---

## Invisibility Cloak — Calibration Notes

- On launch, stay **out of frame** for ~1.5 seconds (45 frames) while the background is captured.
- Wear a **red garment** (default) — the HSV mask targets red hues.
- Change cloak colour by passing `color="green"` or `color="blue"` to `InvisibilityEffect()` in `main.py`.
- If lighting changes, press `I` to re-activate the effect and re-calibrate.

---

## Thermal — Tuning

In `effects/thermal.py`:

```python
ThermalEffect.COLORMAP = cv2.COLORMAP_INFERNO   # dramatic dark palette
ThermalEffect.COLORMAP = cv2.COLORMAP_JET       # classic rainbow (default)
ThermalEffect.COLORMAP = cv2.COLORMAP_HOT       # fire-style
```

Temporal blend weight `_alpha` (0.0–1.0): higher = more responsive, lower = smoother.

---

## License

MIT
