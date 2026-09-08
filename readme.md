# 🏴‍☠️ Chest Hunter (Wayland Edition)

A high-performance, resilient automation tool designed for Linux (Wayland/COSMIC & X11). Optimized for low-latency environments like **Younow**.

## Description

**Chest Hunter** is a sophisticated computer-vision-based automation tool designed to monitor and interact with live streams on the [YouNow](https://www.younow.com) platform. Developed to solve the challenge of missing time-sensitive "Chest" drops during multitasking, the project evolved from a simple procedural script into a robust Object-Oriented system capable of managing multiple targets simultaneously.

The core logic utilizes **OpenCV** and template matching to identify chest spawns across secondary displays. Unlike standard click-bots, Chest Hunter implements a custom **Resilience Engine** to filter out environmental noise—such as workspace swiping or UI pop-ups—ensuring interactions only occur when consistent movement "streaks" are detected.

## Key Technical Achievements:

* **Multi-Object Tracking (MOT):** A specialized `Manager` class handles the lifecycle of multiple `Chest` instances, using coordinate-distance mathematics to distinguish between new targets and existing ones.
* **Wayland Compatibility Bridge:** Overcame the strict security and display limitations of the Wayland protocol by implementing a **ydotool** system service. This allows for low-level mouse control that standard libraries like PyAutoGUI cannot achieve on modern Linux environments.
* **Dual-Monitor Calibration:** Solves the "coordinate offset" issue inherent in multi-monitor Linux setups through a custom calibration ratio and a **3-step transition algorithm** that allows the cursor to traverse virtual screen boundaries accurately.
* **Intelligent Filtering:** Includes a built-in "Noise vs. Motion" logic that prevents false positives by requiring consistent movement patterns before a click is triggered.

## 🚀 Key Features

### 1. Unified Linux Compatibility
- Full migration from **X11 to Wayland**.
- Uses a **Bridge Layer** to decouple platform-specific tools from core logic, ensuring stability across different compositors.

### 2. Intelligent Management & Tracking
- **Smart Manager:** Recognizes if a chest has slightly moved rather than treating it as a new object, preventing duplicate clicks.
- **Dynamic Lifecycle:** Automatically handles add/remove events when game tabs open or close.
- **Auto-Cleanup:** Features a cooldown mechanism that purges stale chest data from memory to keep the script lean.

### 3. Precision Triggering
- **Streak System:** Requires **3 consecutive movements** within a specific threshold before triggering a click. This effectively eliminates false positives.
- **Wayland Navigator:** Uses a unique 3-step "cursor push" (Stage -> 1921,0 -> Target) to navigate between isolated screen spaces on multi-monitor setups.

### 4. Hardware Resilience (The "Bridge" Fix)
- **Monitor-Sleep Protection:** Implemented a 2.0s timeout and `TimeoutExpired` handling. 
- **Auto-Recovery:** The script intelligently waits and retries if the display signal is lost (e.g., monitor turning off), resuming instantly upon wake-up.

---

## 🛠️ Usage
Run the script through your preferred terminal. For high-performance play:
```bash
pip install -r requirements.txt
python main.py