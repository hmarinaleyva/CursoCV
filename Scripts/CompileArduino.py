import os.path

MainDir = os.path.dirname(os.path.abspath(__file__))
ArduinoSketchDir = os.path.join(MainDir, '.', 'Arduino/ArduinoTest')
print(os.getcwd())
os.chdir(MainDir)
print(os.getcwd())
os.chdir(ArduinoSketchDir)
print(os.getcwd())