from depthai_sdk import Previews, FPSHandler
from depthai_sdk.managers import PipelineManager, PreviewManager, BlobManager, NNetManager
import depthai as dai

import cv2, os, time

# Cambiar la ruta de ejecución aquí
MainDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(MainDir)

# Ruta del modelo la configuración de la red neuronal entrenada para la deteción de objetos
MODEL_PATH = os.path.join(MainDir, '../Models/MetroModel_YOLOv5s', "Metro_openvino_2021.4_6shave.blob")
CONFIG_PATH = os.path.join(MainDir, '../Models/MetroModel_YOLOv5s', "Metro.json")

# inicializar el BlobManager con la ruta al archivo .blob
bm = BlobManager(blobPath=MODEL_PATH)
nm = NNetManager(nnFamily="YOLO", inputSize=4)
nm.readConfig(CONFIG_PATH)  # this will also parse the correct input size
# initialize blob manager with path to the blob
bm = BlobManager(blobPath=MODEL_PATH)
nm = NNetManager(nnFamily="YOLO", inputSize=4)
nm.readConfig(CONFIG_PATH)  # this will also parse the correct input size
pm = PipelineManager()
pm.createColorCam(previewSize=nm.inputSize, xout=True)
# create preview manager
fpsHandler = FPSHandler()
pv = PreviewManager(display=[Previews.color.name], fpsHandler=fpsHandler)
# create NN with managers
nn = nm.createNN(pipeline=pm.pipeline, nodes=pm.nodes, source=Previews.color.name,
                 blobPath=bm.getBlob(shaves=6, openvinoVersion=pm.pipeline.getOpenVINOVersion(), zooType="depthai"))
pm.addNn(nn)



###############################################################################


# Anhcho y alto de la imagen de entrada a la red neuronal
width, height = 640, 480

# Ruta absoluta del modelo
nnBlobPath = MODEL_PATH

# Tiny yolo v3/4 label texts
labelMap = [
    "person",         "bicycle",    "car",           "motorbike",     "aeroplane",   "bus",           "train",
    "truck",          "boat",       "traffic light", "fire hydrant",  "stop sign",   "parking meter", "bench",
    "bird",           "cat",        "dog",           "horse",         "sheep",       "cow",           "elephant",
    "bear",           "zebra",      "giraffe",       "backpack",      "umbrella",    "handbag",       "tie",
    "suitcase",       "frisbee",    "skis",          "snowboard",     "sports ball", "kite",          "baseball bat",
    "baseball glove", "skateboard", "surfboard",     "tennis racket", "bottle",      "wine glass",    "cup",
    "fork",           "knife",      "spoon",         "bowl",          "banana",      "apple",         "sandwich",
    "orange",         "broccoli",   "carrot",        "hot dog",       "pizza",       "donut",         "cake",
    "chair",          "sofa",       "pottedplant",   "bed",           "diningtable", "toilet",        "tvmonitor",
    "laptop",         "mouse",      "remote",        "keyboard",      "cell phone",  "microwave",     "oven",
    "toaster",        "sink",       "refrigerator",  "book",          "clock",       "vase",          "scissors",
    "teddy bear",     "hair drier", "toothbrush"
]

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
spatialDetectionNetwork = pipeline.create(dai.node.YoloSpatialDetectionNetwork)
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
#spatialDetectionNetwork.setAnchors([10,14, 23,27, 37,58, 81,82, 135,169, 344,319])
#spatialDetectionNetwork.setAnchorMasks({ "side26": [1,2,3], "side13": [3,4,5] })
spatialDetectionNetwork.setAnchors([10,13,16,30,33,23,30,61,62,45,59,119,116,90,156,198,373,326])
spatialDetectionNetwork.setAnchorMasks({ "side80": [1,2,3], "side40": [3,4,5], "side20": [6,7,8] })
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

################################################

# Output queues will be used to get the rgb frames and nn data from the outputs defined above
previewQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
detectionNNQueue = device.getOutputQueue(name="detections", maxSize=4, blocking=False)
xoutBoundingBoxDepthMappingQueue = device.getOutputQueue(name="boundingBoxDepthMapping", maxSize=4, blocking=False)
depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
networkQueue = device.getOutputQueue(name="nnNetwork", maxSize=4, blocking=False);

