import os, serial, subprocess

MainDir = os.path.dirname(os.path.abspath(__file__))
ArduinoSketchDir = os.path.join(MainDir, '.', 'Arduino/ArduinoTest')
os.chdir(ArduinoSketchDir)

try:
    InfoBoard = subprocess.getoutput('arduino-cli board list').split()
    PuertoArduino  = InfoBoard[9] # Obtener el puerto de la placa Arduino
    FQBN  = InfoBoard[16] # Obtener el FQBN de la placa Arduino
    os.system("arduino-cli compile --fqbn " + FQBN)
    os.system("arduino-cli upload -p " + PuertoArduino +  " --fqbn " + FQBN)
except:
    os.system("arduino-cli config init --overwrite")
    os.system("arduino-cli core install arduino:avr")
    os.system("sudo chmod a+rw /dev/ttyACM0")
    os.system("arduino-cli compile --fqbn " + FQBN)
    os.system("arduino-cli upload -p " + PuertoArduino +  " --fqbn " + FQBN)