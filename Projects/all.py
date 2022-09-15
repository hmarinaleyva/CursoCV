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

from depthai_sdk import Previews, FPSHandler
from depthai_sdk.managers import PipelineManager, PreviewManager, BlobManager, NNetManager
import depthai as dai
import cv2, os, time
from scipy import spatial

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
            "emergency-left",
            "emergency-right",
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
def Nearest_Coordinate(Point, Centroids):
    x0, y0 = Point
    minDist = min((x-x0)**2 + (y-y0)**2 for x, y in Centroids)
    for x, y in Centroids:
        if (x-x0)**2 + (y-y0)**2 == minDist:
            return x, y

# Coordenadas del centro de la imagen
x0 = width//2
y0 = height//2

# Estilos de dibujo (colores y timpografía)
BoxesColor = (0, 255, 0)
BoxesSize = 1
LineColor = (0, 0, 255)
CircleColor = (255, 0, 0)
TextColor = (0, 255, 255)
FontFace = cv2.FONT_HERSHEY_SIMPLEX # Fuente de texto
FontSize = 0.5 # Tamaño de la fuente

# Variables de tiempo y velocidad 
fps = 0
time = 0

while True:


    frame = previewQueue.get().getCvFrame()
    detections = detectionNNQueue.get().detections

    depthFrame = depthQueue.get().getFrame()
    depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
    depthFrameColor = cv2.equalizeHist(depthFrameColor)
    depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_HOT)


    if len(detections) != 0:

        # Coordenadas del centro de los objetos detectados
        Centroids = []

        for detection in detections:

            detection_label = str(labelMap[detection.label])

            # Calcular los vertices de la caja delimitadora
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)
            
            # Calcular el centro de la caja delimitadora y agregarlo a la lista de centroides
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            Centroids.append((x,y))

            # Calcular el ancho y alto de la caja delimitadora
            w = x2 - x1
            h = y2 - y1

            # Calcular la distancia a la caja delimitadora
            z = detection.spatialCoordinates.z/1000
            confidence = detection.confidence*100            

            # Escribir información de la detección en el frame
            cv2.putText(frame, detection_label , (x1, y1), FontFace, FontSize, TextColor, 2)
            cv2.putText(frame, "{:.2f} %".format(confidence), (x2, y), FontFace, FontSize, TextColor, 1)
            cv2.putText(frame, "Z: {:.3f} mm".format(z) , (x1, y+h), FontFace, FontSize, TextColor)
            cv2.rectangle(frame, (x1, y1), (x2, y2), BoxesColor, BoxesSize)


        # Calcular el objeto detectado más cercano al centro de la imágen
        x, y = Nearest_Coordinate((x0,y0), Centroids)

        # Dibujar una checha que indique el objeto más cercano desde centro de la imágen
        cv2.arrowedLine(frame, (x0, y0), (x, y), LineColor, 2)
        

    cv2.putText(frame, "NN fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), FontFace, 0.4, TextColor)
    cv2.imshow("depth", depthFrameColor)
    cv2.imshow("rgb", frame)

    # Salir del programa si alguna de estas teclas son presionadas {ESC, SPACE, q} 
    if cv2.waitKey(1) in [27, 32, ord('q')]:
        break
