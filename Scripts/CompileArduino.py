import os

MainDir = os.path.dirname(os.path.abspath(__file__))
ArduinoSketchDir = os.path.join(MainDir, '.', 'Arduino/ArduinoTest')
print(os.getcwd())
os.chdir(MainDir)
print(os.getcwd())
os.chdir(ArduinoSketchDir)
print(os.getcwd())

os.system("curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh")
os.system("arduino-cli compile --fqbn arduino:avr:mega")