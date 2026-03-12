import cv2
import numpy as np
import time
import random

class Chest:
    def __init__(self, template_name, coords, bridge):
        self.template = template_name
        self.coords = coords
        # The bridge is our "Eye" that works on both X11 and Wayland
        self.bridge = bridge
        self.center = (coords[0] + coords[2] / 2, coords[1] + coords[3] / 2)

        self.previous_frame = None
        self.movement_score = 0
        self.clicked = False
        self.bounce_streak = 0
        self.required_streak = 3
        self.last_seen = time.time()

    def is_bouncing(self, low=500, high=8000, threshold=55):
        """
        Analyzes frames for movement using the Hybrid Bridge.
        Returns True ONLY when the streak requirement is met.
        """
        if self.clicked:
            return False

        try:
            # 1. Ask the bridge for a cropped screenshot of the chest region
            screenshot = self.bridge.get_screenshot(region=self.coords)

            if screenshot is None:
                return False

            # 2. Convert PIL Image to Grayscale NumPy array for OpenCV
            current_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        except Exception as e:
            print(f"[DEBUG] Perception Error on {self.template}: {e}")
            self.bounce_streak = 0
            return False

        # 3. Handle first frame initialization
        if self.previous_frame is None:
            self.previous_frame = current_frame
            return False

        # 4. Quick exit if nothing changed at all
        if np.array_equal(self.previous_frame, current_frame):
            self.movement_score = 0
            return False

        try:
            # Guard against OpenCV Error (-209:Sizes of input arguments do not match)
            # This happens if the bridge returns a crop slightly different in size frame-to-frame
            h, w = self.previous_frame.shape
            if current_frame.shape != (h, w):
                current_frame = cv2.resize(current_frame, (w, h))


            # 5. Calculate Difference (Motion Detection)
            difference = cv2.absdiff(self.previous_frame, current_frame)
            _, thresh = cv2.threshold(difference, threshold, 255, cv2.THRESH_BINARY)
            self.movement_score = cv2.countNonZero(thresh)

            # Update history
            self.previous_frame = current_frame

            # 6. Evaluate the "Bounce"
            if low < self.movement_score < high:
                self.bounce_streak += 1
                status_msg = "STREAKING"
            elif self.movement_score >= high:
                # If the whole screen flashes or moves, it's not a bounce
                self.bounce_streak = 0
                status_msg = "RESET (NOISE)"
            else:
                self.bounce_streak = 0 
                status_msg = "IDLE"

            # 7. Debug Logging
            if self.movement_score > 0:
                name = self.template.split('/')[-1]
                print(f"[DEBUG] {name} | Score: {self.movement_score} | Streak: {self.bounce_streak}/{self.required_streak} | {status_msg}")

            return self.bounce_streak >= self.required_streak

        except Exception as e:
            print(f"[DEBUG] Math Error: {e}")
            self.bounce_streak = 0
            return False

    def click(self):
        """Executes a click via the bridge and resets internal state."""
        if self.clicked:
            return
            
        # Human-like randomization
        delay = random.uniform(0.3, 0.6)
        print(f"!!! TRIGGERING CLICK: {self.template.split('/')[-1]} (Delay: {delay:.2f}s) !!!")

        try:
            self.bridge.click_at(self.center[0], self.center[1])
            self.clicked = True
            self.bounce_streak = 0
            self.previous_frame = None
        except Exception as e:
            print(f"[ERROR] Bridge click failed: {e}")

class ChestManager:
    def __init__(self, bridge, distance_threshold=50, max_idle_time=8.0):
        self.active_chests = []
        self.bridge = bridge
        self.distance_threshold = distance_threshold
        self.max_idle_time = max_idle_time

    def update_from_vision(self, detected_list):
        """
        Processes new detections, updates existing chest objects, 
        and prunes old ones based on idle time or click status.
        """
        now = time.time()
        for template_name, coords in detected_list:
            new_center = (coords[0] + coords[2] / 2, coords[1] + coords[3] / 2)
            found_existing = False
            for chest in self.active_chests:
                dist = np.sqrt((chest.center[0] - new_center[0])**2 + (chest.center[1] - new_center[1])**2)
                if dist < self.distance_threshold:
                    # Update data for the existing chest object
                    chest.coords = coords
                    chest.center = new_center
                    chest.last_seen = now
                    found_existing = True
                    break
            
            if not found_existing:
                print(f"[MANAGER] New tracking target: {template_name.split('/')[-1]} at {new_center}")
                self.active_chests.append(Chest(template_name, coords, self.bridge))

        # Cleanup: Remove chests that haven't been seen in max_idle_time OR were successfully clicked
        self.active_chests = [c for c in self.active_chests if (now - c.last_seen < self.max_idle_time) and not c.clicked]

    def get_active_chests(self):
        return self.active_chests