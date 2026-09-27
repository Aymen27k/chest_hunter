import time
import subprocess
import tempfile
import glob
import os
import numpy as np
from PIL import Image
import cv2

class Bridge:
    def __init__(self):
        pass

    def get_screenshot(self, region=None):
        """Captures the desktop using cosmic-screenshot."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                subprocess.run(["cosmic-screenshot", "--interactive=false", "--notify=false", "--save-dir", tmp_dir],
                               check=True, capture_output=True, timeout=2.0)
                time.sleep(0.10)
                files = glob.glob(os.path.join(tmp_dir, "*"))
                if not files: return None
                img = Image.open(max(files, key=os.path.getmtime))
                img.load()
                if region:
                    return img.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))
                return img
            except subprocess.TimeoutExpired:
                print("[BRIDGE] Monitor appears to be OFF or sleeping. Waiting...")
                time.sleep(5) 
                return None
            except Exception as e:
                print(f"[BRIDGE ERROR] Screenshot failed: {e}")
                return None

    def _go_to_far_left(self):
        """Forces the cursor to Monitor 2 (Far Left) via controlled stepping hops."""
        # Hop 1: Ensure we step at least one monitor left
        subprocess.run(["ydotool", "mousemove", "-a", "0", "0"], check=True)
        time.sleep(0.01)
        subprocess.run(["ydotool", "mousemove", "--", "-900", "0"], check=True)
        time.sleep(0.01)
        
        # Hop 2: Ensure we hit Monitor 2 even if starting from Monitor 3
        subprocess.run(["ydotool", "mousemove", "-a", "0", "0"], check=True)
        time.sleep(0.01)
        subprocess.run(["ydotool", "mousemove", "--", "-900", "0"], check=True)
        time.sleep(0.01)

        # Lock to Monitor 2 origin
        subprocess.run(["ydotool", "mousemove", "-a", "0", "0"], check=True)
        time.sleep(0.01)

    def click_at(self, raw_x, raw_y, is_like=False):
        """
        Uses controlled stepping hops to navigate to any monitor,
        re-anchors to local (0,0), and clicks the exact target.
        """
        # 1. Reset baseline to Monitor 2 (Far Left)
        self._go_to_far_left()

        # 2. Determine target monitor and step right as needed
        if raw_x < 1920:
            # Monitor 2 (Left) - Already at Monitor 2 origin
            monitor_name = "Monitor 2 (Left)"
            if raw_x > 1300:
                target_x, target_y = 860, 350
            else:
                target_x, target_y = 365, 350

        elif raw_x < 3840:
            # Monitor 1 (Center) - Step right once
            monitor_name = "Monitor 1 (Center)"
            subprocess.run(["ydotool", "mousemove", "965", "0"], check=True)
            time.sleep(0.01)
            subprocess.run(["ydotool", "mousemove", "-a", "0", "0"], check=True)
            time.sleep(0.01)

            if raw_x > 3200:
                target_x, target_y = 850, 365
            else:
                target_x, target_y = 370, 365

        else:
            # Monitor 3 (Right) - Step right twice
            monitor_name = "Monitor 3 (Right)"
            # Hop to Monitor 1
            subprocess.run(["ydotool", "mousemove", "965", "0"], check=True)
            time.sleep(0.01)
            subprocess.run(["ydotool", "mousemove", "-a", "0", "0"], check=True)
            time.sleep(0.01)
            # Hop to Monitor 3
            subprocess.run(["ydotool", "mousemove", "965", "0"], check=True)
            time.sleep(0.01)
            subprocess.run(["ydotool", "mousemove", "-a", "0", "0"], check=True)
            time.sleep(0.01)

            if raw_x > 5000:
                target_x, target_y = 880, 350
            else:
                target_x, target_y = 380, 350

        # 3. Final offset movement & click
        try:
            subprocess.run(["ydotool", "mousemove", "-a", str(target_x), str(target_y)], check=True)
            time.sleep(0.15)
            subprocess.run(["ydotool", "click", "0xc0"], check=True)
            print(f"[BRIDGE] [{monitor_name}] Auto-stepped & Clicked at (-a {target_x} {target_y}) for RAW X: {raw_x}")
        except Exception as e:
            print(f"[ERROR] Click execution failed: {e}")

    def locate_and_click(self, template_path, confidence=0.8, region=None, is_like=False):
        """Vision engine: Detects chest and triggers dynamic stepping click."""
        screen = self.get_screenshot(region=region)
        if not screen: return False
        
        screen_np = np.array(screen.convert('RGB'))
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        if template is None: return False

        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= confidence:
            h, w = template.shape
            cx = max_loc[0] + (w // 2)
            cy = max_loc[1] + (h // 2)
            
            if region:
                cx += region[0]
                cy += region[1]
                
            print(f"[DIAGNOSTIC] Vision found target at RAW: ({cx}, {cy})")
            self.click_at(cx, cy, is_like=is_like)
            return True
            
        return False

bridge = Bridge()