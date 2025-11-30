import os

from mlops.config import IRRIGATION_MODEL_DIR
from mlops.utils import create_version_dir, version_models
from src.Irrigation_Model import IrrigationModel


def train_irrigation():
    """Train irrigation model, save a versioned snapshot, and return (acc, version_dir)."""
    print("🌱 Training IRRIGATION model...")

    model = IrrigationModel()
    acc = model.train()

    if acc is None:
        # Defensive: if training skipped due to empty dataset
        print("⚠ Irrigation training returned None (possibly empty dataset).")
        return 0.0, None

    print(f"🌱 Irrigation accuracy: {acc:.4f}")

    # Save a version folder with timestamp + accuracy
    version_dir = create_version_dir(IRRIGATION_MODEL_DIR, acc)
    version_models(IRRIGATION_MODEL_DIR, version_dir)

    return acc, version_dir
