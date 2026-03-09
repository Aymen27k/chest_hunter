import os
import numpy as np
from PIL import Image
import pyautogui
import time
import subprocess
import tempfile
import glob
from pynput.mouse import Button, Controller as MouseController

class HunterBridge:
    def __init__(self):
        # Determine if we are on Wayland
        self.is_wayland = os.environ.get('XDG_SESSION_TYPE') == 'wayland'
        self.mouse = MouseController()
        
        # Fail-safe: pyautogui movements are often blocked on Wayland, 
        # so we disable the pause to prevent script hanging.
        pyautogui.PAUSE = 0 
        
        print(f"[SYSTEM] Environment Detected: {'WAYLAND' if self.is_wayland else 'X11'}")
        if self.is_wayland:
            print("[INFO] Using pynput for Wayland-compatible mouse control.")

    def get_screenshot(self, region=None):
        """
        COSMIC-Native Screenshot Bridge.
        Uses cosmic-screenshot with notifications disabled.
        """
        if not self.is_wayland:
            return pyautogui.screenshot(region=region)

        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                # --notify=false: Prevents the system "Screenshot saved" popup
                # --interactive=false: Captures immediately without asking which area
                cmd = [
                    "cosmic-screenshot", 
                    "--interactive=false", 
                    "--notify=false",
                    "--save-dir", tmp_dir
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)

                # Buffer for file availability
                time.sleep(0.1)

                files = glob.glob(os.path.join(tmp_dir, "*"))
                if not files:
                    return None

                latest_file = max(files, key=os.path.getmtime)
                
                with Image.open(latest_file) as img:
                    if region:
                        left, top, w, h = region
                        processed_img = img.crop((left, top, left + w, top + h))
                    else:
                        processed_img = img.copy()
                    
                    processed_img.load() 
                    return processed_img

            except Exception as e:
                print(f"[DEBUG] Bridge Screenshot Error: {e}")
                return None
            
        return None

    def click_at(self, x, y):
        """
        Moves and clicks using pynput. 
        Includes a small 'settle' delay to ensure Wayland registers the location.
        """
        try:
            # 1. Move to target
            self.mouse.position = (int(x), int(y))
            
            # 2. Settle time (Wayland compositor needs a moment to update focus)
            time.sleep(0.1)
            
            # 3. Press and Release
            self.mouse.press(Button.left)
            time.sleep(0.05)
            self.mouse.release(Button.left)
            
            print(f"[INPUT] Clicked target at ({x}, {y})")
        except Exception as e:
            print(f"[ERROR] Mouse injection failed: {e}")

    def move_back(self, x, y):
        """Returns cursor to original position."""
        self.mouse.position = (int(x), int(y))