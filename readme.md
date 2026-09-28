# 🏴‍☠️ Chest Hunter (Wayland Edition)

A high-performance, resilient automation tool designed for Linux (Wayland/COSMIC & X11). Optimized for low-latency environments like **YouNow**.

## Description

**Chest Hunter** is a sophisticated computer-vision-based automation tool designed to monitor and interact with live streams on the [YouNow](https://www.younow.com) platform. Developed to solve the challenge of missing time-sensitive "Chest" drops during multitasking, the project evolved from a simple procedural script into a robust Object-Oriented system capable of managing multiple targets simultaneously.

The core logic utilizes **OpenCV** and template matching to identify chest spawns across multi-display setups. Unlike standard click-bots, Chest Hunter implements a custom **Resilience Engine** to filter out environmental noise—such as workspace swiping or UI pop-ups—ensuring interactions only occur when consistent movement "streaks" are detected.

## Key Technical Achievements:

* **Multi-Object Tracking (MOT):** A specialized `Manager` class handles the lifecycle of multiple `Chest` instances, using coordinate-distance mathematics to distinguish between new targets and existing ones.
* **Wayland Compatibility Bridge:** Overcame the strict security and display limitations of the Wayland protocol by implementing a **ydotool** system service. This allows for low-level mouse control that standard libraries like PyAutoGUI cannot achieve on modern Linux environments.
* **3-Monitor Independent Scaling Engine:** Successfully scales across a massive $5760 \times 1080$ multi-display matrix. Implements per-monitor **2D linear coordinate transformation** ($f(x) = m \cdot x + b$) across both $X$ and $Y$ axes to account for HiDPI virtual input scaling, top window panels, and hardware drift independently for every display.
* **Inactivity Auto-Shutdown:** Features a smart idle timer that automatically terminates the application after 5 minutes of zero chest detections, freeing up CPU/GPU resources when streams go quiet.
* **Intelligent Filtering:** Includes a built-in "Noise vs. Motion" logic that prevents false positives by requiring consistent movement patterns before a click is triggered.

## 🚀 Key Features

### 1. Unified Linux & 3-Monitor Compatibility
- Full migration from **X11 to Wayland**, supporting up to 6 simultaneous split-view live streams across 3 independent physical displays.
- Uses a **Bridge Layer** combined with a deterministic state machine (stepping hops and origin resets) to bypass compositor boundary blocks.

### 2. Intelligent Management & Resource Efficiency
- **Smart Manager:** Recognizes if a chest has slightly moved rather than treating it as a new object, preventing duplicate clicks.
- **Dynamic Lifecycle:** Automatically handles add/remove events when game tabs open or close.
- **Auto-Shutdown Guard:** Automatically exits after 5 minutes of inactivity to prevent CPU/memory hanging when no chests are active.
- **Auto-Cleanup:** Features a cooldown mechanism that purges stale chest data from memory to keep the script lean.

### 3. Precision Triggering & 2D Linear Calibration
- **Streak System:** Requires **3 consecutive movements** within a specific threshold before triggering a click. This effectively eliminates false positives.
- **Per-Monitor Linear Math:** Translates raw vision pixels into `ydotool` commands using calibrated slope ($m$) and intercept ($b$) values per axis, ensuring pixel-perfect accuracy from top-row chests down to bottom UI buttons.

### 4. Hardware Resilience (The "Bridge" Fix)
- **Monitor-Sleep Protection:** Implemented a 2.0s timeout and `TimeoutExpired` handling. 
- **Auto-Recovery:** The script intelligently waits and retries if the display signal is lost (e.g., monitor turning off), resuming instantly upon wake-up.

---

## 🛠️ Usage
Run the script through your preferred terminal. For high-performance play:
```bash
pip install -r requirements.txt
python main.py
