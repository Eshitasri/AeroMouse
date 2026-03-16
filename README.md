# 🛸 AeroMouse

A touchless, gesture-based navigation system that turns your webcam into a high-precision optical sensor. Control your operating system using natural hand gestures in the air.

AeroMouse demonstrates how computer vision and real-time hand tracking can replace traditional input devices like a mouse.

# 🌟 The AeroMouse Concept

AeroMouse eliminates the need for physical peripherals by translating hand kinematics into system commands.

Instead of relying on hardware sensors, the system uses real-time hand tracking to interpret gestures and map them to OS-level actions such as cursor movement, clicking, scrolling, and dragging.

The project is built using modern computer vision tools and runs entirely on a standard webcam.

# ✨ Features
🖱 Air Cursor Tracking

Move the cursor using your index fingertip as a pointer.

✋ Palm Click

Opening your palm triggers a left mouse click.

🤏 Pinch Drag

Pinching your thumb and index finger together performs a click-and-drag operation, useful for text selection or moving objects.

✌ Right Click Gesture

Raising index and middle fingers triggers a right-click.

👆 Scroll Mode

Holding three fingers up activates vertical scrolling.

# 📊 Visual Feedback

Real-time display of:

Hand skeleton landmarks

Gesture detection states

Cursor tracking point

FPS performance counter

# ⚡ Smooth Cursor Control

Cursor motion uses low-pass smoothing to reduce jitter and improve usability.

# ⚙️ How It Works

AeroMouse processes webcam frames and extracts 21 hand landmarks using the real-time hand tracking pipeline from MediaPipe.

The system then applies gesture logic to determine user intent.

Cursor Navigation

The cursor follows the index finger tip (Landmark 8).
Hand coordinates from the camera frame are mapped to the screen resolution using interpolation.

Gesture Detection

Finger states are determined by comparing fingertip and joint positions.

Examples:

Open Palm → Left Click

Index + Middle Finger → Right Click

Three Fingers Up → Scroll Mode

Thumb + Index Pinch → Drag / Selection

System Control

Mouse commands are executed using PyAutoGUI.

# 🛠 Tech Stack
Core Language

Python 3.x

Computer Vision

OpenCV

Hand Tracking

MediaPipe

System Control

PyAutoGUI

Numerical Processing

NumPy

# 🚀 Quick Start
Clone the Repository
git clone https://github.com/Eshitasri/AeroMouse.git
cd AeroMouse
Install Dependencies
pip install -r requirements.txt
Run the Program
python aeromouse_main.py

Press q to exit the application.

# 🎮 Gesture Controls
Gesture	System Command
Index Finger Raised	Move Cursor
Open Palm	Left Click
Thumb + Index Pinch	Drag / Select
Index + Middle Fingers	Right Click
Three Fingers Up	Scroll Mode

# 📊 System Feedback

The application window provides real-time feedback including:

Hand landmark visualization

Cursor tracking indicator

Gesture detection labels

Frames-per-second (FPS) performance monitor

# 📌 Future Improvements

Planned upgrades for AeroMouse include:

Machine learning based gesture classification

Two-hand gesture recognition (zoom and advanced commands)

Gesture training module

Multi-monitor support

Custom gesture mapping
