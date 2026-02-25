import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui

x1 = 0
y1 = 0
x2 = 0
y2 = 0

#Load Model
base_options = python.BaseOptions(
    model_asset_path='hand_landmarker.task'
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2
)

detector = vision.HandLandmarker.create_from_options(options)
webcam = cv2.VideoCapture(0)


while True:
    ret, image  = webcam.read() #We do not require the first value
    image = cv2.flip(image, 1) #Flip the image to avoid mirror view
    frame_height , frame_width, _ = image.shape #Get the height and width of the frame
    rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #Convert the image to RGB format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img) #Convert the image to mediapipe format
    results = detector.detect(mp_image) #Detect the hands in the image

    if results.hand_landmarks:
        for hand in results.hand_landmarks:
            
            for id, landmark in enumerate(hand):
                x= int(landmark.x * frame_width)
                y= int(landmark.y * frame_height)
                if id == 8: #ForeFinger tip
                    cv2.circle(img = image, center=(x,y), radius=8 , color=(0,255,255), thickness=3)
                    x1 = x
                    y1 = y
                if id == 4: #Thumb tip
                    cv2.circle(img = image, center=(x,y), radius=8 , color=(0,0,255), thickness=3)
                    x2 = x
                    y2 = y
        
        dist = (((x2-x1)**2 + (y2-y1)**2)**0.5)//4 #Calculate the distance between the thumb and forefinger
        cv2.line(image, (x1,y1), (x2,y2), (0,255,0), 3) #Draw a line between the thumb and forefinger
        if dist > 30:
            pyautogui.press("volumeup") #Increase the volume
        else:
            pyautogui.press("volumedown") #Decrease the volume


    cv2.imshow("Hand Gesture Volume Controller", image) #Display the output


    key = cv2.waitKey(10)
    if key == 27: #ESC key to stop the webcam
        break

webcam.release()
cv2.destroyAllWindows()