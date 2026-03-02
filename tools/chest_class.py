import pyautogui
import cv2
import numpy as np
import time
import random

class Chest:
    def __init__(self, template_name, coords):
        self.template = template_name
        self.coords = coords
        self.center = (coords[0] + coords[2] / 2, coords[1] + coords[3] / 2)

        self.previous_frame = None
        self.movement_score = 0
        self.clicked = False
        
        self.bounce_streak = 0
        self.required_streak = 3 
        self.last_bounce_time = 0 
        self.last_seen = time.time()

    def is_bouncing(self, low=500, high=8000, threshold=55):
        if self.clicked:
            return False

        try:
            # OPTIMIZATION: Take the screenshot of the region
            current_screenshot = pyautogui.screenshot(region=self.coords)
            current_frame = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_BGR2GRAY)
            del current_screenshot 
        except Exception:
            self.bounce_streak = 0
            return False

        if self.previous_frame is None:
            self.previous_frame = current_frame
            return False

        # EFFICIENCY CHECK: Bitwise comparison
        if np.array_equal(self.previous_frame, current_frame):
            self.movement_score = 0
            # We don't necessarily reset the streak to 0 here to allow for 
            # very slight pauses in animation, but we return False.
            return False

        try:
            difference = cv2.absdiff(self.previous_frame, current_frame)
            _, thresh = cv2.threshold(difference, threshold, 255, cv2.THRESH_BINARY)
            self.movement_score = cv2.countNonZero(thresh)
            
            self.previous_frame = current_frame

            if low < self.movement_score < high:
                self.bounce_streak += 1
                status_msg = "STREAKING"
            elif self.movement_score >= high:
                self.bounce_streak = 0
                status_msg = "RESET (MAJOR CHANGE)"
            else:
                self.bounce_streak = 0 
                status_msg = "IDLE"

            if self.movement_score > 0:
                print(f"[DEBUG] {self.template.split('/')[-1]} | Score: {self.movement_score} | Streak: {self.bounce_streak}/{self.required_streak} | {status_msg}")

            return self.bounce_streak >= self.required_streak
                
        except Exception:
            self.bounce_streak = 0
            return False

    def click(self, score=None):
        if self.clicked:
            return
        delay = random.uniform(0.3, 0.7) 
        print(f"!!! TRIGGERING CLICK on {self.template.split('/')[-1]} after {delay:.2f}s delay !!!")
        time.sleep(delay)
        try:
            orig_x, orig_y = pyautogui.position()
            pyautogui.click(self.center[0], self.center[1])
            pyautogui.moveTo(orig_x, orig_y)
            self.clicked = True
            self.bounce_streak = 0 
            self.previous_frame = None 
        except Exception as e:
            print(f"Failed to execute click: {e}")

class ChestManager:
    def __init__(self, distance_threshold=50, max_idle_time=8.0):
        self.active_chests = []
        self.distance_threshold = distance_threshold
        self.max_idle_time = max_idle_time

    def update_from_vision(self, detected_list):
        now = time.time()
        for template_name, coords in detected_list:
            new_center = (coords[0] + coords[2] / 2, coords[1] + coords[3] / 2)
            found_existing = False
            for chest in self.active_chests:
                dist = np.sqrt((chest.center[0] - new_center[0])**2 + (chest.center[1] - new_center[1])**2)
                if dist < self.distance_threshold:
                    chest.coords = coords
                    chest.center = new_center
                    chest.last_seen = now
                    found_existing = True
                    break
            if not found_existing:
                self.active_chests.append(Chest(template_name, coords))

        # Cleanup: Remove chests not seen recently
        # IMPORTANT: If you swap workspaces, vision won't find them, 
        # so they will be removed from the registry after max_idle_time.
        self.active_chests = [c for c in self.active_chests if (now - c.last_seen < self.max_idle_time) and not c.clicked]

    def get_active_chests(self):
        return self.active_chests