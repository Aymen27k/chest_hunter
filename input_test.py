import time
from bridge import HunterBridge
from pynput.mouse import Controller, Button

def run_coord_test():
    """
    Verification: Coordinate Delta Test & Click Test.
    Final step before full integration: Confirming that the OS
    not only moves the pointer but also registers the click.
    """
    bridge = HunterBridge()
    mouse = Controller()
    
    # Target coordinates (adjust if you want to click a specific UI element)
    target_x, target_y = 500, 500
    
    print("--- WAYLAND INPUT DIAGNOSTIC ---")
    print(f"Current Position: {mouse.position}")
    print(f"Moving to: {target_x}, {target_y} in 2 seconds...")
    time.sleep(2)

    try:
        # Move using the bridge
        bridge.mouse.position = (target_x, target_y)
        
        # Give the OS a tiny moment to process movement
        time.sleep(0.2)
        
        # Check actual position
        final_x, final_y = mouse.position
        print(f"Final Position: {final_x}, {final_y}")
        
        if int(final_x) == target_x and int(final_y) == target_y:
            print("\n[SUCCESS] Movement Verified.")
            
            # --- FINAL CLICK TEST ---
            print("Testing Click in 1 second... (Make sure something clickable is at 500,500)")
            time.sleep(1)
            bridge.mouse.click(Button.left, 1)
            print("[INFO] Click command sent.")
            
            print("\nVerification complete. You can now safely swap pyautogui.click() for bridge.mouse.click() in chest_hunter_v2.py.")
        else:
            print(f"\n[FAIL] Pointer is at {final_x}, {final_y} instead of {target_x}, {target_y}")
            print("Wayland is blocking coordinate overrides.")
            
    except Exception as e:
        print(f"\n[ERROR] Test crashed: {e}")

if __name__ == "__main__":
    run_coord_test()