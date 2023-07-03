import cv2
import time
import numpy as np
import HandTrackingModule as htm
import autopy
import pyautogui
import math

wScr, hScr = autopy.screen.size()
wCam, hCam = 640,480
frameR = 100
smoothening = 7.5
scrollWeight = 3

# Index Finger Past & Current Location
plocX,plocY = 0,0
clocX,clocY = 0,0
# Center of Hand Past & Current Location
pHandX,pHandY = 0,0
cHandX,cHandY = 0,0

# OpenCV Video Capture & Detection
cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
detector = htm.HandDetector(maxHands=1)

# Window Volume Control
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
volMode = 0 # 0: off, 1: on

# FPS Calculation
cTime = 0
pTime = 0

while True:
    # Find Hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)

    # Valid Mouse Movement Range Box
    cv2.rectangle(img,(frameR,frameR),(wCam-frameR,hCam-frameR),(255,0,255),2)
    
    keyInput = cv2.waitKey(1)
    # Escape Key
    if keyInput == 27: # esc : 27
        break
    elif len(lmList) == 0:
        pass
    # Volume Manage Mode Off
    elif keyInput == 115 and volMode == 1:
        volMode = 0
    # Volume Manage Mode On
    elif keyInput == 115 or volMode == 1: # s : 115
        volMode = 1
        cv2.rectangle(img,(50,150),(85,400),(0,255,0),3)
        cv2.rectangle(img,(50,int(volBar)),(85,400),(0,255,0),cv2.FILLED)
        cv2.putText(img,f"{int(volPer)}%",(40,450),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

        x1,y1 = lmList[4][1], lmList[4][2]
        x2,y2 = lmList[8][1], lmList[8][2]
        cx,cy = (x1+x2)//2, (y1+y2)//2
        cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
        cv2.circle(img,(x2,y2),15,(255,0,255),cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)
        cv2.circle(img,(cx,cy),15,(255,0,255),cv2.FILLED)
        length = math.hypot(x2-x1,y2-y1)

        # Hand range 50 ~ 250
        # Volume range -96 ~ 0
        vol = np.interp(length,[20,200],[minVol,maxVol])
        volBar = np.interp(length,[20,200],[400,150])
        volPer = np.interp(length,[20,200],[0,100])
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img,(cx,cy),15,(0,255,0),cv2.FILLED)
    # Basic Mouse Mode
    else:
        x1, y1 = lmList[8][1:]  # Index Finger
        x2, y2 = lmList[12][1:] # Middle Finger
        handX,handY = lmList[9][1:] # Center of Hand
    
        fingers = detector.fingersUp()

        # Convert Coordinates
        x3 = np.interp(x1,(frameR,wCam-frameR),(0,wScr))
        y3 = np.interp(y1,(frameR,hCam-frameR),(0,hScr))
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening

        handTmpX = np.interp(handX,(frameR,wCam-frameR),(0,wScr))
        handTmpY = np.interp(handY,(frameR,hCam-frameR),(0,hScr))
        cHandX = pHandX + (handTmpX - pHandX) / smoothening
        cHandY = pHandY + (handTmpY - pHandY) / smoothening

        # Moving Mode: Only Index Finger
        if fingers[1] == 1 and fingers[2] == 0:
            x3_flip = min(wScr - clocX,wScr - 0.01)
            y3 = min(y3,hScr - 0.01)
            cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
            autopy.mouse.move(x3_flip,y3)
        
        # Click Mode
        if fingers[1] == 1 and fingers[2] == 1 and sum(fingers) <= 3:
            length,img,lineInfo = detector.findDistance(8,12,img)
            if length < 30:
                cv2.circle(img,(lineInfo[-2],lineInfo[-1]),15,(0,255,0),cv2.FILLED)
                autopy.mouse.click()

        # Scroll Mode
        if sum(fingers) >= 4:
            cv2.circle(img,(handX,handY),15,(255,0,255),cv2.FILLED)
            pyautogui.scroll(round(float(cHandY-pHandY)*scrollWeight),3)

        pHandX, pHandY = cHandX, cHandY
        plocX, plocY = clocX, clocY

    # Frame Rate
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img,f"Fps: {int(fps)}",(20,50),cv2.FONT_HERSHEY_PLAIN,2,(255,0,255),2)

    # Display
    cv2.imshow("Img",img)

cap.release()
cv2.destroyAllWindows()