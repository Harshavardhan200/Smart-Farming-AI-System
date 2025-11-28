import time
import json
import logging
from datetime import datetime

from src.Irrigation_Model import IrrigationModel
from src.plant_health import PlantHealthModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from sensors_ads import SensorADS
from npk_sensor import NPKSensor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ======================================================
# Load Models
# ======================================================
irrigation_model = IrrigationModel(
    dataset_path="data/irrigation.csv",
    model_path="models/irrigation/current/irrigation_model.pkl",
    scaler_path="models/irrigation/current/irrigation_scaler.pkl",
    encoder_path="models/irrigation/current/irrigation_encoders.pkl"
)

plant_model = PlantHealthModel(
    dataset_path="data/plant_health_data.csv",
    model_path="models/plant_health/current/plant_health_svm.pkl",
    scaler_path="models/plant_health/current/plant_health_scaler.pkl",
    encoder_path="models/plant_health/current/plant_health_encoder.pkl"
)

# Offline LLM (FLAN-T5 Small)
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
llm_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

# Sensors
ads = SensorADS()
npk = NPKSensor(port="/dev/ttyUSB0")  # optional

# ======================================================
# Inference Loop
# ======================================================
while True:
    try:
        # Read sensors
        temperature, humidity = ads.read_temp_humidity()
        moisture = ads.read_soil_moisture()
        light = ads.read_light_intensity()

        n, p, k = npk.read_npk() if npk else (None, None, None)

        # Predictions
        irrigation_pred = irrigation_model.predict([
            temperature, humidity, moisture, light
        ])

        plant_pred = plant_model.predict([
            temperature, humidity, moisture, light, n, p, k
        ])

        # LLM response
        prompt = (
            f"Temperature: {temperature}C, Humidity: {humidity}%, "
            f"Soil moisture: {moisture}%, Light: {light} lux. "
            f"NPK: {n},{p},{k}. "
            f"Irrigation needed: {irrigation_pred}. "
            f"Plant health: {plant_pred}. "
            "Give a short farming recommendation."
        )

        inputs = tokenizer(prompt, return_tensors="pt")
        output = llm_model.generate(**inputs, max_length=80)
        advisory = tokenizer.decode(output[0], skip_special_tokens=True)

        # Logging
        log = {
            "timestamp": str(datetime.now()),
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": moisture,
            "light": light,
            "n": n,
            "p": p,
            "k": k,
            "irrigation_needed": irrigation_pred,
            "plant_health": plant_pred,
            "advice": advisory
        }

        with open("data/live_log.json", "a") as f:
            f.write(json.dumps(log) + "\n")

        logging.info(f"LOGGED: {log}")

    except Exception as e:
        logging.error(f"Error in inference loop: {e}")

    time.sleep(10)
