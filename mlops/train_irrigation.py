import os
from mlops.config import DATA_PATH, IRRIGATION_MODEL_DIR
from mlops.utils import create_version_dir, version_models, save_current_model, git_commit_and_push
from src.Irrigation_Model import IrrigationModel

def train_irrigation():

    print("🌱 Training IRRIGATION model...")

    csv_path = os.path.join(DATA_PATH, "irrigation.csv")

    model = IrrigationModel()
    model.train_from_csv(csv_path)

    # -------------------------
    # SAVE NEW MODEL FILES
    # -------------------------
    model_files = model.save_all(IRRIGATION_MODEL_DIR)  
    # Your IrrigationModel should implement save_all()

    # -------------------------
    # VERSIONING
    # -------------------------
    version_dir = create_version_dir(IRRIGATION_MODEL_DIR)
    version_models(os.path.join(IRRIGATION_MODEL_DIR, "current"), version_dir)

    # -------------------------
    # COMMIT TO GITHUB
    # -------------------------
    git_commit_and_push("Updated irrigation model")

    print("✔ IRRIGATION retraining complete.")
