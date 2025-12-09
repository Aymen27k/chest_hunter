import sys, os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller binary."""
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    # Running from source
    return os.path.join(os.path.abspath("."), relative_path)

TEMPLATES_DIR = resource_path("chest_templates")

# Thresholds
THRESHOLD_VALUE = 50
LOWER_MOVEMENT_THRESHOLD = 550
HIGHER_MOVEMENT_THRESHOLD = 1200

# Likes feature
LIKE_BUTTON_PATH = os.path.join(TEMPLATES_DIR, "like.jpg")
MAX_LIKES_PER_STREAM = 20
LIKE_COOLDOWN = 7

# Chest templates
CHEST_TEMPLATES = [
    os.path.join(TEMPLATES_DIR, "still_chest_player.jpg"),
    os.path.join(TEMPLATES_DIR, "chest_x10.jpg"),
    os.path.join(TEMPLATES_DIR, "small_chest.jpg"),
    os.path.join(TEMPLATES_DIR, "chest_x10_2.jpg"),
    os.path.join(TEMPLATES_DIR, "still_chest_x3.jpg"),
    os.path.join(TEMPLATES_DIR, "chest_x5.jpg"),
    os.path.join(TEMPLATES_DIR, "chest_regular.jpg"),
    os.path.join(TEMPLATES_DIR, "chest_x4.jpg"),
    os.path.join(TEMPLATES_DIR, "chest_x7.jpg"),
    os.path.join(TEMPLATES_DIR, "chest_50.jpg"),
    os.path.join(TEMPLATES_DIR, "chest_x8.jpg"),
]
