import time
import sys
import os
import argparse
from log import log_event
from tools.vision import detect_all_chests
from tools.chest_class import ChestManager
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

    # Dependency Injection
    manager = ChestManager(bridge=bridge, distance_threshold=50, max_idle_time=25.0)

    last_scan_time = 0
    scan_interval = 1.0
    last_popup_check = 0
    popup_interval = 5.0

    # Initialize to a dynamic safe point (Current time minus cooldown guarantees immediate first run readiness)
    last_like_time = time.time() - LIKE_COOLDOWN - 1.0
    dot_count = 1

    # --- IDLE AUTO-SHUTDOWN TRACKER ---
    idle_start_time = None
    IDLE_TIMEOUT = 300  # 5 minutes in seconds

    try:
        print(f"Initializing Vision System... [Likes Enabled: {with_likes}]")

        while True:
            current_time = time.time()
            active_chests = manager.get_active_chests()

            # 1. VISION PHASE
            if current_time - last_scan_time > scan_interval:
                try:
                    detected_coords = detect_all_chests(CHEST_TEMPLATES)
                    before_count = len(manager.active_chests)
                    manager.update_from_vision(detected_coords)
                    after_count = len(manager.active_chests)

                    if after_count > 0:
                        # Reset idle timer immediately whenever chests are active
                        idle_start_time = None

                        if before_count != after_count:
                            log_event(f"Registry Updated: Tracking {after_count} chest(s)")
                        else:
                            dots = "." * dot_count
                            sys.stdout.write(f"\rStatus: {after_count} chest(s) monitored. Scanning{dots}   ")
                            sys.stdout.flush()
                            dot_count = (dot_count % 3) + 1
                    else:
                        # Start tracking idle duration if no chests are visible
                        if idle_start_time is None:
                            idle_start_time = current_time

                        elapsed_idle = int(current_time - idle_start_time)
                        remaining_time = max(0, IDLE_TIMEOUT - elapsed_idle)

                        dots = "." * dot_count
                        sys.stdout.write(
                            f"\rStatus: No chests detected. Searching{dots} "
                            f"(Auto-off in {remaining_time}s)   "
                        )
                        sys.stdout.flush()
                        dot_count = (dot_count % 3) + 1

                        # AUTO-SHUTDOWN TRIGGER
                        if elapsed_idle >= IDLE_TIMEOUT:
                            print()  # Clear line from carriage return \r status
                            log_event("SYSTEM | No chests detected for 5 minutes. Executing automatic shutdown.")
                            break

                except Exception as e:
                    log_event(f"Error in vision loop: {e}")

                last_scan_time = current_time
            
            # 2. ANALYSIS & EXECUTION PHASE
            for chest in active_chests:
                try:
                    if chest.is_bouncing(LOWER_MOVEMENT_THRESHOLD, HIGHER_MOVEMENT_THRESHOLD):
                        log_event("Bounce confirmed", chest, chest.movement_score)
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
                if current_time - last_like_time >= LIKE_COOLDOWN:
                    # Check if any chest is close to popping
                    is_critical = any(c.bounce_streak >= 2 for c in active_chests)
                    if not is_critical:
                        if bridge.locate_and_click(LIKE_BUTTON_PATH, is_like=True):
                            likes_given_current_stream += 1
                            last_like_time = current_time
                            print(f"\nLikes: {likes_given_current_stream}/{MAX_LIKES_PER_STREAM}")
                        else:
                            # If vision fails to match it, update timer slightly so it doesn't slam CPU on every loop frame
                            last_like_time = current_time - (LIKE_COOLDOWN - 2.0)

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nInitiating graceful shutdown...")
    finally:
        print("Chest Hunter has stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chest Hunter Agent")
    parser.add_argument("--with-likes", action="store_true", default=False)
    args = parser.parse_args()
    
    # Fallback check: force true if wrapper command skips flag parsing
    main(with_likes=args.with_likes)