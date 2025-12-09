import time
import os
import argparse
from log import log_event
from tools.vision import detect_chests
from tools.chest_class import Chest
from tools.utils import item_location_clicking
from tools.config import CHEST_TEMPLATES, LOWER_MOVEMENT_THRESHOLD, HIGHER_MOVEMENT_THRESHOLD, TEMPLATES_DIR, MAX_LIKES_PER_STREAM, LIKE_BUTTON_PATH, LIKE_COOLDOWN

def main(with_likes=False):
    likes_given_current_stream = 0
    try:
        chests: list[Chest] = detect_chests(CHEST_TEMPLATES)
        while True:
            for chest in chests:
                print(f"Testing chest {chest.template} at {chest.coords}")          
                if chest.is_bouncing(LOWER_MOVEMENT_THRESHOLD, HIGHER_MOVEMENT_THRESHOLD):
                    log_event("Bounce detected", chest, chest.movement_score)
                    print("Bounce detected → clicking")
                    chest.click()
                    log_event("Clicked", chest)
                else:
                    print("No bounce detected")

                    # Handle pop-ups
                    clicked_window_pop = item_location_clicking(os.path.join(TEMPLATES_DIR, "window_pop.jpg"))
                    clicked_got_it = item_location_clicking(os.path.join(TEMPLATES_DIR, "got_it.jpg"))
                    clicked_woohoo = item_location_clicking(os.path.join(TEMPLATES_DIR, "woohoo.jpg"))

                    if clicked_window_pop or clicked_got_it or clicked_woohoo:
                        print("One or more pop-up buttons were found and clicked. Adding a short delay.")
                        time.sleep(1)

                    # Handle likes if enabled
                    if with_likes and likes_given_current_stream < MAX_LIKES_PER_STREAM:
                        if item_location_clicking(LIKE_BUTTON_PATH):
                            likes_given_current_stream += 1
                            print(f"Given {likes_given_current_stream}/{MAX_LIKES_PER_STREAM} likes in this stream.")
                            time.sleep(LIKE_COOLDOWN)

                    # Small delay to avoid CPU overload
                    time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nCtrl+C detected! Initiating graceful shutdown...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Chest Hunter has stopped gracefully.")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Chest Hunter Agent")
        parser.add_argument(
            "--with-likes",
            action="store_true",
            help="Enable automatic likes during the stream"
        )
        args = parser.parse_args()

        main(with_likes=args.with_likes)
    except KeyboardInterrupt:
        # suppress traceback here
        print("\nChest Hunter terminated by user. Goodbye.")