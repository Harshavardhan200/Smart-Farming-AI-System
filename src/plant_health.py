import pandas as pd
import numpy as np
import joblib
import logging
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# -------------------------------------
# LOGGING
# -------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class PlantHealthModel:

    def __init__(self,
                 dataset="data/plant_health_data.csv",
                 model_file="models/plant_health/plant_health_svm.pkl"):

        # Determine project root (one level above src/)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Build absolute paths
        self.dataset = os.path.join(BASE_DIR, dataset)
        self.model_file = os.path.join(BASE_DIR, model_file)

        self.scaler_file = os.path.join(BASE_DIR, "models/plant_health/plant_health_scaler.pkl")
        self.encoder_file = os.path.join(BASE_DIR, "models/plant_health/plant_health_encoder.pkl")

        # Create model directory if missing
        os.makedirs(os.path.join(BASE_DIR, "models/plant_health"), exist_ok=True)

        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

        logging.info(f"PlantHealthModel initialized with dataset: {self.dataset}")

    # ------------------------------------------------
    def load_dataset(self):
        """Load dataset and clean unnecessary columns."""
        df = pd.read_csv(self.dataset)

        # Remove unused columns if present
        for col in ["Unnamed: 0", "Soil_pH"]:
            if col in df.columns:
                df = df.drop(columns=[col])

        #logging.info(f"Dataset loaded with shape {df.shape}.")
        return df

    # ------------------------------------------------
    def preprocess(self, df):
        """Encode label + scale numeric features."""
        df = df.copy()

        # Encode target labels
        df["Plant_Health_Status"] = self.label_encoder.fit_transform(
            df["Plant_Health_Status"]
        )

        X = df.drop(columns=["Plant_Health_Status"])
        y = df["Plant_Health_Status"]

        X_scaled = self.scaler.fit_transform(X)

        return X_scaled, y

    # ------------------------------------------------
    def train(self):
        """Train SVM classifier."""
        df = self.load_dataset()
        X, y = self.preprocess(df)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model = SVC(kernel="rbf", probability=True)
        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)
        acc = accuracy_score(y_test, preds)

        logging.info(f"Training complete. Accuracy = {acc}")
        #logging.info("\n" + classification_report(y_test, preds))

        # Save all components
        joblib.dump(self.model, self.model_file)
        joblib.dump(self.scaler, self.scaler_file)
        joblib.dump(self.label_encoder, self.encoder_file)

        return acc

    # ------------------------------------------------
    def predict(self, soil_moisture, temp, humidity,
                light, nitrogen, phosphorus, potassium):
        """Predict plant health with trained SVM."""

        # Load saved model/scaler/encoder if not in memory
        if self.model is None:
            self.model = joblib.load(self.model_file)
            self.scaler = joblib.load(self.scaler_file)
            self.label_encoder = joblib.load(self.encoder_file)

        df = pd.DataFrame([{
            "Soil_Moisture": soil_moisture,
            "Ambient_Temperature": temp,
            "Humidity": humidity,
            "Light_Intensity": light,
            "Nitrogen_Level": nitrogen,
            "Phosphorus_Level": phosphorus,
            "Potassium_Level": potassium
        }])

        # Scale input
        X_scaled = self.scaler.transform(df)

        pred = self.model.predict(X_scaled)[0]
        label = self.label_encoder.inverse_transform([pred])[0]

        logging.info(f"Prediction: {label}")
        return label

    # ------------------------------------------------
    def retrain(self):
        """Auto retrain on updated dataset."""
        #logging.info("Retraining started...")
        return self.train()
        # ------------------------------------------------
    def train_from_csv(self, path):
        """Train from external CSV (used by CI/CD)."""
        self.dataset = path
        return self.train()

    # ------------------------------------------------
    def save_all(self, base_dir):
        """Save plant health model into /current/ directory."""
        current_dir = os.path.join(base_dir, "current")
        os.makedirs(current_dir, exist_ok=True)

        model_out = os.path.join(current_dir, "plant_health_svm.pkl")
        scaler_out = os.path.join(current_dir, "plant_health_scaler.pkl")
        encoder_out = os.path.join(current_dir, "plant_health_encoder.pkl")

        joblib.dump(self.model, model_out)
        joblib.dump(self.scaler, scaler_out)
        joblib.dump(self.label_encoder, encoder_out)

        return [model_out, scaler_out, encoder_out]

    # ------------------------------------------------
    @staticmethod
    def load_current():
        """Load model for inference on Raspberry Pi."""
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        current_path = os.path.join(BASE_DIR, "models/plant_health/current")

        model = joblib.load(os.path.join(current_path, "plant_health_svm.pkl"))
        scaler = joblib.load(os.path.join(current_path, "plant_health_scaler.pkl"))
        encoder = joblib.load(os.path.join(current_path, "plant_health_encoder.pkl"))

        obj = PlantHealthModel()
        obj.model = model
        obj.scaler = scaler
        obj.label_encoder = encoder
        return obj
