from depthai_sdk import Previews, FPSHandler
from depthai_sdk.managers import PipelineManager, PreviewManager, BlobManager, NNetManager
import depthai as dai
import cv2, os

# Cambiar la ruta de ejecución aquí
MainDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(MainDir)

# Ruta del modelo la configuración de la red neuronal entrenada para la deteción de objetos
MODEL_PATH = os.path.join(MainDir, '../Models/MetroModel_YOLOv5s', "Metro_openvino_2021.4_6shave.blob")
CONFIG_PATH = os.path.join(MainDir, '../Models/MetroModel_YOLOv5s', "Metro.json")

MODEL_PATH  = os.path.join(MainDir, '../Models/YOLOv5/Small', "yolov5s_openvino_2021.4_6shave.blob")
CONFIG_PATH = os.path.join(MainDir, '../Models/YOLOv5/Small', "yolov5s.json")


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

# initialize pipeline
with dai.Device(pm.pipeline) as device:
    # create outputs
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