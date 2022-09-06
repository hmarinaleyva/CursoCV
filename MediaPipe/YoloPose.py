import os
import matplotlib.pyplot as plt

from PIL import Image
import cv2

import mediapipe as mp
from mediapipe.python.solutions import pose as mp_pose

#si está usando colab
#desde google.colab.patches importar cv2_imshow
#Centro PyTorch
import torch

#Modelo
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Detectar solo la clase "persona"
yolo_model.classes=[0]

mp_drawing = mp.solutions.drawing_utils
mp_pose =mp.solutions.pose

#obtener la dimensión del vídeo
cap = cv2.VideoCapture(0)
success, frame = cap.read()
height, width, _ = frame.shape
size = (width, height)

#para webacam cv2. VideoCapture(NUM) NUM -> 0,1,2 para cámaras web primarias y secundarias.
#Para guardar el archivo de video como salida.avi
out = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 20, size)
while cap.isOpened():    
    success, frame = cap.read()
    if not success:
        break

    #Recolorear feed de RGB a BGR
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #Hacer que la imagen se pueda escribir en falso mejora la predicción
    image.flags.writeable = False 

    result = yolo_model(image)
    
    #Vuelva a colorear la imagen a BGR para su representación
    image.flags.writeable = True   
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    #print(result.xyxy) # predicciones img1 (tensor)
    #Esta matriz contendrá recortes de imágenes en caso de que la necesitemos
    img_list =[]
    
    #necesitamos un margen delimitador adicional para que los cultivos humanos se detecten correctamente
    MARGIN=10

    for (xmin, ymin, xmax, ymax, confidence, clas) in result.xyxy[0].tolist():
      with mp_pose.Pose(min_detection_confidence=0.3, min_tracking_confidence=0.3) as pose:
        #Predicción de postura de medios, somos
        results = pose.process(image[int(ymin)+MARGIN:int(ymax)+MARGIN,int(xmin)+MARGIN:int(xmax)+MARGIN:])

        #Dibuje puntos de referencia en la imagen, si esto es confuso, considere pasar por el corte de matriz numpy
        mp_drawing.draw_landmarks(image[int(ymin)+MARGIN:int(ymax)+MARGIN,int(xmin)+MARGIN:int(xmax)+MARGIN:], results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                            mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                            ) 
        img_list.append(image[int(ymin):int(ymax),int(xmin):int(xmax):])

    #escribir en el archivo de vídeo
    out.write(image)

    #Código para salir del vídeo en caso de que esté utilizando la cámara web
    cv2.imshow('Activity recognition', image)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
#out.release()
#Cv2.destruir todas las ventanas()