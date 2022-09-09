#!/usr/bin/env python3

import os, time
import cv2
import depthai as dai
import numpy as np
from util.functions import non_max_suppression
from re import T


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
device = dai.Device(pipeline)# Pipeline defined, now the device is assigned and pipeline is started
# Output queues will be used to get the rgb frames and nn data from the outputs defined above
q_nn_input = device.getOutputQueue(name="nn_input", maxSize=4, blocking=False)
q_nn = device.getOutputQueue(name="nn", maxSize=4, blocking=False)



def GetBoundingBoxes(q_nn_input, q_nn):    
    in_nn_input = q_nn_input.get()
    in_nn = q_nn.get()
    frame = in_nn_input.getCvFrame()
    output = np.array(in_nn.getLayerFp16("output"))# get the "output" layer
    cols = output.shape[0]//10647# reshape to proper format
    output = np.reshape(output, (10647, cols))
    output = np.expand_dims(output, axis = 0)
    boxes = non_max_suppression(output, conf_thres=conf_thresh, iou_thres=iou_thresh)
    boxes = np.array(boxes[0])
    return [frame, boxes]


# Calcular FPS y mostrar en pantalla
def Show_FPS(frame_count, start_time):
    global fps
    frame_count += 1
    fps = frame_count / (time.time() - start_time)
    start_time = time.time()
    cv2.putText(frame, "FPS: {:.2f}".format(fps), (2, frame.shape[0] - 4), FontFace, 0.75, TextColor)

fps = 0
start_frame_time = 0
BoxesColor = (0, 255, 0)
TextColor = (255,255,255)
FontFace = cv2.FONT_HERSHEY_TRIPLEX # Fuente de texto 
while True:
    frame, boxes = GetBoundingBoxes(q_nn_input, q_nn) # Obtener fotograma de la cámara y las cajas de detección
    if boxes is not None and boxes.ndim != 0: # Si hay objetos detectados

        for i in range(boxes.shape[0]): # Para cada objeto detectado
            x1, y1, x2, y2 = int(boxes[i,0]), int(boxes[i,1]), int(boxes[i,2]), int(boxes[i,3])
            conf, class_index = boxes[i, 4], int(boxes[i, 5]) # Extraer la confianza y el índice de la clase de la predicción
            label = f"{labelMap[class_index]}: {conf:.2f}" # Crear etiqueta de la clase predicha
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), BoxesColor, 1) # Dibujar caja de detección
            (w, h), _ = cv2.getTextSize(label, FontFace, 0.3, 1) # Obtener el ancho y alto de la etiqueta
            frame = cv2.rectangle(frame, (x1, y1 - 2*h), (x1 + w, y1), BoxesColor, -1) # Dibuja el recuadro de la etiqueta
            frame = cv2.putText(frame, label, (x1, y1 - 5), FontFace, 0.3, TextColor, 1) # Dibuja el texto de la etiqueta

    cv2.putText(frame, "FPS: {:.2f}".format(fps), (2, frame.shape[0] - 4), FontFace, 0.75, TextColor) # Mostrar FPS
    cv2.imshow("YOLOv5Hands", frame)  # Mostrar frame en pantalla

    fps = 1 / (time.time() - start_frame_time) # Calcular FPS
    start_frame_time = time.time() # Reiniciar el contador de tiempo
   

    # Salir del programa si alguna de estas teclas son presionadas {ESC, q, SPACE} 
    if cv2.waitKey(1) in [27, ord('q'), 32]:
        break
