import os, subprocess, serial

SketchPath = 'Arduino/ArduinoTest'
MainDir = os.path.dirname(os.path.abspath(__file__))
ArduinoSketchDir = os.path.join(MainDir, '.', SketchPath)
os.chdir(ArduinoSketchDir)

try:
    InfoBoard = subprocess.getoutput('arduino-cli board list').split()
    print(InfoBoard)
    PuertoArduino  = InfoBoard[9] # Obtener el puerto de la placa Arduino
    FQBN  = InfoBoard[16] # Obtener el FQBN de la placa Arduino
    os.system("arduino-cli compile --fqbn " + FQBN)
    os.system("arduino-cli upload -p " + PuertoArduino +  " --fqbn " + FQBN)
except Exception as e:
    print("No se estableció comunicación serial con una placa Arduino correctamente")
    os.system("arduino-cli config init --overwrite")
    os.system("arduino-cli core install arduino:avr")
    os.system("sudo chmod a+rw " + PuertoArduino)
    os.system("arduino-cli compile --fqbn " + FQBN)
    os.system("arduino-cli upload -p " + PuertoArduino +  " --fqbn " + FQBN)

ArduinoSerial = serial.Serial(PuertoArduino, 9600, timeout=1)