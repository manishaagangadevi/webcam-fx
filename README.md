# webcam-fx

Real-time webcam effects controlled by hand gestures using Python, OpenCV and MediaPipe.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square) ![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green?style=flat-square) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange?style=flat-square) ![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey?style=flat-square)

---

## Overview

webcam-fx turns your webcam into a real-time effects engine controlled entirely by hand gestures — no keyboard, no mouse, no special equipment.

Point your index fingers at each other to summon an effect window in mid-air. The frame resizes live as you move your hands. Pinch both hands simultaneously to cycle through effects.

---

## Effects

| Effect | How it works |
|--------|-------------|
| **Thermal** | Converts the frame to grayscale, applies CLAHE contrast enhancement, bilateral smoothing, then maps to a JET false-colour palette with temporal blending to reduce flicker |
| **Scan Lines** | Layers chromatic aberration, CRT scan-line mask, interlace flicker, rolling brightness wave, gaussian grain and vignette — full analogue TV simulation |
| **Invisibility** | Uses MediaPipe Selfie Segmentation to detect your body and replace it with a pre-captured background — no green screen or special clothing needed |

---

## Gesture Controls

| Gesture | Action |
|---------|--------|
| Both index fingers pointing at each other | Creates the effect frame between your fingertips |
| Spread hands apart | Makes the frame bigger |
| Bring hands closer | Makes the frame smaller |
| Pinch both hands at the same time | Cycles to next effect |

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/manishaagangadevi/webcam-fx
cd webcam-fx
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run**
```bash
python main.py
```

> **Invisibility tip:** When the program starts, stay out of frame for 2 seconds while it captures the background automatically.

---

## Requirements

```
opencv-python>=4.8.0
numpy>=1.24.0
mediapipe>=0.10.0
```

Python 3.10 or higher recommended.

---

## Project Structure

```
webcam-fx/
├── main.py                  # Entry point — hand tracking, gesture logic, render loop
├── effects/
│   ├── base.py              # Abstract BaseEffect class
│   ├── thermal.py           # Thermal camera effect
│   ├── scanlines.py         # TV scan lines effect
│   └── invisibility.py      # Invisibility via body segmentation
├── utils/
│   └── renderer.py          # HUD overlay and FPS counter
└── requirements.txt
```

---

## Built with

- [OpenCV](https://opencv.org/) — camera capture and image processing
- [MediaPipe](https://mediapipe.dev/) — hand tracking and body segmentation
- [NumPy](https://numpy.org/) — array operations and effect pipelines