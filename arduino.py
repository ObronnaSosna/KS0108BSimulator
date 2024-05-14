import serial
from serial.tools import list_ports
import time


def arduinoInit(p="/dev/ttyUSB0"):
    global arduino
    try:
        arduino = serial.Serial(port=p, baudrate=115200, timeout=0, writeTimeout=0)
    except:
        pass


def sendCommand(cs, data):
    if cs == 0:
        data += 2**11
    if cs == 1:
        data += 2**10
    try:
        arduino.write(bytes(str(data), "utf-8"))
        # arduino.write(str(data).encode())
    except:
        pass


def arduinoClose():
    try:
        arduino.close()
    except:
        pass


def getPorts():
    return sorted([x for x, y, z in list_ports.comports() if "USB" in x])
