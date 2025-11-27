import os
from mlops.config import DATA_PATH, PLANT_MODEL_DIR
from mlops.utils import create_version_dir, version_models, save_current_model, git_commit_and_push
from src.plant_health import PlantHealthModel

def train_plant_health():

    print("🌿 Training PLANT HEALTH model...")

    csv_path = os.path.join(DATA_PATH, "plant_health_data.csv")

    model = PlantHealthModel()
    model.train_from_csv(csv_path)

    # Save new model
    model_files = model.save_all(PLANT_MODEL_DIR)

    # Versioning
    version_dir = create_version_dir(PLANT_MODEL_DIR)
    version_models(os.path.join(PLANT_MODEL_DIR, "current"), version_dir)

    # Push to GitHub
    git_commit_and_push("Updated plant health model")

    print("✔ PLANT HEALTH retraining complete.")
