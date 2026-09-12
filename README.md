# 🛸 AeroMouse: Real-Time Human-Computer Interaction (HCI) System

A touchless, gesture-based computer vision navigation system that translates real-time hand kinetics from a standard webcam stream into high-precision, native operating system input threads. 

AeroMouse bypasses traditional mechanical peripherals by implementing low-latency spatial tracking, signal processing, and defensive software engineering workflows.

---

## 🔥 Advanced Production-Grade Implementations

Unlike basic tutorial computer vision scripts, this framework implements enterprise design patterns to handle real-world deployment challenges:

- **Low-Pass Jitter Filtration (EMA):** Implements an Exponential Moving Average algorithm (`curr_x = prev_x + (target_x - prev_x) / SMOOTHING`) that leverages an 80% historical position weight to dampen high-frequency hand tremors and sensor noise, delivering sub-pixel precision.
- **Temporal State Debouncing:** Features a 400ms signal validation decay buffer. If tracking frames drop out briefly during rapid symbol changes, the pipeline caches the previous mode text instead of flickering the UI layout.
- **Anti-Chatter Intent Locks:** Includes a single-shot execution lock combined with a sustained 500ms temporal hold window for contextual right-clicks, preventing the operating system's context menu from continuously opening and closing itself.
- **Fail-Safe OS Context Protection:** Programmatically wraps the main frame capture thread inside a `try-finally` manager hook, guaranteeing that if a fatal runtime crash occurs, a `mouseUp()` signal is explicitly forced to prevent hardware mouse handles from locking up.
- **Adaptive Coordinate Interpolation:** Utilizes dynamic linear mapping (`np.interp`) with custom boundary frame reductions, allowing users to effortlessly reach the absolute screen edges of high-resolution monitors without forcing their hand out of the webcam's capture view frustum.
- **Modern MediaPipe Tasks API:** Built natively on top of the decoupled, up-to-date Google MediaPipe Tasks vision pipeline rather than the deprecated legacy solutions framework.

---

## 🎮 Intuitive Gesture Vocabulary Mapping

| Gesture Configuration | Active Finger Bitmask State | Emulated System Command |
| --- | --- | --- |
| **Move Cursor** | Index Finger Fully Extended ☝️ | Smooth Mouse Translation (EMA Low-Pass Filter) |
| **Left Click / Open** | Rapid Thumb + Index Finger Pinch 🤏 | Discrete Left-Click (Tap to open links/files) |
| **Text Highlight / Window Drag**| Sustained Thumb + Index Finger Pinch 🗂️ | Programmatic Continuous `mouseDown()` Thread |
| **Right Click** | Sustained Thumbs Up (0.5s Intentional Hold) 👍 | Single-Shot Context Menu Execution |
| **System Standby / Idle** | Open Palm Completely ✋ | Engages Neutral Mode (Resolves "Midas Touch" issue) |
| **Vertical Scroll** | Three Fingers Fully Extended Up 👆 | Dynamic Multi-line Document Scrolling |
| **System Pause** | Closed Fist ✊ | Suspends Input Listeners / Clears Tracking Vectors |

---

## 🛠️ Tech Stack & Architecture

- **Core Runtime:** Python 3.11+
- **Computer Vision API:** Google MediaPipe Tasks API (Hand Landmarker Model Topology)
- **Frame Optimization:** OpenCV (Color space conversions, matrix transformations, and window canvas overlays)
- **Low-Level Emulation:** PyAutoGUI (Native OS input listener thread injection)
- **Mathematical Processing:** NumPy (Vector distance metrics and linear coordinate boundaries)
- **Container Deployment:** Docker (Isolated deployment blueprint)

---

## 🚀 Quick Start & Deployment

### Clone the Repository
```bash
git clone https://github.com/Eshitasri/AeroMouse.git
cd AeroMouse
```

### Install Project Dependencies
```bash
pip install -r requirements.txt
```

### Run the Interface Engine
```bash
python main.py
```
*Press **'q'** inside the focused video overlay canvas window to safely execute the hardware detachment loop and exit.*
