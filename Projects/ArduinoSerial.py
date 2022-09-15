import re
import serial, subprocess

try: # try to open the serial port
    InfoBoard = subprocess.getoutput('arduino-cli board list').split()
    PuertoArduino  = InfoBoard[9] # Obtener el puerto de la placa Arduino
    FQBN  = InfoBoard[16] # Obtener el FQBN de la placa Arduino
    ArduinoSerial = serial.Serial(PuertoArduino, 9600, timeout=1) # open the serial port
    ArduinoSerial.write(b'0123456') # send a byte string
except:
    print("No se estableció comunicación serial con una placa Arduino correctamente")
    exit()