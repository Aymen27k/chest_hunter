import pyautogui

def item_location_clicking(image_path):
    # Initialize the mouse position
    x, y = pyautogui.position()
    try:
        window_pop_up = pyautogui.locateOnScreen(image_path, confidence=0.8, grayscale=True)
        if window_pop_up:
            center_x = window_pop_up.left + window_pop_up.width / 2
            center_y = window_pop_up.top + window_pop_up.height / 2
            pyautogui.click(center_x, center_y)
            pyautogui.moveTo(x, y)
            print(f"Clicked on '{image_path}' at ({int(center_x)}, {int(center_y)})")
            return True
        else:
            print(
                f"'{image_path}' found but not clickable (perhaps due to very low confidence returning None, "
                f"though unlikely with ImageNotFoundException).")
            return False
    except pyautogui.ImageNotFoundException:
        print(f"Image '{image_path} not found on screen. Skipping Click")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while processing '{image_path}': {e}")
        return False