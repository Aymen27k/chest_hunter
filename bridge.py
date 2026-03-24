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
        # Your primary monitor width (the 'Plate' boundary)
        self.primary_width = 1920

        # CALIBRATION RATIOS
        self.cal_x_sec = 1495 / 1715
        self.cal_y_sec = 630 / 746

        self.cal_x_pri = 1.0
        self.cal_y_pri = 1.0

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
                # This is specifically where it catches the "Monitor Off" hang
                print("[BRIDGE] Monitor appears to be OFF or sleeping. Waiting...")
                time.sleep(5) # Throttle the loop so it doesn't spam the CPU while you're away
                return None
            except Exception as e:
                print(f"[BRIDGE ERROR] Screenshot failed: {e}")
                return None

    def click_at(self, raw_x, raw_y):
        """
        Refinement: Checks target X to determine if a 'Handover' 
        to the Secondary Island is necessary.
        """
        is_secondary = raw_x >= self.primary_width

        if is_secondary:
            # --- SECONDARY ISLAND LOGIC ---
            local_x = raw_x - self.primary_width
            target_x = int(local_x * self.cal_x_sec)
            target_y = int(raw_y * self.cal_y_sec)

            try:
                # Triple-Jump Protocol
                subprocess.run(["ydotool", "mousemove", "-a", "0", "0"], check=True)
                time.sleep(0.05)
                subprocess.run(["ydotool", "mousemove", "-a", str(self.primary_width + 1), "0"], check=True)
                time.sleep(0.05)
                subprocess.run(["ydotool", "mousemove", "-a", str(target_x), str(target_y)], check=True)
            except Exception as e:
                print(f"[ERROR] Secondary jump failed: {e}")
        else:
            # --- PRIMARY ISLAND LOGIC ---
            target_x = int(raw_x * self.cal_x_pri)
            target_y = int(raw_y * self.cal_y_pri)

            try:
                # Direct Reset-to-Target (No Handover needed)
                subprocess.run(["ydotool", "mousemove", "-a", "0", "0"], check=True)
                time.sleep(0.05)
                subprocess.run(["ydotool", "mousemove", "-a", str(target_x), str(target_y)], check=True)
            except Exception as e:
                print(f"[ERROR] Primary move failed: {e}")

        # Final Execution
        try:
            time.sleep(0.2)
            subprocess.run(["ydotool", "click", "0xc0"], check=True)
        except Exception as e:
            print(f"[ERROR] Click execution failed: {e}")

    def locate_and_click(self, template_path, confidence=0.8, region=None):
        """Unchanged detection logic, now feeding into Local Offset clicker."""
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
                
            self.click_at(cx, cy)
            return True
            
        return False

bridge = Bridge()