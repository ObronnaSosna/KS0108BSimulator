import serial
from serial.tools import list_ports
from time import sleep


def arduinoInit(p="/dev/ttyUSB0"):
    global arduino
    global enabled
    try:
        arduino = serial.Serial(port=p, baudrate=115200, timeout=None, writeTimeout=0)
        enabled = True
    except:
        enabled = False


def sendCommand(cs, data):
    if cs == 0:
        data += 2**11
    if cs == 1:
        data += 2**10
    try:
        arduino.write(bytes(str(data) + "a", "utf-8"))
        sleep(0.00003)
    except:
        pass


def arduinoClose():
    try:
        arduino.close()
        enabled = False
    except:
        pass


def getPorts():
    return sorted([x for x, y, z in list_ports.comports()])


enabled = False
