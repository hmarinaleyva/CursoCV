# Compilar y sube un skech para una placa Arduino Uno conectada al puerto /dev/ttyACM1

import os

MainDir = os.path.dirname(os.path.abspath(__file__))
ArduinoSketchDir = os.path.join(MainDir, '.', 'Arduino/ArduinoTest')
os.chdir(ArduinoSketchDir)

try:
    os.system("arduino-cli compile --fqbn arduino:avr:uno")
    os.system("arduino-cli upload -p /dev/ttyACM1 --fqbn arduino:avr:uno")
except:
    os.system("arduino-cli config init --overwrite")
    os.system("arduino-cli core install arduino:avr")
    os.system("sudo chmod a+rw /dev/ttyACM1")
    os.system("arduino-cli compile --fqbn arduino:avr:uno")
    os.system("arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno")