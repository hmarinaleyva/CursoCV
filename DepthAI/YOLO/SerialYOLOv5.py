#!/usr/bin/env python3

import serial, subprocess

try:
    InfoBoard = subprocess.getoutput('arduino-cli board list').split()
    PuertoArduino  = InfoBoard[9] # Obtener el puerto de la placa Arduino
    FQBN  = InfoBoard[16] # Obtener el FQBN de la placa Arduino
    ArduinoSerial = serial.Serial(PuertoArduino, 9600, timeout=1) # open the serial port
except:
    print("No se estableció comunicación serial con una placa Arduino correctamente")
    exit()

import os, time
import cv2
import depthai as dai
import numpy as np
from Utilities.YoloFunctions import non_max_suppression

# Cambiar la ruta de ejecución aquí
MainDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(MainDir)

# Ruta del modelo de la red neuronal entrenada para la deteción de objetos y parámetros de entrada
nn_path = os.path.join(MainDir, './YoloModels', "YOLOv5sDefault.blob")
conf_thresh = 0.3   # Establecer el umbral de confianza
iou_thresh = 0.4    # Establecer el umbral de IoU de NMS
nn_shape = 416      # resolución de la imagen de entrada de la red neuronal
labelMap = [        # Establecer el mapa de etiquetas de la red neuronal
    "Persona",   "Bicicleta", "Auto",      "Moto",      "Avión",      "Autobús",     "Tren",
    "Camión",    "Barco",     "Semáforo",  "Grifo",     "Stop",       "Parquímetro", "Banco",
    "Pájaro",    "Gato",      "Perro",     "Caballo",   "Oveja",      "Vaca",        "Elefante",
    "Oso",       "Cebra",     "Jirafa",    "Mochila",   "Paraguas",   "Bolso",       "Corbata",
    "Maleta",    "Frisbee",   "Esquís",    "Snowboard", "Pelota",     "Cometa",      "Bate",
    "Guante",    "Monopatín", "Surf",      "Raqueta",   "Botella",    "Copa",        "Taza",
    "Tenedor",   "Cuchillo",  "Cuchara",   "Cuenco",    "Plátano",    "Manzana",     "Sándwich",
    "Naranja",   "Brócoli",   "Zanahoria", "Hot-Hog",   "Pizza",      "Dona",        "Pastel",
    "Silla",     "Sofá",      "Maceta",    "Cama",      "Comedor",    "Baño",        "TV",
    "Portátil",  "Ratón",     "mando",     "Teclado",   "SmartPhone", "Microondas",  "Horno",
    "Tostadora", "Fregadero", "Nevera",    "Libro",     "Reloj",      "Jarrón",      "Tijeras",
    "Peluche",   "Secador",   "Cepillo"
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
device = dai.Device(pipeline)# pipeline definido, ahora se asigna el dispositivo y se inicia la pipeline
# Las colas de salida se utilizarán para obtener las tramas rgb y los datos nn de las salidas definidas anteriormente
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

fps = 0
start_frame_time = 0
BoxesColor = (0, 255, 0)
LineColor = (0, 0, 255)
CircleColor = (255, 0, 0)
TextColor = (255,255,255)
FontFace = cv2.FONT_HERSHEY_TRIPLEX # Fuente de texto

# Coordenadas del centro de la imagen
x0 = nn_shape//2
y0 = nn_shape//2

while True:
    
    # Iniciar el contador de tiempo para calcular los FPS
    start_frame_time = time.time() 
    
    # Salir del programa si alguna de estas teclas son presionadas {ESC, SPACE, q} 
    if cv2.waitKey(1) in [27, 32, ord('q')]:
        break

    # Obtener fotograma de la cámara OAK-D y la salida de la red neuronal compilada en el dispositivo
    frame, boxes = GetBoundingBoxes(q_nn_input, q_nn)



    # Si hay objetos detectados 
    if boxes is not None and boxes.ndim != 0:

        # Coordenadas del centro de los objetos detectados
        DetectionCentroids = []

        # Distancias hw entre el centro de la imagen y el centro de los objetos detectados
        Distances = []

        # Para cada objeto detectado
        for i in range(boxes.shape[0]): 
            
            # Extraer los datos de la caja delimitadora
            x1, y1, x2, y2 = int(boxes[i,0]), int(boxes[i,1]), int(boxes[i,2]), int(boxes[i,3]) # Coordenadas de la caja delimitadora
            conf, class_index = boxes[i, 4], int(boxes[i, 5]) # Extraer la confianza y el índice de la clase de la predicción

            # Calcular las cordenadas del centro de la caja delimitadora
            x = int((x1+x2)/2) # coordenada horizontal del centro de la caja delimitadora
            y = int((y1+y2)/2) # coordenada vertical del centro de la caja delimitadora
            DetectionCentroids.append((x,y)) # Agregar las coordenadas del centro de la caja delimitadora a la lista DetectionCentroids

            # Sumar la distancia vetical y horizontal (hw) entre el centro de la caja delimitadora y el centro de la imagen
            hw = abs(x-x0) + abs(y-y0)
            Distances.append(hw) # Agregar la distancia hw a la lista Distances

            # Dibujar en el fotograma actual marcas de interés
            label = f"{labelMap[class_index]}: {conf:.2f}" # Crear etiqueta de la clase predicha
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), BoxesColor, 1) # Dibujar caja de detección
            (w, h), _ = cv2.getTextSize(label, FontFace, 0.3, 1) # Obtener el ancho y alto de la etiqueta
            frame = cv2.rectangle(frame, (x1, y1 - 2*h), (x1 + w, y1), BoxesColor, -1) # Dibuja el recuadro de la etiqueta
            frame = cv2.putText(frame, label, (x1, y1 - 5), FontFace, 0.3, TextColor, 1) # Dibuja el texto de la etiqueta
            frame = cv2.circle(frame, (x, y), 2, CircleColor, 2) # Dibuja un círculo en el centro de la caja de detección

        # Obtener las coordenadas del centro de la caja delimitadora más cercana
        NeighborObjectPosition = DetectionCentroids[Distances.index(min(Distances))]

        # Trazar una línea desde el centro de la imagen hasta el centro de la caja delimitadora más cercana
        cv2.line(frame, (x0, y0), NeighborObjectPosition, LineColor, 2)

    # Mostar el fotograma en una ventana
    fps = 1 / (time.time() - start_frame_time) # Calcular FPS
    cv2.putText(frame, "FPS: {:.2f}".format(fps), (2, frame.shape[0] - 4), FontFace, 0.75, TextColor) # Mostrar FPS
    cv2.imshow("YOLOv5Hands", frame)  # Mostrar frame en pantalla