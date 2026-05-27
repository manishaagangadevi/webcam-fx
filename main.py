import cv2
import numpy as np
import mediapipe as mp
import math
import time

from effects.thermal import ThermalEffect
from effects.scanlines import ScanlineEffect
from effects.invisibility import InvisibilityEffect

mp_hands = mp.solutions.hands

EFFECTS = ["thermal", "scanlines", "invisibility"]
EFFECT_MAP = {
    "thermal":      ThermalEffect(),
    "scanlines":    ScanlineEffect(),
    "invisibility": InvisibilityEffect(),
}
EFFECT_COLORS = {
    "thermal":      (0, 80, 255),
    "scanlines":    (180, 180, 180),
    "invisibility": (0, 255, 180),
}

PINCH_DIST     = 45
SMOOTH         = 0.15
PINCH_COOLDOWN = 1.2


def dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def lm_px(landmark, w, h):
    return int(landmark.x * w), int(landmark.y * h)


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    # Background capture
    print("\n=== webcam-fx ===")
    print("Stay OUT of frame for 2 seconds — capturing background...")
    bg_frames = []
    bg_needed = 60
    while len(bg_frames) < bg_needed:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        bg_frames.append(frame.astype(np.float32))
        display = frame.copy()
        cv2.putText(display,
                    f"Stay out! Capturing background... ({bg_needed - len(bg_frames)} frames)",
                    (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2)
        cv2.imshow("webcam-fx", display)
        cv2.waitKey(1)

    background = np.median(np.stack(bg_frames, axis=0), axis=0).astype(np.uint8)
    EFFECT_MAP["invisibility"]._background = background
    EFFECT_MAP["invisibility"]._calibrated = True
    print("Done! Step into frame.\n")

    effect_idx     = 0
    last_pinch_t   = 0.0
    both_pinch_was = False

    # Smoothed box coords
    s_x1 = s_y1 = s_x2 = s_y2 = None

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.5,
        max_num_hands=2,
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]
            out   = frame.copy()

            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            left_index  = None
            right_index = None
            left_pinch  = False
            right_pinch = False

            if results.multi_hand_landmarks and results.multi_handedness:
                for lm, handed in zip(results.multi_hand_landmarks,
                                      results.multi_handedness):
                    label     = handed.classification[0].label
                    idx_tip   = lm_px(lm.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP], w, h)
                    thumb_tip = lm_px(lm.landmark[mp_hands.HandLandmark.THUMB_TIP], w, h)
                    pinching  = dist(idx_tip, thumb_tip) < PINCH_DIST

                    if label == "Right":   # mirrored = left on screen
                        left_index  = idx_tip
                        left_pinch  = pinching
                    else:
                        right_index = idx_tip
                        right_pinch = pinching

                    # Draw dots
                    dot_c = (0, 255, 100) if pinching else (0, 0, 255)
                    cv2.circle(out, thumb_tip, 8, dot_c, -1)
                    cv2.circle(out, idx_tip,   8, dot_c, -1)
                    cv2.line(out, thumb_tip, idx_tip, dot_c, 2)
                    if pinching:
                        mid = ((thumb_tip[0]+idx_tip[0])//2,
                               (thumb_tip[1]+idx_tip[1])//2)
                        cv2.circle(out, mid, 14, (255,255,255), 2)

            # Both pinch = cycle filter
            now            = time.time()
            both_pinch_now = left_pinch and right_pinch
            if both_pinch_now and not both_pinch_was:
                if now - last_pinch_t > PINCH_COOLDOWN:
                    effect_idx   = (effect_idx + 1) % len(EFFECTS)
                    last_pinch_t = now
                    for fx in EFFECT_MAP.values():
                        fx.reset()
                    EFFECT_MAP["invisibility"]._background = background
                    EFFECT_MAP["invisibility"]._calibrated = True
            both_pinch_was = both_pinch_now

            # Build box — FIXED:
            # X = from left index tip to right index tip (horizontal span)
            # Y = centered on the average Y of both fingertips
            #     height = 60% of the horizontal width so it looks like a screen
            if left_index and right_index:
                left_x,  left_y  = left_index
                right_x, right_y = right_index

                # Horizontal bounds = exact finger span
                raw_x1 = min(left_x, right_x)
                raw_x2 = max(left_x, right_x)
                span   = raw_x2 - raw_x1

                # Vertical: top = fingertip Y level, height = 60% of span
                top_y  = min(left_y, right_y)
                raw_y1 = top_y
                raw_y2 = top_y + int(span * 0.60)

                # Smooth each edge independently
                def sm(prev, target):
                    return int(prev*(1-SMOOTH) + target*SMOOTH) if prev is not None else target

                s_x1 = sm(s_x1, raw_x1)
                s_y1 = sm(s_y1, raw_y1)
                s_x2 = sm(s_x2, raw_x2)
                s_y2 = sm(s_y2, raw_y2)

                # Clamp to frame
                x1 = max(0, s_x1)
                y1 = max(0, s_y1)
                x2 = min(w, s_x2)
                y2 = min(h, s_y2)

                if x2 - x1 > 20 and y2 - y1 > 20:
                    active_name = EFFECTS[effect_idx]
                    roi = frame[y1:y2, x1:x2].copy()
                    if roi.size > 0:
                        try:
                            processed = EFFECT_MAP[active_name].process(roi)
                            out[y1:y2, x1:x2] = processed
                        except Exception:
                            pass

                    bc = EFFECT_COLORS[active_name]
                    cv2.rectangle(out, (x1, y1), (x2, y2), bc, 2)

                    # Corner markers
                    cs = 18
                    for px, py in [(x1,y1),(x2,y1),(x1,y2),(x2,y2)]:
                        dx = cs if px == x1 else -cs
                        dy = cs if py == y1 else -cs
                        cv2.line(out, (px,py), (px+dx, py), bc, 3)
                        cv2.line(out, (px,py), (px, py+dy), bc, 3)

                # Dot on each fingertip (on top of everything)
                cv2.circle(out, left_index,  10, (255,255,255), 2)
                cv2.circle(out, right_index, 10, (255,255,255), 2)

            else:
                s_x1 = s_y1 = s_x2 = s_y2 = None
                msg  = "Show both hands to activate"
                font = cv2.FONT_HERSHEY_SIMPLEX
                (mw, mh), _ = cv2.getTextSize(msg, font, 0.65, 1)
                cv2.rectangle(out,
                              ((w-mw)//2-12, h//2-mh-14),
                              ((w+mw)//2+12, h//2+12),
                              (0,0,0), cv2.FILLED)
                cv2.putText(out, msg, ((w-mw)//2, h//2),
                            font, 0.65, (0,220,255), 1, cv2.LINE_AA)

            # HUD
            active_name = EFFECTS[effect_idx]
            color = EFFECT_COLORS[active_name]
            font  = cv2.FONT_HERSHEY_SIMPLEX
            label = f"FX: {active_name.upper()}"
            (tw, th), _ = cv2.getTextSize(label, font, 0.8, 2)
            cv2.rectangle(out, (10,10), (tw+26, th+26), (0,0,0), cv2.FILLED)
            cv2.putText(out, label, (18, th+18), font, 0.8, color, 2, cv2.LINE_AA)

            lc = (0,255,100) if left_pinch  else (60,60,60)
            rc = (0,255,100) if right_pinch else (60,60,60)
            cv2.circle(out, (w-50, 28), 10, lc, -1)
            cv2.circle(out, (w-20, 28), 10, rc, -1)
            cv2.putText(out, "L", (w-55,33), font, 0.38, (0,0,0), 1)
            cv2.putText(out, "R", (w-25,33), font, 0.38, (0,0,0), 1)

            if both_pinch_now:
                cv2.putText(out, "SWITCHING!", (w//2-70, 65),
                            font, 0.9, (0,255,255), 2, cv2.LINE_AA)

            hint = "Spread hands = box size | Pinch BOTH = change filter | Q=quit"
            (hw,_),_ = cv2.getTextSize(hint, font, 0.37, 1)
            cv2.rectangle(out, (0,h-16),(w,h),(0,0,0),cv2.FILLED)
            cv2.putText(out, hint, ((w-hw)//2, h-3),
                        font, 0.37, (150,150,150), 1, cv2.LINE_AA)

            cv2.imshow("webcam-fx", out)
            if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()