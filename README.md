# Smart Farming AI System  
### Irrigation Model + Plant Health Model + Offline LLM (HuggingFace)  
### Raspberry Pi 5 Installation & Usage Guide

---

## 1. Overview

This project integrates:

- Irrigation prediction using a Support Vector Machine (SVM).
- Plant health prediction using a separate SVM model.
- Offline LLM inference using `google/flan-t5-small` on HuggingFace.
- Sensor-based inputs:  
  - Temperature & humidity (DHT11/DHT22)  
  - Soil moisture (MCP3008 ADC)  
  - Light intensity (LDR + resistor)
  - Optional NPK sensor  
- Logging-based operations for AI decision-making.

The entire system works **offline on Raspberry Pi 5**, optimized for low power and no-internet environments suitable for remote farming.

---

## 2. Requirements

### Hardware:
- Raspberry Pi 5  
- DHT11 or DHT22  
- MCP3008 ADC  
- Soil Moisture Sensor  
- LDR + 10kΩ Resistor  
- Optional NPK Sensor  
- Jumper wires, breadboard

### Software:
- Python 3.11 or 3.13  
- HuggingFace Transformers  
- PyTorch CPU  
- scikit-learn  
- gpiozero, spidev, Adafruit DHT library

---

## 3. Raspberry Pi Setup

Update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

Enable SPI:

```bash
sudo raspi-config
# Interface Options → SPI → Enable
```

Reboot:

```bash
sudo reboot
```

---

## 4. Install OS-Level Dependencies

```bash
sudo apt install -y python3-pip python3-dev python3-full python3-smbus \
                    libatlas-base-dev libopenjp2-7 libtiff5
```

Install GPIO sensor support:

```bash
sudo apt install -y python3-libgpiod
sudo pip3 install --break-system-packages adafruit-circuitpython-dht
sudo pip3 install --break-system-packages gpiozero spidev
```

---

## 5. Python Requirements

Create **requirements.txt**:

```
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
```

Install:

```bash
sudo pip3 install --break-system-packages -r requirements.txt
```

---

## 6. Install PyTorch (CPU)

```bash
sudo pip3 install --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
```

If numpy breaks:

```bash
sudo pip3 install --break-system-packages numpy --upgrade
```

---

## 7. Download Offline HuggingFace LLM

```bash
python3 - << 'EOF'
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
AutoTokenizer.from_pretrained("google/flan-t5-small")
EOF
```

Model downloads to:

```
~/.cache/huggingface/
```

---

## 8. Project Structure

```
smart_farming_ai/
│
├── irrigation_data.csv
├── plant_health_data.csv
│
├── Irrigation_Model.py
├── plant_health.py
├── agriculture.py
│
├── requirements.txt
└── README.md
```

---

## 9. Running the AI System

Run:

```bash
python3 agriculture.py
```

Process executed:

1. Loads irrigation model.  
2. Loads plant health model.  
3. Reads real-time sensor values.  
4. Predicts irrigation need.  
5. Predicts plant health.  
6. Generates AI advisory using offline LLM.  
7. Logs everything.

Example logs:

```
2025-01-10 03:12:44,553 - INFO - IrrigationModel initialized.
2025-01-10 03:12:49,101 - INFO - Plant Health Prediction: Moderate Stress
2025-01-10 03:12:52,033 - INFO - LLM Response Generated Successfully.
```

---

## 10. Sensor Wiring Guide

### DHT11 / DHT22

```
VCC  → 3.3V  
DATA → GPIO4  
GND  → GND  
```

### Soil Moisture Sensor → MCP3008 CH0

```
Soil Sensor → CH0
CLK → GPIO11
DOUT → GPIO9
DIN → GPIO10
CS → GPIO8
VDD → 3.3V
GND → GND
```

### LDR Light Sensor (Voltage Divider)

```
LDR — Resistor — MCP3008 CH1
```

---

## 11. Troubleshooting

### Issue: Model Out-of-Memory / crash (`Killed` or exit -9)

Use only:

```
google/flan-t5-small
```

Avoid larger models.

### Issue: typing_extensions uninstall conflict

Fix:

```bash
sudo pip3 install --break-system-packages --ignore-installed package_name
```

### Issue: PyTorch fails to import

Reinstall CPU wheel:

```bash
sudo pip3 install --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
```

---

## 12. Future Enhancements

- Add cloud sync (MQTT or Firebase).
- Live dashboard using Flask.
- ESP32 sensor expansion.
- Mobile app integration.
- Voice-based local assistant (offline TTS).

---

## 13. License

Open-source for research and educational purposes.

