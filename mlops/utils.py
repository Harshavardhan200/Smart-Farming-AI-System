"""
Utility helpers for model versioning, cleanup, reporting, and git integration.
"""
import os
import shutil
import subprocess
from typing import Optional, List
from datetime import datetime

from mlops.config import PROJECT_ROOT, timestamp


# =========================================
# VERSION FOLDER HELPERS
# =========================================
def create_version_dir(model_dir: str, acc: float) -> str:
    """Create a version folder with timestamp + accuracy."""
    folder = f"{timestamp()}_acc_{acc:.4f}"
    version_dir = os.path.join(model_dir, "versions", folder)
    os.makedirs(version_dir, exist_ok=True)
    return version_dir


def version_models(model_dir: str, version_dir: str) -> None:
    """Copy all top-level .pkl files from model_dir into version_dir."""
    os.makedirs(version_dir, exist_ok=True)

    for name in os.listdir(model_dir):
        src = os.path.join(model_dir, name)
        if os.path.isfile(src) and name.endswith(".pkl"):
            dst = os.path.join(version_dir, name)
            shutil.copy2(src, dst)

    print(f"📦 Saved versioned models → {version_dir}")


def list_versions(model_dir: str) -> List[str]:
    versions_root = os.path.join(model_dir, "versions")
    if not os.path.exists(versions_root):
        return []
    return sorted(
        [d for d in os.listdir(versions_root)
         if os.path.isdir(os.path.join(versions_root, d))]
    )


def latest_version_dir(model_dir: str) -> Optional[str]:
    versions = list_versions(model_dir)
    if not versions:
        return None
    return os.path.join(model_dir, "versions", versions[-1])


def set_current_from_version_dir(model_dir: str, version_dir: str) -> None:
    current_dir = os.path.join(model_dir, "current")
    os.makedirs(current_dir, exist_ok=True)
    shutil.copytree(version_dir, current_dir, dirs_exist_ok=True)
    print(f"🔁 Updated current model for {model_dir} from {version_dir}")


# =========================================
# ROLLBACK
# =========================================
def rollback_to_previous(model_dir: str) -> bool:
    versions = list_versions(model_dir)
    if len(versions) < 2:
        print(f"⚠ Not enough versions to rollback in {model_dir}")
        return False

    prev = versions[-2]
    src = os.path.join(model_dir, "versions", prev)
    dst = os.path.join(model_dir, "current")
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"🔄 Rolled back to version {prev}")
    return True


# =========================================
# AUTO-DELETE OLD VERSIONS
# =========================================
def cleanup_old_versions(model_dir: str, keep_last: int = 30) -> None:
    versions_root = os.path.join(model_dir, "versions")
    if not os.path.exists(versions_root):
        return

    versions = sorted(
        [v for v in os.listdir(versions_root)
         if os.path.isdir(os.path.join(versions_root, v))]
    )

    if len(versions) <= keep_last:
        return

    old_versions = versions[:-keep_last]

    for v in old_versions:
        path = os.path.join(versions_root, v)
        shutil.rmtree(path, ignore_errors=True)
        print(f"🧹 Deleted old version: {path}")

    print(f"✔ Cleanup complete (kept last {keep_last}).")


# =========================================
# NIGHTLY MARKDOWN REPORT
# =========================================
def write_nightly_report(
        prev_irr, irr_acc, irr_version_dir, irr_updated,
        prev_plant, plant_acc, plant_version_dir, plant_updated
    ):
    report_dir = os.path.join(PROJECT_ROOT, "reports")
    os.makedirs(report_dir, exist_ok=True)

    report_path = os.path.join(report_dir, "nightly_report.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(report_path, "w") as f:
        f.write(f"# 🌙 Nightly Training Report – {now}\n\n")

        f.write("## Irrigation Model\n")
        f.write(f"- Previous Accuracy: {prev_irr}\n")
        f.write(f"- New Accuracy: {irr_acc}\n")
        f.write(f"- Saved Version: {irr_version_dir}\n")
        f.write(f"- Current Model Updated? {'✅ Yes' if irr_updated else '❌ No'}\n\n")

        f.write("## Plant Health Model\n")
        f.write(f"- Previous Accuracy: {prev_plant}\n")
        f.write(f"- New Accuracy: {plant_acc}\n")
        f.write(f"- Saved Version: {plant_version_dir}\n")
        f.write(f"- Current Model Updated? {'✅ Yes' if plant_updated else '❌ No'}\n\n")

        f.write("---\n")
        f.write("Versions older than 30 were automatically deleted.\n")

    print(f"📝 Nightly report written → {report_path}")
    return report_path


# =========================================
# OPTIONAL GIT PUSH (NOT USED IN CI)
# =========================================
def git_commit_and_push(message: str) -> None:
    """Manual use only."""
    try:
        os.chdir(PROJECT_ROOT)
        subprocess.run(["git", "pull", "--rebase"], check=False)
        subprocess.run(["git", "add", "models/"], check=False)
        subprocess.run(["git", "add", "mlops/last_metrics.json"], check=False)
        subprocess.run(["git", "commit", "-m", message], check=False)
        subprocess.run(["git", "push"], check=False)
        print("⬆ Git push complete.")
    except Exception as exc:
        print(f"❌ Git push failed: {exc}")
