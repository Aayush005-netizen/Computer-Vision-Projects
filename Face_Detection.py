import cv2
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
webcam = cv2.VideoCapture(0)

while True:
    _ , img = webcam.read() #We do not require the first value
    img = cv2.flip(img, 1) #Flip the image to avoid mirror view
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #Convert the image to grayscale
    faces = face_cascade.detectMultiScale(gray, 1.5, 4) #Detect the faces in the image
    for x,y,w,h in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 3) #Draw a rectangle around the face
    cv2.imshow("Face Detector", img) #Display the output
    key = cv2.waitKey(10)
    if key == 27: #ESC key to stop the webcam
        break

webcam.release()
cv2.destroyAllWindows()
