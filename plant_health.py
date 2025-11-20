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
# LOGGING (Shown in Thonny)
# -------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class PlantHealthModel:

    def __init__(self, dataset="plant_health_data.csv", model_file="plant_health_svm.pkl"):
        self.dataset = dataset
        self.model_file = model_file
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()   # For Plant_Health_Status

        logging.info("PlantHealthModel initialized.")

    # ------------------------------------------------
    def load_dataset(self):
        """Load dataset and clean unnecessary columns."""
        df = pd.read_csv(self.dataset)

        # Drop unwanted columns
        for col in ["Unnamed: 0", "Soil_pH"]:
            if col in df.columns:
                df = df.drop(columns=[col])

        logging.info(f"Dataset loaded with shape {df.shape}.")
        return df

    # ------------------------------------------------
    def preprocess(self, df):
        """Encode target + scale numeric features."""
        df = df.copy()

        # Encode target labels
        df["Plant_Health_Status"] = self.label_encoder.fit_transform(
            df["Plant_Health_Status"]
        )

        X = df.drop(columns=["Plant_Health_Status"])
        y = df["Plant_Health_Status"]

        # Scale features
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
        logging.info("\n" + classification_report(y_test, preds))

        # Save everything
        joblib.dump(self.model, self.model_file)
        joblib.dump(self.scaler, "plant_health_scaler.pkl")
        joblib.dump(self.label_encoder, "plant_health_encoder.pkl")

        return acc

    # ------------------------------------------------
    def predict(self, soil_moisture, temp, humidity,
                light, nitrogen, phosphorus, potassium):

        """Predict plant health with trained SVM."""
        # Load saved objects if needed
        if self.model is None:
            self.model = joblib.load(self.model_file)
            self.scaler = joblib.load("plant_health_scaler.pkl")
            self.label_encoder = joblib.load("plant_health_encoder.pkl")

        df = pd.DataFrame([{
            "Soil_Moisture": soil_moisture,
            "Ambient_Temperature": temp,
            "Humidity": humidity,
            "Light_Intensity": light,
            "Nitrogen_Level": nitrogen,
            "Phosphorus_Level": phosphorus,
            "Potassium_Level": potassium
        }])

        # Scale numeric features
        X_scaled = self.scaler.transform(df)

        pred = self.model.predict(X_scaled)[0]
        label = self.label_encoder.inverse_transform([pred])[0]

        logging.info(f"Prediction: {label}")
        return label

    # ------------------------------------------------
    def retrain(self):
        """Retrain using updated dataset."""
        logging.info("Retraining started...")
        return self.train()



