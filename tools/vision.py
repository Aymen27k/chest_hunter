from typing import List, Tuple
import pyautogui
import cv2
import numpy as np

def detect_all_chests(templates: List[str], confidence: float = 0.9) -> List[Tuple[str, tuple]]:
    """
    Scans the screen for ALL instances of ALL templates.
    Returns a list of (template_name, (x, y, w, h))
    """
    found_chests = []
    
    for template_path in templates:
        try:
            # Lowering default confidence slightly to 0.8 for better detection
            # locateAllOnScreen returns a generator
            matches = list(pyautogui.locateAllOnScreen(
                template_path, 
                confidence=confidence, 
                grayscale=True
            ))
            
            if matches:
                for loc in matches:
                    new_coords = (int(loc.left), int(loc.top), int(loc.width), int(loc.height))
                    if not is_duplicate(new_coords, found_chests):
                        found_chests.append((template_path, new_coords))
                        
        except Exception as e:
            # We don't want to crash, just move to the next template
            continue
            
    return found_chests

def is_duplicate(new_coords: tuple, existing_list: list, gap: int = 30) -> bool:
    nx, ny, nw, nh = new_coords
    for name, (ex, ey, ew, eh) in existing_list:
        if abs(nx - ex) < gap and abs(ny - ey) < gap:
            return True
    return False