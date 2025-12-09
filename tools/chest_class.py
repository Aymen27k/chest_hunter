import pyautogui, cv2, numpy as np, time
import random

class Chest:
    def __init__(self, template, coords):
        self.template = template
        self.coords = coords
        self.previous_frame = None
        self.movement_score = 0
        self.clicked = False


    def __repr__(self):
        return f"Chest(template={self.template}, coords={self.coords}, clicked={self.clicked})"

    def is_bouncing(self, low, high, threshold=50):
        current_screenshot = pyautogui.screenshot(region=self.coords)
        current_frame = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_BGR2GRAY)

        if self.previous_frame is None:
            # Cannot calculate movement yet. Store the current frame for the next iteration.
            print(f"Chest {self.template}: Initializing tracking memory. No bounce check performed.")
            self.previous_frame = current_frame.copy() 
            return False

        difference = cv2.absdiff(self.previous_frame, current_frame)
        _, thresh = cv2.threshold(difference, threshold, 255, cv2.THRESH_BINARY)
        self.movement_score = cv2.countNonZero(thresh)
        print(f"Chest {self.template} movement score: {self.movement_score}")

        # 3. Update the memory for the *next* comparison
        # Use .copy() to ensure we store an independent frame snapshot
        self.previous_frame = current_frame.copy()
        return low < self.movement_score < high


    def click(self):
        # Random delay between 5 and 23 seconds
        delay = random.uniform(5, 23)
        print(f"Waiting {delay:.2f}s before clicking chest {self.template}...")
        time.sleep(delay)
        cx = self.coords[0] + self.coords[2] / 2
        cy = self.coords[1] + self.coords[3] / 2
        x, y = pyautogui.position()
        pyautogui.click(cx, cy)
        pyautogui.moveTo(x, y)
        self.clicked = True
        print(f"Clicked chest {self.template} at ({cx}, {cy})")
        # Calculate extra wait before scanning again
        bounce_duration = 25
        extra_wait = max(0, bounce_duration - delay)
        print(f"Waiting {extra_wait:.2f}s before scanning again...")
        time.sleep(extra_wait)
