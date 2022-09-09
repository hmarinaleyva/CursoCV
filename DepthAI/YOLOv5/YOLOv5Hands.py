#!/usr/bin/env python3

import os, subprocess, serial
from re import T
import cv2
import depthai as dai
from util.functions import non_max_suppression
import time
import numpy as np

# Cambiar la ruta de ejecución aquí
MainDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(MainDir)

# Ruta del modelo de la red neuronal entrenada para la deteción de objetos y parámetros de entrada
nn_path = os.path.join(MainDir, './ModelsYOLO', "ModelYOLOv5.blob")
conf_thresh = 0.3   # Establecer el umbral de confianza
iou_thresh = 0.4    # Establecer el umbral de IoU de NMS
nn_shape = 416      # resolución de la imagen de entrada de la red neuronal
labelMap = [        # Establecer el mapa de etiquetas de la red neuronal
    "Persona", "Bicicleta", "Auto", "Moto", "Avión", "Autobús", "Tren",
    "Camión", "Barco", "Semáforo", "Grifo", "Stop", "Parquímetro", "Banco",
    "Pájaro", "Gato", "Perro", "Caballo", "Oveja", "Vaca", "Elefante",
    "Oso", "Cebra", "Jirafa", "Mochila", "Paraguas", "Bolso", "Corbata",
    "Maleta", "Frisbee", "Esquís", "Snowboard", "Pelota", "Cometa", "Bate",
    "Guante", "Monopatín", "Surf", "raqueta de tenis", "Botella", "Copa", "taza",
    "Tenedor", "Cuchillo", "Cuchara", "Cuenco", "Plátano", "Manzana", "Sándwich",
    "Naranja", "Brócoli", "Zanahoria", "Hot-Hog", "Pizza", "Dona", "Pastel",
    "Silla", "Sofá", "Maceta", "Cama", "Comedor", "Baño", "TV",
    "Portátil", "Ratón", "mando", "Teclado", "SmartPhone", "Microondas", "Horno",
    "Tostadora", "Fregadero", "Nevera", "Libro", "Reloj", "Jarrón", "Tijeras",
    "Peluche", "Secador", "Cepillo"
]

def GetBoundingBoxes():    
    in_nn_input = q_nn_input.get()
    in_nn = q_nn.get()
    frame = in_nn_input.getCvFrame()
    output = np.array(in_nn.getLayerFp16("output"))# get the "output" layer
    cols = output.shape[0]//10647# reshape to proper format
    output = np.reshape(output, (10647, cols))
    output = np.expand_dims(output, axis = 0)
    total_classes = cols - 5
    boxes = non_max_suppression(output, conf_thres=conf_thresh, iou_thres=iou_thresh)
    boxes = np.array(boxes[0])
    return [frame, boxes, total_classes]


def Draw_boxes(frame, boxes, total_classes):
    ColorBox = (0, 255, 0)
    if boxes.ndim == 0:
        return frame
    else:

        for i in range(boxes.shape[0]): # Para cada objeto detectado
            x1, y1, x2, y2 = int(boxes[i,0]), int(boxes[i,1]), int(boxes[i,2]), int(boxes[i,3])
            conf, class_index = boxes[i, 4], int(boxes[i, 5])
            label = f"{labelMap[class_index]}: {conf:.2f}"
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), ColorBox, 1)
            # Get the width and height of label for bg square
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.3, 1)

            # Shows the text.
            frame = cv2.rectangle(frame, (x1, y1 - 2*h), (x1 + w, y1), ColorBox, -1)
            frame = cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)
    return frame


# Start defining a pipeline
pipeline = dai.Pipeline()
pipeline.setOpenVINOVersion(version = dai.OpenVINO.VERSION_2021_4)
detection_nn = pipeline.create(dai.node.NeuralNetwork)# Define a neural network that will make predictions based on the source frames
detection_nn.setBlobPath(nn_path)
detection_nn.setNumPoolFrames(4)
detection_nn.input.setBlocking(False)
detection_nn.setNumInferenceThreads(2)


# Definir camara central RGB del sensor OAK-D como fuente de video
cam=None
cam_source = "rgb" 
cam = pipeline.create(dai.node.ColorCamera)
cam.setPreviewSize(nn_shape,nn_shape)
cam.setInterleaved(False)
cam.preview.link(detection_nn.input)
cam.setFps(40) 

# Create outputs
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("nn_input")
xout_rgb.input.setBlocking(False)

detection_nn.passthrough.link(xout_rgb.input)

xout_nn = pipeline.create(dai.node.XLinkOut)
xout_nn.setStreamName("nn")
xout_nn.input.setBlocking(False)

detection_nn.out.link(xout_nn.input)

# Pipeline defined, now the device is assigned and pipeline is started
device = dai.Device(pipeline)

# Output queues will be used to get the rgb frames and nn data from the outputs defined above
q_nn_input = device.getOutputQueue(name="nn_input", maxSize=4, blocking=False)
q_nn = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

start_time = time.time()
counter = 0
fps = 0
while True:
    [frame, boxes, total_classes] = GetBoundingBoxes()

    if boxes is not None:
        frame = Draw_boxes(frame, boxes, total_classes)
    

    
    # Calcular FPS y mostrar en pantalla
    counter += 1
    fps = counter / (time.time() - start_time)
    counter = 0
    start_time = time.time()
    cv2.putText(frame, "FPS: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.75, (255, 255, 255))
    cv2.imshow("YOLOv5Hands", frame)

    # Salir del programa si alguna de estas teclas son presionadas {ESC, q, SPACE} 
    if cv2.waitKey(1) in [27, ord('q'), 32]:
        break
