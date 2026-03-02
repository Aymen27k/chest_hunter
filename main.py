import time
import os
import argparse
from log import log_event
from tools.vision import detect_all_chests
from tools.chest_class import ChestManager
from tools.utils import item_location_clicking
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
    # Debug print to verify argument passing
    print(f"DEBUG: Internal 'with_likes' state is: {with_likes}")
    
    likes_given_current_stream = 0
    manager = ChestManager(distance_threshold=50, max_idle_time=15.0)

    last_scan_time = 0
    scan_interval = 2.0

    last_popup_check = 0
    popup_interval = 5.0

    # Track the last time a like was given
    last_like_time = 0 

    try:
        print("Chest Hunter active. Monitoring for chests...")
        
        while True:
            current_time = time.time()

            # 1. VISION PHASE: Update the registry of where chests are
            if current_time - last_scan_time > scan_interval:
                try:
                    detected_coords = detect_all_chests(CHEST_TEMPLATES)
                    before_count = len(manager.active_chests)
                    manager.update_from_vision(detected_coords)
                    after_count = len(manager.active_chests)

                    if after_count > 0:
                        if before_count != after_count:
                            print(f"Registry Updated: Tracking {after_count} chest(s)")
                        else:
                            print(f"Status: {after_count} chest(s) monitored. Scanning for movement...")
                except Exception:
                    pass
                last_scan_time = current_time

            # 2. ANALYSIS PHASE: Check movement for every chest in the registry
            active_chests = manager.get_active_chests()
            for chest in active_chests:
                try:
                    # Note: using chest.required_streak if available, otherwise defaulting to a safe number like 3
                    req = getattr(chest, 'required_streak', 3)
                    if chest.is_bouncing(LOWER_MOVEMENT_THRESHOLD, HIGHER_MOVEMENT_THRESHOLD):
                        log_event("Bounce confirmed via streak", chest, chest.movement_score)
                        print(f"!!! BOUNCE DETECTED on {chest.template} (Score: {chest.movement_score:.2f}) !!!")
                        chest.click(chest.movement_score)
                        log_event("Clicked", chest)
                except Exception as bounce_err:
                    print(f"Error checking bounce: {bounce_err}")

            # 3. UTILITY PHASE: Independent Pop-up Scan
            if current_time - last_popup_check > popup_interval:
                try:
                    clicked_window_pop = item_location_clicking(os.path.join(TEMPLATES_DIR, "window_pop.jpg"))
                    clicked_got_it = item_location_clicking(os.path.join(TEMPLATES_DIR, "got_it.jpg"))
                    clicked_woohoo = item_location_clicking(os.path.join(TEMPLATES_DIR, "woohoo.jpg"))

                    if clicked_window_pop or clicked_got_it or clicked_woohoo:
                        print("System: Cleared a pop-up window.")
                        for c in active_chests:
                            c.previous_frame = None
                        time.sleep(1)
                except Exception:
                    pass
                last_popup_check = current_time

            # 4. LIKE PHASE (Optimized Non-Blocking)
            if with_likes and likes_given_current_stream < MAX_LIKES_PER_STREAM:
                # Check if cooldown has passed
                if current_time - last_like_time > LIKE_COOLDOWN:
                    
                    # RELAXED CHECK: Only block likes if a chest is very close to triggering (streak >= required-1)
                    # This prevents the "numbness" where 1 frame of noise stops likes forever.
                    is_critical_moment = any(c.bounce_streak >= (getattr(c, 'required_streak', 3) - 1) for c in active_chests)
                    
                    if not is_critical_moment:
                        if item_location_clicking(LIKE_BUTTON_PATH):
                            likes_given_current_stream += 1
                            last_like_time = current_time 
                            print(f"Likes: {likes_given_current_stream}/{MAX_LIKES_PER_STREAM}")
            
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nInitiating graceful shutdown...")
    finally:
        print("Chest Hunter has stopped.")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Chest Hunter Agent")
        parser.add_argument(
            "--with-likes",
            action="store_true",
            default=False,
            help="Enable automatic likes during the stream"
        )
        args = parser.parse_args()
        
        # Explicit print before calling main
        print(f"CLI Arguments received: {args}")
        main(with_likes=args.with_likes)
    except KeyboardInterrupt:
        print("\nChest Hunter terminated by user. Goodbye.")