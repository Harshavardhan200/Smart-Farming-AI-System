import os
import shutil
import subprocess
from datetime import datetime
import json

# =========================================
# TIMESTAMP
# =========================================
def timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# =========================================
# VERSION FOLDER (INCLUDES ACCURACY)
# =========================================
def create_version_dir(model_dir, acc: float):
    """
    Create a version folder:
    models/.../versions/YYYY-MM-DD_HH-MM-SS_acc_0.9523/
    """
    folder = f"{timestamp()}_acc_{acc:.4f}"
    version_dir = os.path.join(model_dir, "versions", folder)
    os.makedirs(version_dir, exist_ok=True)
    return version_dir


# =========================================
# COPY MODELS INTO VERSION FOLDER
# =========================================
def version_models(current_dir, version_dir):
    """
    Copy the contents of 'current/' into a versioned folder.
    """
    if not os.path.exists(current_dir):
        print(f"⚠ ERROR: Current model folder does not exist: {current_dir}")
        return

    os.makedirs(version_dir, exist_ok=True)
    for file in os.listdir(current_dir):
        src = os.path.join(current_dir, file)
        dst = os.path.join(version_dir, file)
        shutil.copy2(src, dst)

    print(f"📦 Saved versioned model → {version_dir}")


# =========================================
# ROLLBACK FUNCTIONS
# =========================================
def rollback_to_previous(model_dir):
    """
    Revert current model to previous version.
    Does NOT delete the latest version.
    """
    versions_path = os.path.join(model_dir, "versions")
    if not os.path.exists(versions_path):
        print("⚠ No versions folder found.")
        return False

    versions = sorted(os.listdir(versions_path))
    if len(versions) < 2:
        print("⚠ Not enough versions to rollback.")
        return False

    prev_version = versions[-2]
    src = os.path.join(versions_path, prev_version)
    dst = os.path.join(model_dir, "current")

    print(f"🔄 Rolling back to: {prev_version}")
    shutil.copytree(src, dst, dirs_exist_ok=True)
    return True


# =========================================
# METRICS SAVE / LOAD
# =========================================
def load_last_metrics(path="mlops/last_metrics.json"):
    if not os.path.exists(path):
        print("⚠ No previous metrics found → starting fresh.")
        return {"irrigation_acc": 0, "plant_acc": 0}

    with open(path, "r") as f:
        return json.load(f)


def save_metrics(irrigation_acc, plant_acc, path="mlops/last_metrics.json"):
    data = {
        "irrigation_acc": irrigation_acc,
        "plant_acc": plant_acc,
        "timestamp": timestamp(),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print("📊 Metrics updated.")


# =========================================
# SHOULD WE ROLLBACK?
# =========================================
def should_rollback(prev_acc, new_acc):
    """
    Return True if accuracy dropped.
    """
    return new_acc < prev_acc


# =========================================
# SAFE GIT COMMIT AND PUSH
# =========================================
def git_commit_and_push(message: str):
    """
    Safe push that avoids rejections and works with CircleCI.
    """

    try:
        # Pull latest (avoid conflicts)
        subprocess.run(["git", "pull", "--rebase"], check=False)

        # Add everything needed
        subprocess.run(["git", "add", "."], check=False)

        # Commit
        subprocess.run(["git", "commit", "-m", message], check=False)

        # Push using CircleCI token
        repo_url = os.environ.get("CIRCLE_REPOSITORY_URL")
        github_token = os.environ.get("GITHUB_TOKEN")

        if github_token and repo_url:
            safe_url = repo_url.replace("https://", f"https://{github_token}@")
            subprocess.run(["git", "push", safe_url], check=False)
        else:
            subprocess.run(["git", "push"], check=False)

        print("⬆ Git push complete.")

    except Exception as e:
        print(f"❌ Git push failed: {e}")
