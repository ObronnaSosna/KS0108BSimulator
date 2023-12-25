import serial
import time


def arduinoInit(p="/dev/ttyUSB0"):
    global arduino
    arduino = serial.Serial(port=p, baudrate=9600, timeout=0.1)


def sendCommand(cs, data):
    if cs == 0:
        data += 2**11
    if cs == 1:
        data += 2**10
    arduino.write(bytes(str(data), "utf-8"))


def arduinoClose():
    arduino.close()
