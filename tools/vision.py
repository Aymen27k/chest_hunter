from typing import List, Tuple
import pyautogui
import cv2
import numpy as np
from bridge import bridge

def detect_all_chests(templates: List[str], confidence: float = 0.9) -> List[Tuple[str, tuple]]:
    """
    Hybrid Vision: Scans the screen for ALL instances of ALL templates
    using the bridge.get_screenshot() to ensure Wayland/COSMIC compatibility.
    """
    found_chests = []
    
    # Take a single screenshot for this scan cycle via the Bridge
    screen_img = bridge.get_screenshot()

    if screen_img is None:
        return found_chests

    for template_path in templates:
        try:
            # We use locateAll (not locateAllOnScreen) because we already have the image.
            # This bypasses pyautogui's internal screen capture which fails on Wayland.
            matches = list(pyautogui.locateAll(
                template_path,
                screen_img,
                confidence=confidence,
                grayscale=True
            ))
            
            if matches:
                for loc in matches:
                    new_coords = (int(loc.left), int(loc.top), int(loc.width), int(loc.height))
                    if not is_duplicate(new_coords, found_chests):
                        found_chests.append((template_path, new_coords))
                        
        except Exception as e:
            # Silently handle templates that aren't found or errors
            continue
            
    return found_chests

def is_duplicate(new_coords: tuple, existing_list: list, gap: int = 40) -> bool:
    nx, ny, nw, nh = new_coords
    for name, (ex, ey, ew, eh) in existing_list:
        if abs(nx - ex) < gap and abs(ny - ey) < gap:
            return True
    return False