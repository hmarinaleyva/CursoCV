import serial, subprocess

try: # try to open the serial port
    InfoBoard = subprocess.getoutput('arduino-cli board list').split()
    PuertoArduino  = InfoBoard[9] # Obtener el puerto de la placa Arduino
    FQBN  = InfoBoard[16] # Obtener el FQBN de la placa Arduino
    ArduinoSerial = serial.Serial(PuertoArduino, 9600, timeout=1) # open the serial port
except:
    print("No se estableció comunicación serial con una placa Arduino correctamente")
    exit()

ArduinoSerial.write(b'0123456') # send a byte string

from utilities import *
from depthai_sdk import Previews, FPSHandler
from depthai_sdk.managers import PipelineManager, PreviewManager, BlobManager, NNetManager
import depthai as dai
import cv2, os

# Cambiar la ruta de ejecución aquí
MainDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(MainDir)

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)

# Properties
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

stereo.initialConfig.setConfidenceThreshold(255)
stereo.setLeftRightCheck(True)
stereo.setSubpixel(False)

# Linking
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)

xoutDepth = pipeline.create(dai.node.XLinkOut)
xoutDepth.setStreamName("depth")
stereo.depth.link(xoutDepth.input)

xoutDepth = pipeline.create(dai.node.XLinkOut)
xoutDepth.setStreamName("disp")
stereo.disparity.link(xoutDepth.input)

# Connect to device and start pipeline
device = dai.Device(pipeline)

# Output queue will be used to get the depth frames from the outputs defined above
depthQueue = device.getOutputQueue(name="depth")
dispQ = device.getOutputQueue(name="disp")

text = TextHelper()
hostSpatials = HostSpatialsCalc(device)
y = 200
x = 300
step = 3
delta = 5
hostSpatials.setDeltaRoi(delta)

time_start = time.time()
while True:
    depthFrame = depthQueue.get().getFrame()
    # Calculate spatial coordiantes from depth frame
    spatials, centroid = hostSpatials.calc_spatials(depthFrame, (x,y)) # centroid == x/y in our case

    # Get disparity frame for nicer depth visualization
    disp = dispQ.get().getFrame()
    disp = cv2.applyColorMap(disp, cv2.COLORMAP_JET)

    text.rectangle(disp, (x-delta, y-delta), (x+delta, y+delta))
    text.putText(disp, "X: " + ("{:.2f}m".format(spatials['x']/1000) if not math.isnan(spatials['x']) else "--"), (x + 10, y + 20))
    text.putText(disp, "Y: " + ("{:.2f}m".format(spatials['y']/1000) if not math.isnan(spatials['y']) else "--"), (x + 10, y + 35))
    text.putText(disp, "Z: " + ("{:.2f}m".format(spatials['z']/1000) if not math.isnan(spatials['z']) else "--"), (x + 10, y + 50))

    z = spatials['z']/1000

    print(z)

    if time.time() - time_start >= z/4 and z>0 and z<1:
        ArduinoSerial.write(b'3')
        time_start = time.time()

    if time.time() - time_start >= z/8 and z>1 and z<2:
        ArduinoSerial.write(b'2')
        time_start = time.time()

    if time.time() - time_start >= z/16 and z>2 and z<3:
        ArduinoSerial.write(b'1')
        time_start = time.time()

    if time.time() - time_start >= z/32 and z>3 and z<4:
        ArduinoSerial.write(b'0')
        time_start = time.time()

    # Show the frame
    cv2.imshow("depth", disp)

    key = cv2.waitKey(1)
    if key in [27, 32, ord('q')]: # Salir del programa si alguna de estas teclas son presionadas {ESC, SPACE, q}
        break
    elif key == ord('w'):
        y -= step
    elif key == ord('a'):
        x -= step
    elif key == ord('s'):
        y += step
    elif key == ord('d'):
        x += step
    elif key == ord('r'): # Increase Delta
        if delta < 50:
            delta += 1
            hostSpatials.setDeltaRoi(delta)
    elif key == ord('f'): # Decrease Delta
        if 3 < delta:
            delta -= 1
            hostSpatials.setDeltaRoi(delta)