# Coordenadas del centro de la imagen
x0 = width//2
y0 = height//2

# Estilos de dibujo
BoxesColor = (0, 255, 0)
LineColor = (0, 0, 255)
CircleColor = (255, 0, 0)
TextColor = (255,255,255)
FontFace = cv2.FONT_HERSHEY_SIMPLEX#cv2.FONT_HERSHEY_TRIPLEX # Fuente de texto

# Variables de tiempo y velocidad 
fps = 0
start_frame_time = 0

startTime = time.monotonic()
counter = 0
fps = 0
printOutputLayersOnce = True

while True:
    inPreview = previewQueue.get()
    inDet = detectionNNQueue.get()
    depth = depthQueue.get()
    inNN = networkQueue.get()

    if printOutputLayersOnce:
        toPrint = 'Output layer names:'
        for ten in inNN.getAllLayerNames():
            toPrint = f'{toPrint} {ten},'
        print(toPrint)
        printOutputLayersOnce = False;

    frame = inPreview.getCvFrame()
    depthFrame = depth.getFrame() # depthFrame values are in millimeters

    depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
    depthFrameColor = cv2.equalizeHist(depthFrameColor)
    depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_HOT)

    counter+=1
    current_time = time.monotonic()
    if (current_time - startTime) > 0.01 : # every 10 ms
        fps = counter / (current_time - startTime)
        counter = 0
        startTime = current_time

    detections = inDet.detections
    if len(detections) != 0:
        boundingBoxMapping = xoutBoundingBoxDepthMappingQueue.get()
        roiDatas = boundingBoxMapping.getConfigData()

        for roiData in roiDatas:
            roi = roiData.roi
            roi = roi.denormalize(depthFrameColor.shape[1], depthFrameColor.shape[0])
            topLeft = roi.topLeft()
            bottomRight = roi.bottomRight()
            xmin = int(topLeft.x)
            ymin = int(topLeft.y)
            xmax = int(bottomRight.x)
            ymax = int(bottomRight.y)

            cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), TextColor, FontFace)


    # If the frame is available, draw bounding boxes on it and show the frame
    height = frame.shape[0]
    width  = frame.shape[1]
    for detection in detections:
        # Denormalize bounding box
        x1 = int(detection.xmin * width)
        x2 = int(detection.xmax * width)
        y1 = int(detection.ymin * height)
        y2 = int(detection.ymax * height)
        try:
            label = labelMap[detection.label]
        except:
            label = detection.label
        cv2.putText(frame, str(label), (x1 + 10, y1 + 20), FontFace, 0.5, 255)
        cv2.putText(frame, "{:.2f}".format(detection.confidence*100), (x1 + 10, y1 + 35), FontFace, 0.5, 255)
        cv2.putText(frame, f"X: {int(detection.spatialCoordinates.x)} mm", (x1 + 10, y1 + 50), FontFace, 0.5, 255)
        cv2.putText(frame, f"Y: {int(detection.spatialCoordinates.y)} mm", (x1 + 10, y1 + 65), FontFace, 0.5, 255)
        cv2.putText(frame, f"Z: {int(detection.spatialCoordinates.z)} mm", (x1 + 10, y1 + 80), FontFace, 0.5, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), BoxesColor, FontFace)

    cv2.putText(frame, "NN fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), FontFace, 0.4, TextColor)
    cv2.imshow("depth", depthFrameColor)
    cv2.imshow("rgb", frame)

    # Salir del programa si alguna de estas teclas son presionadas {ESC, SPACE, q} 
    if cv2.waitKey(1) in [27, 32, ord('q')]:
        break

################################################
device = dai.Device(pm.pipeline)
pv.createQueues(device)
nm.createQueues(device)
nnData = []

while True:

    # parse outputs
    pv.prepareFrames()
    inNn = nm.outputQueue.tryGet()

    if inNn is not None:
        nnData = nm.decode(inNn)
        # count FPS
        fpsHandler.tick("color")

    nm.draw(pv, nnData)
    pv.showFrames()

    # Salir del programa si alguna de estas teclas son presionadas {ESC, SPACE, q} 
    if cv2.waitKey(1) in [27, 32, ord('q')]:
        break