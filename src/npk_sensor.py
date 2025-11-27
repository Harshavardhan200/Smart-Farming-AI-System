from pymodbus.client import ModbusSerialClient
import logging

logging.basicConfig(level=logging.INFO)

class NPKSensor:
    def __init__(self, port="/dev/ttyS0", slave_id=1):
        self.client = ModbusSerialClient(
            method="rtu",
            port=port,
            baudrate=9600,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )
        self.slave_id = slave_id

    def read_npk(self):
        if not self.client.connect():
            logging.error("Failed to connect to RS485 Modbus.")
            return None, None, None

        # NPK sensor register map:
        # Nitrogen:   0x0001
        # Phosphorus: 0x0002
        # Potassium:  0x0003

        rr = self.client.read_input_registers(0x0001, 3, slave=self.slave_id)

        if not rr.isError():
            nitrogen = rr.registers[0]
            phosphorus = rr.registers[1]
            potassium = rr.registers[2]
            return nitrogen, phosphorus, potassium
        else:
            logging.error("Modbus read error.")
            return None, None, None
