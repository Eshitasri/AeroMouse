# 🛸 AeroMouse 
A touchless, gesture-based navigation system that turns your webcam into a high-precision optical sensor. Control your OS with the air.

# 🌟 The AeroMouse Concept
AeroMouse eliminates the need for physical peripherals by translating hand kinematics into system commands. Unlike other virtual mice that use awkward pinches, AeroMouse utilizes an Open Palm gesture for selection, making the interaction feel more natural and intentional.

# ✨ Features
Air-Tracking: High-precision cursor movement using the index finger tip.
Palm-Click: Open your palm fully to trigger a "Select" or Left-Click action.
Dynamic Mapping: Automatically scales hand movement to your specific monitor resolution.
Visual Feedback: On-screen landmarks show you exactly what the AI is seeing in real-time.

# ⚙️ How It Works
AeroMouse uses a custom logic gate based on the 21 landmarks provided by the MediaPipe framework:
Navigation Mode: The system tracks the $x, y$ coordinates of the Index Finger Tip (Landmark 8).
Selection Logic: The system monitors the "Open" state of all five fingers. When the distance between the fingertips and the wrist exceeds a specific dynamic threshold, an Open Palm is detected, and a click instruction is sent via PyAutoGUI.

# 🛠 Tech StackCore:
Python 3.x
Vision: OpenCV
Inference: MediaPipe
System Control: PyAutoGUI / NumPy

# Quick StartInstallation
 Clone the repo
git clone https://github.com/Eshitasri/AeroMouse.git
cd AeroMouse

# Install requirements
pip install -r requirements.txt
python aeromouse_main.py

# 🎮 Instructions
Hand Gesture	                System Command
Index Finger                  Raised	Move Cursor
Full Open Palm	              Left Click / Select
Two Fingers (Index/Middle)	  Right Click
Three Fingers Vertical	      Scroll Mode
