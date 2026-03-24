# 🏴‍☠️ Chest Hunter (Wayland Edition)

A high-performance, resilient automation tool designed for Linux (Wayland/COSMIC & X11). Optimized for low-latency environments like **Younow**.

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