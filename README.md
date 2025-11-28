# Smart Farming AI System
## Irrigation Model + Plant Health Model + Offline LLM (FLAN-T5 Small)
## Raspberry Pi 5 + EdgeML + Automated MLOps (Nightly Retrain + Rollback)

---

## 1. Overview

This project implements a complete Edge Machine Learning + MLOps workflow for a Smart Farming system that runs fully offline. It includes:

- Irrigation prediction using an SVM classifier
- Plant health classification using an SVM classifier
- Offline LLM advisory generation using google/flan-t5-small
- Real-time inference on Raspberry Pi 5
- Hourly data upload from Raspberry Pi to GitHub
- Nightly automatic retraining via CircleCI
- Automatic rollback if new models perform worse
- Full model versioning and tracking inside GitHub

The system is designed for remote agricultural environments where internet connectivity is limited or unavailable.

---

## 2. Hardware Requirements

- Raspberry Pi 5
- DHT11 or DHT22 temperature & humidity sensor
- ADS1115 or MCP3008 ADC module
- Soil moisture sensor
- LDR (Light Dependent Resistor) + 10kΩ resistor
- Optional RS485-based NPK soil nutrient sensor
- Jumper wires and breadboard

---

## 3. Software Requirements

- Python 3.11 or newer
- scikit-learn
- PyTorch CPU version
- HuggingFace transformers
- gpiozero
- spidev
- adafruit-circuitpython-dht
- GitHub repository with versioning
- CircleCI for automated retraining and rollback

---

## 4. Raspberry Pi Setup

Update system:
```bash
sudo apt update && sudo apt upgrade -y
```
Enable SPI and I2C:
```bash
sudo raspi-config
```
Install OS dependencies:
```bash
sudo apt install -y python3-pip python3-dev python3-full python3-smbus \
libatlas-base-dev libopenjp2-7 libtiff5 python3-libgpiod
````
Install sensor libraries:
```bash
sudo pip3 install --break-system-packages adafruit-circuitpython-dht
sudo pip3 install --break-system-packages gpiozero spidev
````
---

## 5. Python Dependencies

Create a requirements.txt file:

pandas
numpy
scikit-learn
joblib
adafruit-circuitpython-dht
gpiozero
spidev
transformers==4.37.0
safetensors
requests

Install the dependencies:
```bash
sudo pip3 install --break-system-packages -r requirements.txt
```
---

## 6. Install PyTorch CPU
```bash
sudo pip3 install --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
```
Fix NumPy if necessary:
```bash
sudo pip3 install --break-system-packages numpy --upgrade
```
---

## 7. Download Offline LLM Model
```bash
python3 - << 'EOF'
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
AutoTokenizer.from_pretrained("google/flan-t5-small")
EOF
```
The model will be stored in:
```bash
~/.cache/huggingface/
```
---
## 📁 Project Structure
```
Smart-Farming-AI-System/
│
├── 📂 data/
│ ├── 📄 irrigation.csv
│ └── 📄 plant_health_data.csv
│
├── 📂 models/
│ ├── 📂 irrigation/
│ │ ├── 📁 current/
│ │ └── 🗂️ versions/
│ └── 📂 plant_health/
│ ├── 📁 current/
│ └── 🗂️ versions/
│
├── 🧠 src/
│ ├── 🧪 Irrigation_Model.py
│ ├── 🌿 plant_health.py
│ ├── 🚜 agriculture.py
│ ├── 🔌 sensors_ads.py
│ ├── 🧪 npk_sensor.py
│
├── 🍓 raspberry_pi/
│ ├── ⚡ inference_loop.py
│ ├── 📡 upload_data.sh
│ └── 🕒 crontab_setup.txt
│
├── ⚙️ mlops/
│ ├── ⚙️ config.py
│ ├── 🧰 utils.py
│ ├── 📊 metrics.py
│ ├── 🔁 train_irrigation.py
│ ├── 🧬 train_plant_health.py
│ └── ♻️ retrain_all.py
│
├── 🔄 .circleci/
│ └── ⚙️ config.yml
│
└── 📘 README.md
```
---

## 9. Running Real-Time Inference on Raspberry Pi
```bash
python3 raspberry_pi/inference_loop.py
```
This script handles:

- Reading sensor values
- Irrigation prediction
- Plant health prediction
- Generating offline LLM-based advisory using FLAN-T5 Small
- Logging predictions for future retraining

---

## 10. MLOps Pipeline (Nightly Retraining + Rollback)

Nightly Retraining Steps (CircleCI)

- Download the latest data from GitHub
- Retrain the irrigation model
- Retrain the plant health model
- Compare the new accuracy with the previous version
- If accuracy improves → update the current/ model
- If accuracy decreases → rollback to previous version
- Push updated models to GitHub

Versioning Structure:
```
models/irrigation/versions/<timestamp>/
models/plant_health/versions/<timestamp>/
```
Deployed Active Models:
```
models/irrigation/current/
models/plant_health/current/
```
---

## 11. Raspberry Pi Hourly Data Upload

Add cron job:
```
0 * * * * bash /home/pi/Smart-Farming-AI-System/raspberry_pi/upload_data.sh
```
This allows new sensor data to be pushed hourly to GitHub for retraining.

---

## 🔌 Sensor Wiring Table

### 🟦 DHT11 / DHT22 (Temperature & Humidity)
| Pin on Sensor | Connect To | Notes      |
|---------------|------------|------------|
| VCC           | 3.3V       | Power      |
| DATA          | GPIO4      | Signal pin |
| GND           | GND        | Ground     |

---

### 🟫 Soil Moisture Sensor (via MCP3008)
| Soil Sensor Pin | MCP3008 Pin | Raspberry Pi GPIO | Notes          |
|------------------|-------------|--------------------|----------------|
| Analog Out       | CH0         | —                  | Read via ADC   |
| —                | CLK         | GPIO11             | SPI Clock      |
| —                | DOUT        | GPIO9              | MISO           |
| —                | DIN         | GPIO10             | MOSI           |
| —                | CS          | GPIO8              | Chip Select    |

---

### 🟨 LDR (Light Sensor via MCP3008)
| Component | Connect To            | Notes              |
|-----------|------------------------|--------------------|
| LDR       | Voltage Divider Input  | Forms divider      |
| Resistor  | Ground                 | 10kΩ recommended   |
| Output    | MCP3008 CH1            | Analog reading     |


---

## 13. Troubleshooting

PyTorch ImportError:
```bash
sudo pip3 install --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
```
DHT Sensor Failure:
```bash
sudo pip3 install --break-system-packages adafruit-circuitpython-dht
```
NumPy Version Errors:
```bash
sudo pip3 install --break-system-packages numpy --upgrade
```
---

## 14. Future Improvements

- Add MQTT or AWS IoT cloud sync
- Develop live Streamlit dashboard
- Add ESP32 wireless remote sensor nodes
- Add drone-based crop imagery integration
- Add offline TTS for voice-based advisory
