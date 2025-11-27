import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# -----------------------------
# PROJECT ROOT PATH
# -----------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATH = os.path.join(PROJECT_ROOT, "data")
MODELS_PATH = os.path.join(PROJECT_ROOT, "models")

# -----------------------------
# MODEL SUB-FOLDERS
# -----------------------------
IRRIGATION_MODEL_DIR = os.path.join(MODELS_PATH, "irrigation")
PLANT_MODEL_DIR = os.path.join(MODELS_PATH, "plant_health")

# GitHub username
GITHUB_USERNAME = "Harshavardhan200"

# Set from CircleCI variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# -----------------------------
# TIMESTAMP FOR VERSION FOLDER
# -----------------------------
def timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
