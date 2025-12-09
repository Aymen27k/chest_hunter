import logging

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File handler (writes to hunter_log.txt)
file_handler = logging.FileHandler("hunter_log.txt")
file_handler.setLevel(logging.INFO)

# Console handler (prints to terminal)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Common format
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def log_event(event, chest=None, score=None):
    if chest and score is not None:
        logger.info(f"{event} | Chest={chest.template} | Score={score}")
    elif chest:
        logger.info(f"{event} | Chest={chest.template}")
    else:
        logger.info(event)
