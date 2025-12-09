from typing import List
import pyautogui
from tools.chest_class import Chest

def detect_chests(templates: List[str]) -> List[Chest]:
    chests = []
    for template in templates:
        try:
            loc = pyautogui.locateOnScreen(template, confidence=0.9, grayscale=True)
            if loc:
                coords = (int(loc.left), int(loc.top), int(loc.width), int(loc.height))
                chests.append(Chest(template, coords))
        except pyautogui.ImageNotFoundException:
            # Skip this template if not found
            continue
    return chests
