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
        # Your primary monitor width boundary
        self.primary_width = 1920

        # --- UNIFIED COSMIC CALIBRATION RATIOS ---
        self.cal_x = 850 / 3539  # Base matrix scale (~0.23358)
        self.cal_y = 360 / 717   # Base matrix scale (~0.50209)

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

    def click_at(self, raw_x, raw_y, is_like=False):
        """
        Smooth Non-Linear Scaling Logic:
        Dynamically adjusts scale factor based on horizontal position (raw_x)
        to handle COSMIC's edge compression without sharp boundary jumps.
        """
        # 1. Uniform Y scaling
        target_y = int(raw_y * self.cal_y)

        # 2. Dynamic X Scaling
        if is_like:
            # Dedicated override for Far-Right Like Button
            target_x = int(int(raw_x * self.cal_x) * (330 / 594))
        else:
            # Interpolated multiplier: Smoothly transitions based on screen position
            # Left region (raw_x <= 3100) scales around ~0.15135
            # Right/Center region (raw_x > 3100) uses your verified base self.cal_x (~0.23358)
            if raw_x <= 3100:
                # Smooth transition factor approaching the left anchor
                ratio = raw_x / 2775.0
                scale_x = 0.15135 * ratio
            else:
                scale_x = self.cal_x

            target_x = int(raw_x * scale_x)

        try:
            # Inter-monitor jump
            subprocess.run(["ydotool", "mousemove", "1100", "0"], check=True)
            time.sleep(0.05) 

            # Target move
            subprocess.run(["ydotool", "mousemove", "-a", str(target_x), str(target_y)], check=True)
        except Exception as e:
            print(f"[ERROR] Monitor jump or move failed: {e}")

        # Final Execution Click
        try:
            time.sleep(0.2)
            subprocess.run(["ydotool", "click", "0xc0"], check=True)
        except Exception as e:
            print(f"[ERROR] Click execution failed: {e}")

    def locate_and_click(self, template_path, confidence=0.8, region=None, is_like=False):
        """Vision engine: Now tunnels the is_like flag down to the absolute clicker."""
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
            # Pass the override flag straight down to the coordinate processor
            self.click_at(cx, cy, is_like=is_like)
            return True
            
        return False

bridge = Bridge()