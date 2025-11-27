import os
import sys
import shutil
import subprocess

# -----------------------------------------
# FIX: Add project root to import path
# -----------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from mlops.config import timestamp, GITHUB_TOKEN, GITHUB_USERNAME, PROJECT_ROOT


# --------------------------
# Create Version Folder
# --------------------------
def create_version_dir(base_path):
    version_dir = os.path.join(base_path, "versions", timestamp())
    os.makedirs(version_dir, exist_ok=True)
    return version_dir


# --------------------------
# Copy: current → versioned
# --------------------------
def version_models(current_path, version_dir):
    for file in os.listdir(current_path):
        src = os.path.join(current_path, file)
        dst = os.path.join(version_dir, file)
        shutil.copy2(src, dst)


# --------------------------
# Save model to current/
# --------------------------
def save_current_model(src_files, current_dir):
    os.makedirs(current_dir, exist_ok=True)
    for src in src_files:
        shutil.copy2(src, current_dir)


# --------------------------
# Git Auto Commit + Push
# --------------------------
def git_commit_and_push(message):
    if not GITHUB_TOKEN:
        print("⚠ No GITHUB_TOKEN environment variable! Skipping push.")
        return

    try:
        subprocess.run(["git", "config", "user.email", "ci@circleci.com"])
        subprocess.run(["git", "config", "user.name", "CircleCI Bot"])

        subprocess.run(["git", "add", "models/"])
        subprocess.run(["git", "add", "data/"])
        subprocess.run(["git", "commit", "-m", message], check=False)

        repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/Smart-Farming-AI-System.git"
        subprocess.run(["git", "push", repo_url], check=False)

        print("✔ Models pushed to GitHub.")

    except Exception as e:
        print("❌ Git push failed:", e)
