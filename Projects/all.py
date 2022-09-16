from operator import index
from tkinter import HORIZONTAL
import serial, subprocess

try: #intenta abrir el puerto serie
    InfoBoard = subprocess.getoutput('arduino-cli board list').split()
    PuertoArduino  = InfoBoard[9] #Obtener el puerto de la placa Arduino
    FQBN  = InfoBoard[16] #Obtener el FQBN de la placa Arduino
    ArduinoSerial = serial.Serial(PuertoArduino, 9600, timeout=1) #abrir el puerto serie
except:
    print("No se estableció comunicación serial con una placa Arduino correctamente")
    exit()

ArduinoSerial.write(b'0123456') #enviar una cadena de bytes

from utilities import *
import depthai as dai
import cv2, os, time
import numpy as np

# Cambiar la ruta de ejecución aquí
MainDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(MainDir)

# Ruta del modelo la configuración de la red neuronal entrenada para la deteción de objetos
MODEL_PATH = os.path.join(MainDir, '../Models/MetroModel_YOLOv5s', "Metro_openvino_2021.4_6shave.blob")
CONFIG_PATH = os.path.join(MainDir, '../Models/MetroModel_YOLOv5s', "Metro.json")

# Anhcho y alto de la imagen de entrada a la red neuronal
width, height = 640, 480

# Ruta absoluta del modelo
nnBlobPath = MODEL_PATH

labelMap = [
            "down",
            "emergency",
            "emergency-forward",
            "emergency-right",
            "emergency-left",
            "forward",
            "handicapped",
            "left",
            "line one",
            "line-three",
            "right"
        ]

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
spatialDetectionNetwork = pipeline.create(dai.node.YoloSpatialDetectionNetwork)

# Define sources and outputs for the spatial detection network
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)

nnNetworkOut = pipeline.create(dai.node.XLinkOut)

xoutRgb = pipeline.create(dai.node.XLinkOut)
xoutNN = pipeline.create(dai.node.XLinkOut)
xoutBoundingBoxDepthMapping = pipeline.create(dai.node.XLinkOut)
xoutDepth = pipeline.create(dai.node.XLinkOut)

xoutRgb.setStreamName("rgb")
xoutNN.setStreamName("detections")
xoutBoundingBoxDepthMapping.setStreamName("boundingBoxDepthMapping")
xoutDepth.setStreamName("depth")
nnNetworkOut.setStreamName("nnNetwork")

# Properties
camRgb.setPreviewSize(width, height)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# setting node configs
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)

# Align depth map to the perspective of RGB camera, on which inference is done
stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
stereo.setOutputSize(monoLeft.getResolutionWidth(), monoLeft.getResolutionHeight())

spatialDetectionNetwork.setBlobPath(nnBlobPath)
spatialDetectionNetwork.setConfidenceThreshold(0.5)
spatialDetectionNetwork.input.setBlocking(False)
spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
spatialDetectionNetwork.setDepthLowerThreshold(100)
spatialDetectionNetwork.setDepthUpperThreshold(5000)

# Yolo specific parameters
spatialDetectionNetwork.setNumClasses(11)
spatialDetectionNetwork.setCoordinateSize(4)
spatialDetectionNetwork.setAnchors([10.0,13.0,16.0,30.0,33.0,23.0,30.0,61.0,62.0,45.0,59.0,119.0,116.0,90.0,156.0,198.0,373.0,326.0])
spatialDetectionNetwork.setAnchorMasks({"side80": [0,1,2], "side40": [3,4,5], "side20": [6,7,8]})
spatialDetectionNetwork.setIouThreshold(0.5)
spatialDetectionNetwork.setConfidenceThreshold(0.5)

# Linking
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)

camRgb.preview.link(spatialDetectionNetwork.input)
spatialDetectionNetwork.passthrough.link(xoutRgb.input)

spatialDetectionNetwork.out.link(xoutNN.input)
spatialDetectionNetwork.boundingBoxMapping.link(xoutBoundingBoxDepthMapping.input)

stereo.depth.link(spatialDetectionNetwork.inputDepth)
spatialDetectionNetwork.passthroughDepth.link(xoutDepth.input)
spatialDetectionNetwork.outNetwork.link(nnNetworkOut.input)

# Connect to device and start pipeline
device =dai.Device(pipeline)

# Output queues will be used to get the rgb frames and nn data from the outputs defined above
previewQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
detectionNNQueue = device.getOutputQueue(name="detections", maxSize=4, blocking=False)
xoutBoundingBoxDepthMappingQueue = device.getOutputQueue(name="boundingBoxDepthMapping", maxSize=4, blocking=False)
depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
networkQueue = device.getOutputQueue(name="nnNetwork", maxSize=4, blocking=False)


# Calcular el objeto detectado más cercano al centro de la imagen
def Nearest_Coordinate(OriginPoint, Centroids):
    x0, y0 = OriginPoint
    minDist = min((x-x0)**2 + (y-y0)**2 for x, y in Centroids)
    for index, (x, y) in enumerate(Centroids):
        if (x-x0)**2 + (y-y0)**2 == minDist:
            return x, y, index


