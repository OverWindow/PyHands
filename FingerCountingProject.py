import cv2
import time
import HandTrackingModule as htm

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

cTime = 0
pTime = 0

detector = htm.HandDetector(detectionCon=0.75)

tipIds = [4,8,12,16,20]


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)


    if len(lmList) != 0:
        fingers = []
        if (lmList[5][1] < lmList[4][1] and lmList[4][1] < lmList[17][1]) or (lmList[17][1] < lmList[4][1] and lmList[4][1] < lmList[5][1]):
            fingers.append(0)
        else:
            fingers.append(1)

        for id in range(1,5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        # print(fingers)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img,f"FPS: {int(fps)}",(40,50),cv2.FONT_HERSHEY_COMPLEX,3,(0,255,0),3)
    cv2.imshow("Img",img)
    keyInput = cv2.waitKey(1)
    if keyInput == 27:
        break