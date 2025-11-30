import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (for GITHUB_TOKEN, etc.)
load_dotenv()

# -----------------------------
# PROJECT ROOT PATH
# -----------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# -----------------------------
# DATA / MODEL PATHS
# -----------------------------
DATA_PATH = os.path.join(PROJECT_ROOT, "data")
MODELS_PATH = os.path.join(PROJECT_ROOT, "models")

# Model sub-folders
IRRIGATION_MODEL_DIR = os.path.join(MODELS_PATH, "irrigation")
PLANT_MODEL_DIR = os.path.join(MODELS_PATH, "plant_health")

# GitHub (used mainly by CI)
GITHUB_USERNAME = "Harshavardhan200"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# -----------------------------
# TIMESTAMP FOR VERSION FOLDER
# -----------------------------
def timestamp() -> str:
    """Return a timestamp string like 2025-11-30_23-59-59."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
