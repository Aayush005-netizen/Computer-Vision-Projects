import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import time

# -------------------------------
# Load MediaPipe Hand Model
# -------------------------------
base_options = python.BaseOptions(
    model_asset_path="hand_landmarker.task"
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)

detector = vision.HandLandmarker.create_from_options(options)

# -------------------------------
# Finger State Function
# -------------------------------
def fingers_up(hand):
    tips = [4,8,12,16,20]
    fingers = []

    # Thumb (Left + Right Hand Compatible)
    if abs(hand[4].x - hand[3].x) > 0.03:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other Fingers
    for tip in tips[1:]:
        if hand[tip].y < hand[tip-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

# -------------------------------
# Variables
# -------------------------------
x1=y1=x2=y2=0
prev_action = ""
is_muted = False

# -------------------------------
# Webcam Start
# -------------------------------
webcam = cv2.VideoCapture(0)

while True:
    ret, image = webcam.read()
    image = cv2.flip(image,1)
    h,w,_ = image.shape

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        for hand in result.hand_landmarks:

            # Draw landmarks
            for id,landmark in enumerate(hand):
                x = int(landmark.x * w)
                y = int(landmark.y * h)

                if id==8:
                    x1,y1=x,y
                    cv2.circle(image,(x,y),8,(0,255,255),3)

                if id==4:
                    x2,y2=x,y
                    cv2.circle(image,(x,y),8,(0,0,255),3)

                cv2.circle(image,(x,y),2,(0,255,0),-1)

            # -------------------------------
            # Gesture Logic
            # -------------------------------
            finger_state = fingers_up(hand)
            total_fingers = finger_state.count(1)

            # ✋ Open Palm → Pause
            if total_fingers == 5:
                cv2.putText(image,"PAUSED",(20,60),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),3)
                prev_action = "pause"

            # ✊ Fist → Mute
            elif total_fingers == 0:
                if prev_action != "fist":
                    pyautogui.press("volumemute")
                    is_muted = not is_muted
                    if is_muted:
                        print("Muted")
                    else:
                        print("Unmuted")
                    prev_action = "fist"
                    time.sleep(0.7)
                # else:
                #     pyautogui.press("volumemute")
                #     prev_action = "unmute"
                #     time.sleep(1)

            # 👉 Thumb + Index → Volume Control
            else:
                dist = (((x2-x1)**2 + (y2-y1)**2)**0.5)//4
                palm_x1 = int(hand[0].x * w)
                palm_y1 = int(hand[0].y * h)

                palm_x2 = int(hand[9].x * w)
                plam_y2 = int(hand[9].y * h)

                palm_size = (((palm_x2-palm_x1)**2 + (plam_y2-palm_y1)**2)**0.5)

                if palm_size !=0:
                    dist = dist/palm_size
                else:
                    dist = 0
                
                cv2.line(image,(x1,y1),(x2,y2),(0,255,0),4)

                if dist > 0.3:
                    pyautogui.press("volumeup")
                else:
                    pyautogui.press("volumedown")

                prev_action = "volume"
                time.sleep(0.1)

    cv2.imshow("Hand Gesture Volume Controller", image)

    if cv2.waitKey(10)==27:
        break

webcam.release()
cv2.destroyAllWindows()