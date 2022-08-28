
import os

os.getcwd(path)

import serial, os, cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


hands = mp_hands.Hands( # create hands object
		max_num_hands=1,
		model_complexity=0,
		min_detection_confidence=0.5,
		min_tracking_confidence=0.5)

# function to return the position of the fingertips in a list
def fingertips_positions(results_hands, width, height):
    for hand_landmarks in results_hands.multi_hand_landmarks:   
        x0 = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * width)
        y0 = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * height)
        x1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width)
        y1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height)
        x2 = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * width)
        y2 = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * height)
        x3 = int(hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x * width)
        y3 = int(hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y * height)
        x4 = int(hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x * width)
        y4 = int(hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y * height)
    return [(x0,y0),(x1,y1),(x2,y2),(x3,y3),(x4,y4)]

# function to draw dots and labels at the position of the detected objects in the video frame
def draw_detected_objects(frame, objects_labels, objects_positions):
    for i, position in enumerate(objects_positions):
        cv2.circle(frame, position, 5, (0, 0, 255), 2)
        cv2.putText(frame, objects_labels[i], position, cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return frame

# frame capture
cap = cv2.VideoCapture(0)
success, frame = cap.read()
height, width, _ = frame.shape

# boolean flag to check if hand is detected
PrevFingerDetect  = False

# create loop to capture video
while cap.isOpened():
    # capture frame from video from cap
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    frame.flags.writeable = False                   # make frame read-only
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert frame to RGB

    results_hands = hands.process(frame)            # process frame with hands object
    
    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # check if hand is detected
    if results_hands.multi_hand_landmarks is not None:

        # check if hand is in the frame previously
        if not PrevFingerDetect:
            # Escribir en el centro de la del fotograma la palabra "HAND DETECTED"
            cv2.putText(frame, "HAND DETECTED", (int(width/2), int(height/2)), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
            # Enviar mensaje al Arduino para que suere el BUZZER mediante comunicación serial
            
            PrevFingerDetect = True
        
        fingertips = fingertips_positions(results_hands)                    # position points of fingertips detected
        fingertips_labels = ["0", "1", "2", "3", "4"]                       # labels of fingertips detected
        index_position = fingertips[1]                                      # position of index finger
        draw_detected_objects(frame, fingertips_labels, fingertips)         # draw dots and labels at the fingertip position on the frame            

    else:
        if PrevFingerDetect:
            # Escribir en el centro de la del fotograma la palabra "HAND NOT DETECTED"
            cv2.putText(frame, "HAND NOT DETECTED", (int(width), int(height)), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
            PrevFingerDetect = False

    # Flip the frame horizontally for a selfie-view display.
    cv2.imshow('manitos y cara', frame) #cv2.flip(frame, 1))

    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()


while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

    # To improve performance, optionally mark the frame as not writeable to
    # pass by reference.
    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Draw the face mesh annotations on the frame.
    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    results_hands = hands.process(frame)            # process frame with hands object
    
    # check if hand is detected
    if results_hands.multi_hand_landmarks is not None:
        
        fingertips = fingertips_positions(results_hands)                    # position points of fingertips detected
        fingertips_labels = ["0", "1", "2", "3", "4"]
        index_position = fingertips[1]                                      # position of index finger
        thumb_position = fingertips[0]                                      # position of thumb finger
        draw_detected_objects(frame, fingertips_labels, fingertips)         # draw dots and labels at the fingertip position on the frame            
        #if abs(index_position[0]-thumb_position[0])+abs(index_position[1]-thumb_position[1]) < delta_x+delta_y:
        #    draw_line(frame, index_position, thumb_position, (255,0,0))
        #else:
        #    draw_line(frame, index_position, thumb_position, (0,0,255))


    # Flip the frame horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Face Mesh', cv2.flip(frame, 1))
    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()