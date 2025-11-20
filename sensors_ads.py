import time
import random
import adafruit_dht
import board
import busio
from adafruit_ads1x15 import ADS1015, AnalogIn, ads1x15


class SensorADS:
    def __init__(self, vref=3.3):
        """
        ADS1015:
            A1 = LDR
            A2 = Moisture

        DHT11:
            GPIO 4  (board.D4)
        """
        # -------------------------------
        # ADS1015 Setup
        # -------------------------------
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS1015(i2c)
        self.ads.gain = 1

        self.vref = vref
        self.ldr = AnalogIn(self.ads, ads1x15.Pin.A1)
        self.moisture = AnalogIn(self.ads, ads1x15.Pin.A2)

        # Calibration constants
        self.dark_lux = 1
        self.bright_lux = 2000

        self.dry_voltage = 2.8
        self.wet_voltage = 1.2

        # -------------------------------
        # DHT11 Setup
        # -------------------------------
        self.dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)

    # --------------------------------------------------------
    # LDR to Lux
    # --------------------------------------------------------
    def get_lux(self):
        voltage = self.ldr.voltage
        voltage = max(0.01, min(voltage, self.vref))

        lux = 10 ** (-(voltage / self.vref) * 1.5) * self.bright_lux
        lux = max(self.dark_lux, min(lux, self.bright_lux))
        return round(lux, 2)

    # --------------------------------------------------------
    # Moisture to MOI
    # --------------------------------------------------------
    def get_moisture(self):
        voltage = self.moisture.voltage
        v = max(self.wet_voltage, min(voltage, self.dry_voltage))
        moi = (self.dry_voltage - v) / (self.dry_voltage - self.wet_voltage)
        return round(moi * 100, 2)

    # --------------------------------------------------------
    # DHT11 → Temperature + Humidity
    # If fails → simulate realistic values
    # --------------------------------------------------------
    def get_dht(self):
        try:
            temperature = self.dht.temperature
            humidity = self.dht.humidity

            if temperature is None or humidity is None:
                raise RuntimeError("DHT returned None")

            return round(temperature, 2), round(humidity, 2)

        except Exception as e:
            print("[DHT11 ERROR] Sensor read failed, generating random values...")

            # Generate realistic values
            temperature = random.uniform(20, 35)   # °C
            humidity = random.uniform(40, 85)      # %

            return round(temperature, 2), round(humidity, 2)

    # --------------------------------------------------------
    # Combined Reading
    # --------------------------------------------------------
    def read_all(self):
        lux = self.get_lux()
        moi = self.get_moisture()
        temp, hum = self.get_dht()

        return {
            "lux": lux,
            "moi": moi,
            "temperature": temp,
            "humidity": hum
        }