def indicate_direction(OriginPoint, EndPoint):
    x0, y0 = OriginPoint
    x, y = EndPoint
    HorizontalDistance = x - x0
    VerticalDistance = y - y0
    if abs(HorizontalDistance) > abs(VerticalDistance):
        if HorizontalDistance > 0:
            return "right"
        else:
            return "left"
    else:
        if VerticalDistance > 0:
            return "down"
        else:
            return "up"

# Coordenadas del centro de la imagen
x0 = width//2
y0 = height//2

# Estilos de dibujo (colores y timpografía)
BoxesColor = (0, 255, 0)
BoxesSize = 2
LineColor = (0, 0, 255)
CircleColor = (255, 0, 0)
TextColor = (0, 255, 255)
FontFace = cv2.FONT_HERSHEY_SIMPLEX # Fuente de texto
FontSize = 0.5 # Tamaño de la fuente

# Depth variables
text = TextHelper()
hostSpatials = HostSpatialsCalc(device)
hostSpatials.setDeltaRoi(15)
ShowDepthFrameColor = False

# Variables de tiempo y frecuancia de actualización de fotogramas 
start_time_up    = 0
start_time_down  = 0
start_time_left  = 0
start_time_right = 0
start_time_frame = 0
start_time_horizontal = 0

fps = 0
frames = 0
while True:

    # Obtener el fotograma de la cámara RGB
    frame = previewQueue.get().getCvFrame()

    # Obtener el fotograma de profundidad    
    depthFrame = depthQueue.get().getFrame()

    # Obtener los datos de la red neuronal
    detections = detectionNNQueue.get().detections

    if len(detections) != 0:

        # Coordenadas del centro de los objetos detectados
        Centroids = []

        for detection in detections:

            detection_label = str(labelMap[detection.label])
            confidence = detection.confidence*100

            # Calcular los vertices de la caja delimitadora
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)
            
            # Calcular el centro de la caja delimitadora y agregarlo a la lista de centroides
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            Centroids.append((x,y))

            # Calcular la distancia a la caja delimitadora
            X = detection.spatialCoordinates.x
            Y = detection.spatialCoordinates.y
            Z = detection.spatialCoordinates.z
            distance = math.sqrt(X**2 + Y**2 + Z**2)/1000

            # Escribir información de la detección en el frame
            cv2.putText(frame, detection_label , (x1, y1), FontFace, FontSize, TextColor, 2)
            cv2.putText(frame, "{:.0f} %".format(confidence), (x2, y), FontFace, FontSize, TextColor, 1)
            cv2.putText(frame, "{:.2f} [m]".format(distance) , (x2, y2), FontFace, FontSize, TextColor)
            cv2.rectangle(frame, (x1, y1), (x2, y2), BoxesColor, BoxesSize)


        # Calcular el objeto detectado más cercano al centro de la imágen
        x, y, index = Nearest_Coordinate((x0,y0), Centroids)

        # Calcular la distancia horizontal y vertical al objeto más cercano
        HorizontalDistance = abs(x - x0)
        VerticalDistance = abs(y - y0)

        # 
        if HorizontalDistance > VerticalDistance:
            fx = ( (x - x0)/(2*width) + 1)**8 -1
            if time.time() - start_time_right > fx :
                if (x - x0) > 0: # El objeto está a la derecha del centro de la imagen
                    ArduinoSerial.write(b'0')
                else: # El objeto está a la izquierda del centro de la imagen
                    ArduinoSerial.write(b'1')
                start_time_horizontal = time.time()


        # Dibujar una flecha que indique el objeto más cercano desde centro de la imágen
        cv2.arrowedLine(frame, (x0, y0), (x, y), LineColor, 2)


        
    if False:
        
        spatials, centroid = hostSpatials.calc_spatials(depthFrame, (x0,y0))
        dist = spatials['z']/1000 if spatials is not None else 0
        cv2.circle(frame, (x0, y0), 5, CircleColor, -1)
        #cv2.putText(frame, "Z: " + ("{:.2f}m".format(dist) ), (x0, y0), FontFace, FontSize, TextColor)

        if ShowDepthFrameColor:
            depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
            depthFrameColor = cv2.equalizeHist(depthFrameColor)
            depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_HOT)
            cv2.imshow("depth", depthFrameColor)

    # Mostar fps en el frame RGB
    cv2.putText(frame, "fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), FontFace, 0.4, TextColor)
    cv2.imshow("rgb", frame)

    # Calcular fps con el tiempo de actualización del fotograma anterior 
    frames += 1
    if (time.time() - start_time_frame) > 1:
        fps = frames / (time.time() - start_time_frame)
        frames = 0
        start_time_frame = time.time()
    
    # Salir del programa si alguna de estas teclas son presionadas {ESC, SPACE, q} 
    if cv2.waitKey(1) in [27, 32, ord('q')]:
        break

device.close()