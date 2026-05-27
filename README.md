# webcam-fx

Real-time webcam effects controlled by hand gestures using Python, OpenCV and MediaPipe.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange)

---

## What it does

Point your index fingers at each other to create an effect window in the air. The frame size follows your hands in real time — spread them apart for a bigger frame, bring them closer for a smaller one. Pinch both hands at the same time to cycle through effects.

---

## Effects

| Effect | Description |
|--------|-------------|
| **Thermal** | Heat-map style false colour using CLAHE + bilateral filter + JET colormap |
| **Scan Lines** | CRT monitor simulation with chromatic aberration, interlace flicker and vignette |
| **Invisibility** | Body segmentation replaces you with the background — no special clothing needed |

---

## How to use

**Frame control:**
- Hold both hands up with index fingers pointing
- The effect box spans between your two index fingertips
- Move hands apart → bigger frame
- Move hands closer → smaller frame

**Switch effects:**
- Pinch both hands at the same time (thumb touches index finger on both hands)
- Cycles: Thermal → Scan Lines → Invisibility → Thermal

**Invisibility tip:**
- When you first run the program stay out of frame for 2 seconds
- It captures the background automatically — no green screen needed

---

## Setup

git clone https://github.com/manishaagangadevi/webcam-fx
cd webcam-fx
pip install -r requirements.txt
python main.py

---

## Requirements

opencv-python>=4.8.0
numpy>=1.24.0
mediapipe>=0.10.0

---

## Project Structure

webcam-fx/
├── main.py                  Entry point, hand tracking, gesture control
├── effects/
│   ├── base.py              Abstract base class
│   ├── thermal.py           Thermal camera effect
│   ├── scanlines.py         TV scan lines effect
│   └── invisibility.py      Invisibility via body segmentation
├── utils/
│   └── renderer.py          HUD overlay
└── requirements.txt

