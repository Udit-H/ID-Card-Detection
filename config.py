# config.py
detection_running = False

import os

OCCUPANCY_FILE = "occupancy.txt"

def load_occupancy():
    if os.path.exists(OCCUPANCY_FILE):
        with open(OCCUPANCY_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_occupancy(value):
    with open(OCCUPANCY_FILE, "w") as f:
        f.write(str(value))

occupancy = load_occupancy()
