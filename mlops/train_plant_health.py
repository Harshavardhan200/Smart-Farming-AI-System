import os
from mlops.config import DATA_PATH, PLANT_MODEL_DIR
from mlops.utils import create_version_dir, version_models, git_commit_and_push
from src.plant_health import PlantHealthModel

def train_plant_health():

    print("🌿 Training PLANT HEALTH model...")

    csv_path = os.path.join(DATA_PATH, "plant_health_data.csv")

    model = PlantHealthModel()
    acc = model.train_from_csv(csv_path)

    model.save_all(PLANT_MODEL_DIR)

    version_dir = create_version_dir(PLANT_MODEL_DIR, acc)
    version_models(os.path.join(PLANT_MODEL_DIR, "current"), version_dir)

    git_commit_and_push(f"Updated plant health model | acc={acc:.4f}")

    print("✔ PLANT HEALTH retraining complete.")
    return acc
