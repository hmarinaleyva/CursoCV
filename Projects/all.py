import serial, subprocess

try: #intenta abrir el puerto serie
    InfoBoard = subprocess.getoutput('arduino-cli board list').split("\n")[1].split() 
    PuertoArduino  = InfoBoard[0] #Obtener el puerto de la placa Arduino
    FQBN  = InfoBoard[-2] #Obtener el FQBN de la placa Arduino
    ArduinoSerial = serial.Serial(PuertoArduino, 9600, timeout=1) #abrir el puerto serie
except:
    print("No se estableció comunicación serial con una placa Arduino correctamente")
    exit()

ArduinoSerial.write(b'0123456') #enviar una cadena de bytes

from utilities import *
import depthai as dai
import cv2, os, time


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
            "right",
            "line one",
            "line-three",
            "left"
        ]

spanishLabelMap = [
            "abajo",
            "emergencia",
            "emergencia adelante",
            "emergencia derecha",
            "emergencia izquierda",
            "adelante",
            "minusválido",
            "derecha",
            "línea uno",
            "línea tres",
            "izquierda"
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
spatialDetectionNetwork.setConfidenceThreshold(0.6)

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

# Calcular coordenadas de los vertices un bounding box 
def Vertices(detection):        
    x1 = int(detection.xmin * width)
    x2 = int(detection.xmax * width)
    y1 = int(detection.ymin * height)
    y2 = int(detection.ymax * height)
    return x1, x2, y1, y2

# Calcular la coordenada del centro de un bounding box
def Center(x1, x2, y1, y2):
    x = int((x1 + x2) / 2)
    y = int((y1 + y2) / 2)
    return x, y

# Calcular la distancia de un objeto a la camara
def distance_to_camera(detection):
    X = detection.spatialCoordinates.x
    Y = detection.spatialCoordinates.y
    Z = detection.spatialCoordinates.z
    return math.sqrt(X**2 + Y**2 + Z**2)

# Determina las coordenasdas del centro del bounding box más cercano y el índice correspondiente
def Nearest_Coordinate(OriginPoint, Centroids):
    x0, y0 = OriginPoint
    minDist = min((x-x0)**2 + (y-y0)**2 for x, y in Centroids)
    for index, (x, y) in enumerate(Centroids):
        if (x-x0)**2 + (y-y0)**2 == minDist:
            return x, y, index

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

# Variables de tiempo
frame_time = 0
move_time = 0

mentioned_object = False # Variable para evitar que se repita el nombre del objeto detectado

# anonimus functions
f1 = lambda x: math.sqrt(1 + x) - 1
f2 = lambda x: (x + 1)**2 - 1

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
            x1, x2, y1, y2 = Vertices(detection)
            
            # Calcular el centro de la caja delimitadora y agregarlo a la lista de centroides
            x, y = Center(x1, x2, y1, y2)
            Centroids.append((x, y))

            # Calcular la distancia a la caja delimitadora
            distance = distance_to_camera(detection)

            # Escribir información de la detección en el frame
            cv2.putText(frame, detection_label , (x1, y1), FontFace, FontSize, TextColor, 2)
            cv2.putText(frame, "{:.0f} %".format(confidence), (x2, y), FontFace, FontSize, TextColor, 1)
            cv2.putText(frame, "{:.2f} [m]".format(distance) , (x2, y2), FontFace, FontSize, TextColor)
            cv2.rectangle(frame, (x1, y1), (x2, y2), BoxesColor, BoxesSize)

        # Determina las coordenasdas del centro del bounding box más cercano y el índice correspondiente
        x, y, i = Nearest_Coordinate((x0,y0), Centroids)

        # Reasignar coordenadas (x1, x2, y1, y2) a los vértices del bounding box más cercano
        x1, x2, y1, y2 = Vertices(detections[i])

        # Traducir la etiqueta del objeto detectado y reasingarla a la variable "detection_label"
        detection_label = str(spanishLabelMap[detections[i].label])


        # Si el centro de la imágen está dentro de la caja delimitadora del objeto más cercano
        if x1 < x0 < x2 and y1 < y0 < y2:

            if not mentioned_object:
                os.system('spd-say "' + detection_label + '"')
                ArduinoSerial.write(b'DLRU')
                mentioned_object = True

        else: 
            # Calcular la distancia horizontal y vertical al objeto más cercano
            HorizontalDistance = abs(x - x0)
            VerticalDistance = abs(y - y0)

            if HorizontalDistance > VerticalDistance:

                if f1(time.time() - move_time) > f2(HorizontalDistance/(2*width)):
                    if (x - x0) > 0: # El objeto está a la derecha del centro de la imagen
                        ArduinoSerial.write(b'R') # 68 ASCII
                    else: # El objeto está a la izquierda del centro de la imagen
                        ArduinoSerial.write(b'L') # 76 ASCII
                    move_time = time.time()
            else:

                if f1(time.time() - move_time) > f2(VerticalDistance/(2*height)):
                    if (y - y0) > 0: # El objeto está abajo del centro de la imagen
                        ArduinoSerial.write(b'D') # 82 ASCII
                    else: # El objeto está arriba del centro de la imagen
                        ArduinoSerial.write(b'U') # 85 ASCII
                    move_time = time.time()

            mentioned_object = False

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
    if (time.time() - frame_time) > 1:
        fps = frames / (time.time() - frame_time)
        frames = 0
        frame_time = time.time()
    
    # Salir del programa si alguna de estas teclas son presionadas {ESC, SPACE, q} 
    if cv2.waitKey(1) in [27, 32, ord('q')]:
        break

device.close()