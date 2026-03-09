from bridge import HunterBridge

bridge = HunterBridge()

# Test Vision
img = bridge.get_screenshot()
if img:
    img.save("wayland_test.png")
    print("Vision Check: Screenshot saved as wayland_test.png. Go check it!")

# Test Input
print("Input Check: Moving mouse in 2 seconds...")
import time
time.sleep(2)
bridge.click_at(500, 500)