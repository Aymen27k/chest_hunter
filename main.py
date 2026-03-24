import time
import sys
import os
import argparse
from log import log_event
from tools.vision import detect_all_chests
from tools.chest_class import ChestManager
# 1. Import the singleton bridge instance
from bridge import bridge
from tools.config import (
    CHEST_TEMPLATES,
    LOWER_MOVEMENT_THRESHOLD,
    HIGHER_MOVEMENT_THRESHOLD,
    TEMPLATES_DIR,
    MAX_LIKES_PER_STREAM,
    LIKE_BUTTON_PATH,
    LIKE_COOLDOWN
)


def main(with_likes=False):    
    likes_given_current_stream = 0
    
    # 2. DEPENDENCY INJECTION: Pass the bridge into the Manager!
    # Now the Manager will pass it to every Chest it creates.
    manager = ChestManager(bridge=bridge, distance_threshold=50, max_idle_time=25.0)

    last_scan_time = 0
    scan_interval = 1.0
    last_popup_check = 0
    popup_interval = 5.0
    last_like_time = 0
    dot_count = 1

    try:      
        print("Initializing Vision System...")

        while True:
            current_time = time.time()
            
            # 1. VISION PHASE
            if current_time - last_scan_time > scan_interval:
                try:
                    # Mocking the detection call for the structure
                    detected_coords = detect_all_chests(CHEST_TEMPLATES)
                    before_count = len(manager.active_chests)
                    manager.update_from_vision(detected_coords)
                    after_count = len(manager.active_chests)

                    if after_count > 0:
                        if before_count != after_count:
                            # Print on a new line if the registry actually changes
                            print(f"\n[!] Registry Updated: Tracking {after_count} chest(s)")
                        else:
                            # Generate the dots (1, 2, or 3)
                            dots = "." * dot_count
                            sys.stdout.write(f"\rStatus: {after_count} chest(s) monitored. Scanning{dots}   ")
                            sys.stdout.flush()
                            
                            # Cycle: 1 -> 2 -> 3 -> 1
                            dot_count = (dot_count % 3) + 1
                    else:
                        sys.stdout.write(f"\rStatus: No chests detected. Searching{'.' * dot_count}   ")
                        sys.stdout.flush()
                        dot_count = (dot_count % 3) + 1

                except Exception as e:
                    # Useful for debugging if vision fails
                    print(f"Error: {e}")
                    pass

                last_scan_time = current_time
            
            # Small sleep to prevent CPU hogging while waiting for the next scan interval
            time.sleep(0.1)

            # 2. ANALYSIS & EXECUTION PHASE
            active_chests = manager.get_active_chests()
            for chest in active_chests:
                try:
                    # Chest now internally uses the bridge we injected at creation
                    if chest.is_bouncing(LOWER_MOVEMENT_THRESHOLD, HIGHER_MOVEMENT_THRESHOLD):
                        log_event("Bounce confirmed", chest, chest.movement_score)

                        # 3. CLEANER CALL: Chest now knows how to click itself via bridge
                        chest.click()
                        log_event("Clicked", chest)
                except Exception as bounce_err:
                    print(f"Error checking bounce: {bounce_err}")

            # 3. UTILITY PHASE (Pop-ups)
            if current_time - last_popup_check > popup_interval:
                try:
                    clicked_window_pop = bridge.locate_and_click(os.path.join(TEMPLATES_DIR, "window_pop.jpg"))
                    clicked_got_it = bridge.locate_and_click(os.path.join(TEMPLATES_DIR, "got_it.jpg"))
                    clicked_woohoo = bridge.locate_and_click(os.path.join(TEMPLATES_DIR, "woohoo.jpg"))

                    if clicked_window_pop or clicked_got_it or clicked_woohoo:
                        print("System: Cleared a pop-up window.")
                        for c in active_chests:
                            c.previous_frame = None
                        time.sleep(1)
                except Exception:
                    pass
                last_popup_check = current_time

            # 4. LIKE PHASE
            if with_likes and likes_given_current_stream < MAX_LIKES_PER_STREAM:
                if current_time - last_like_time > LIKE_COOLDOWN:
                    # Check if any chest is close to popping
                    is_critical = any(c.bounce_streak >= 2 for c in active_chests)
                    if not is_critical:
                        if bridge.locate_and_click(LIKE_BUTTON_PATH):
                            likes_given_current_stream += 1
                            last_like_time = current_time
                            print(f"Likes: {likes_given_current_stream}/{MAX_LIKES_PER_STREAM}")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nInitiating graceful shutdown...")
    finally:
        print("Chest Hunter has stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chest Hunter Agent")
    parser.add_argument("--with-likes", action="store_true", default=False)
    args = parser.parse_args()
    main(with_likes=args.with_likes)