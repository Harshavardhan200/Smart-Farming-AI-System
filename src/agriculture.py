import time
import json
import ssl
import logging
import random
import os
import paho.mqtt.client as mqtt

# Local imports
from npk_sensor import NPKSensor
from sensors_ads import SensorADS
from Irrigation_Model import IrrigationModel
from plant_health import PlantHealthModel

# ======================================================
# CONFIG
# ======================================================
USE_SIMULATION = False    # True = fake data, False = real sensors
NPK_ENABLED = False       # Enable only if RS485 NPK sensor connected

# ======================================================
# LOGGING
# ======================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ======================================================
# MQTT SETTINGS
# ======================================================
MQTT_BROKER = "8c70285096fe43429db68ea8e5513422.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
USERNAME = "hivemq.webclient.1763167024884"
PASSWORD = "!A5PgmOd1MS$<7z9X#bf"

TOPIC_SENSOR = "agriedge/sensor"
TOPIC_ADVICE = "agriedge/advice"

# ======================================================
# SENSOR SETUP
# ======================================================
if not USE_SIMULATION:
    sensor = SensorADS()   # ADS1115 + DHT11 wrapper

    if NPK_ENABLED:
        npk = NPKSensor(port="/dev/ttyS0", slave_id=1)

# ======================================================
# MQTT CLIENT INITIALIZATION
# ======================================================
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

logging.info("Connecting to HiveMQ Cloud...")
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
client.loop_start()
logging.info("MQTT Connected and Publishing Enabled.")

# ======================================================
# LOAD ML MODELS WITH CORRECT PATH
# ======================================================
logging.info("Loading ML models...")

# FIXED PATHS → do NOT pass simple file names
irrigation_model = IrrigationModel("data/irrigation.csv")
irrigation_model.train()

plant_model = PlantHealthModel("data/plant_health_data.csv")
plant_model.train()

logging.info("Irrigation & Plant Health Models Loaded Successfully.")

# ======================================================
# LLM DISABLED (COMMENTED OUT SAFELY)
# ======================================================

"""
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logging.info("Loading Hugging Face flan-t5-small...")

model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
hf_model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cpu")

logging.info("LLM Loaded Successfully.")
"""

# ======================================================
# MAIN LOOP
# ======================================================
logging.info("System Running...")

while True:
    try:
        # ---------------------------------------------------
        # SENSOR READINGS
        # ---------------------------------------------------
        if USE_SIMULATION:
            temperature = round(random.uniform(22, 29), 2)
            humidity = round(random.uniform(40, 70), 2)
            soil_moisture = round(random.uniform(10, 75), 2)
            light = random.randint(200, 900)
            nitrogen = random.randint(10, 40)
            phosphorus = random.randint(10, 40)
            potassium = random.randint(10, 40)

        else:
            readings = sensor.read_all()
            temperature = readings["temperature"]
            humidity = readings["humidity"]
            soil_moisture = readings["moi"]
            light = readings["lux"]

            if NPK_ENABLED:
                nitrogen, phosphorus, potassium = npk.read_npk()
                if nitrogen is None:
                    nitrogen, phosphorus, potassium = 20, 15, 18
            else:
                nitrogen, phosphorus, potassium = 20, 15, 18

        # ---------------------------------------------------
        # ML MODEL PREDICTIONS
        # ---------------------------------------------------
        soil_type = "Black Soil"
        stage = "Germination"

        irrigation_pred, moisture_percent = irrigation_model.predict(
            soil_type=soil_type,
            stage=stage,
            moi_raw=soil_moisture,
            temp=temperature,
            humidity=humidity
        )

        plant_pred = plant_model.predict(
            soil_moisture=moisture_percent,
            temp=temperature,
            humidity=humidity,
            light=light,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium
        )

        logging.info(f"Irrigation Need: {irrigation_pred}")
        logging.info(f"Plant Health: {plant_pred}")

        # ---------------------------------------------------
        # MQTT PUBLISH
        # ---------------------------------------------------
        payload = {
            "temperature": float(temperature),
            "humidity": float(humidity),
            "moisture": float(moisture_percent),
            "light": int(light),
            "nitrogen": int(nitrogen),
            "phosphorus": int(phosphorus),
            "potassium": int(potassium),
            "irrigation_prediction": int(irrigation_pred),
            "plant_health_prediction": str(plant_pred),
            "timestamp": float(time.time())
        }

        client.publish(TOPIC_SENSOR, json.dumps(payload))
        logging.info("MQTT Published Sensor Data")
        logging.info("---------------------------")

    except Exception as e:
        logging.error(f"Error: {e}")

    time.sleep(10)
        # ---------------------------------------------------
        # LLM ADVICE
        # ---------------------------------------------------
        prompt = f"""
You are an agricultural expert AI system.

Sensor Inputs:
- Soil Type: {soil_type}
- Growth Stage: {stage}
- Soil Moisture: {moisture_percent}
- Temperature: {temperature}
- Humidity: {humidity}
- Light: {light}
- Nitrogen: {nitrogen}
- Phosphorus: {phosphorus}
- Potassium: {potassium}

ML Predictions:
- Irrigation Required (0/1): {irrigation_pred}
- Plant Health: {plant_pred}

Generate detailed guidance for irrigation, plant health, NPK balance, shade/light corrections, next 3–5 day care plan, warning signs, and prevention.
"""

        #inputs = tokenizer(prompt, return_tensors="pt")
        #outputs = hf_model.generate(**inputs, max_length=250)
        #advice = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # ---------------------------------------------------
        # MQTT PUBLISH
        # ---------------------------------------------------
        payload = {
            "temperature": float(temperature),
            "humidity": float(humidity),
            "moisture": float(moisture_percent),
            "light": int(light),
            "nitrogen": int(nitrogen),
            "phosphorus": int(phosphorus),
            "potassium": int(potassium),
            "irrigation_prediction": int(irrigation_pred),
            "plant_health_prediction": str(plant_pred),
            "timestamp": float(time.time())
        }

        client.publish(TOPIC_SENSOR, json.dumps(payload))
        #client.publish(TOPIC_ADVICE, str(advice))

        logging.info("MQTT Published Sensor Data + Advice")
        logging.info("---------------------------")
        #logging.info(advice)
        logging.info("---------------------------")

    except Exception as e:
        logging.error(f"Error: {e}")

    time.sleep(10)
