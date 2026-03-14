import os

# Base directory is the parent of the 'modules' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define key directories based on BASE_DIR
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Ensure directories exist
for d in [DATA_DIR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)
