import pyfirmata
from pyfirmata import Arduino, SERVO, util
from time import sleep
import cv2
import time
import os
import HandTrackModule as htm
import pyfirmata
import keyboard

folderPath = "Arrows"
myList = os.listdir(folderPath)
overlayList = []

for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)

upArrow = overlayList[2]
downArrow = overlayList[3]
upArrowOn = overlayList[4]
downArrowOn = overlayList[5]

port = 'COM3'

clawPin = 9
LRPin = 7
rMotorPin = 8
lMotorPin = 6

drawColor = (255,0,255)

board = Arduino(port)

board.digital[clawPin].mode = SERVO
board.digital[LRPin].mode = SERVO
board.digital[rMotorPin].mode = SERVO
board.digital[lMotorPin].mode = SERVO

def rotateServo(pin,angle):
    board.digital[pin].write(angle)
    sleep(0.015)


cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
prevTime = 0

detector = htm.handDetector(detectionConfidence= 0.75)

#mediapipe fingertip values
tipIds = [4,8,12,16,20]

rotateServo(LRPin, 90)

while True:
#Import Image
    success, img = cap.read()
    img = detector.findHands(img)
    img = cv2.flip(img, 1)   #flips webcam image
    landmarkList = detector.findPosition(img, draw=False)

############################################
#Controller Display Initialization
    #RMotorArrowup Overlay
    img[40:220,1050:1230] = upArrow
    #RMotorArrowdown Overlay
    img[500:680,1050:1230] = downArrow
    #LMotorArrowup Overlay
    img[40:220,780:960] = upArrow
    #LMotorArrowdown Overlay
    img[500:680,780:960] = downArrow
#############################################

    if len(landmarkList) != 0:
        x1, y1 = landmarkList[8][1:]
        x2, y2 = landmarkList[12][1:]

        fingers = []
        # Thumb
        if landmarkList[tipIds[0]][1] > landmarkList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # comparing y coord of tip of finger to its' center (excluding thumb),
        # CV orientation y increases as it goes downward
        for id in range(1, 5):
            if landmarkList[tipIds[id]][2] < landmarkList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        # print(fingers)
        totalFingers = fingers.count(1)
        print(totalFingers)

        checkFingers =detector.fingersUp()

        #Virtual Controller

        #Select mode index and middle
        if checkFingers[1] and checkFingers[2] and totalFingers == 2:
            print("Select mode")

            # Right Motor Control
            if 50 < x1 < 230 :
                print('right')
                if 40 < y1 < 220:
                    print('up arrow')
                    rotateServo(rMotorPin, 240)
                    # RMotorArrowup Overlay
                    img[40:220, 1050:1230] = upArrowOn

                elif 500 < y1 < 680:
                    print('down arrow')
                    rotateServo(rMotorPin, 40)
                    # RMotorArrowdown Overlay
                    img[500:680, 1050:1230] = downArrowOn

            # Left Motor Control
            elif 320 < x1 < 500:
                print('left')
                if 40 < y1 < 220:
                    print('up arrow')
                    rotateServo(lMotorPin, 240)
                    # LMotorArrowup Overlay
                    img[40:220, 780:960] = upArrowOn

                elif 500 < y1 < 680:
                    print('down arrow')
                    rotateServo(lMotorPin, 0)
                    # LMotorArrowdown Overlay
                    img[500:680, 780:960] = downArrowOn


        #Claw controls
        if (totalFingers == 5):
            rotateServo(clawPin,90)
            cv2.putText(img, f"CLAW OPEN", (40, 100), cv2.FONT_HERSHEY_COMPLEX,
                        1, (0, 255,0), 2)

        elif (totalFingers == 0):
            rotateServo(clawPin,0)
            cv2.putText(img, f"CLAW CLOSED", (40, 100), cv2.FONT_HERSHEY_COMPLEX,
                        1, (0, 0, 255), 2)

        #Consider physical control interface to avoid confusing movements
        #LRMotor
        elif (totalFingers == 1 and landmarkList[20][2] < landmarkList[18][2]):
            rotateServo(LRPin, 0)
            print('right')
        elif (totalFingers == 1 and landmarkList[4][1] > landmarkList[2][1]):
            rotateServo(LRPin, 180)
            print('left')
        elif (totalFingers == 3 and landmarkList[8][2] < landmarkList[6][2] and
              landmarkList[12][2] < landmarkList[10][2]
              and landmarkList[16][2] < landmarkList[14][2]):
            rotateServo(LRPin, 90)
            print('middle')


    if keyboard.is_pressed('q'):
        break

    currTime = time.time()
    fps = 1/(currTime-prevTime)
    prevTime = currTime

    cv2.putText(img, f"FPS: {int(fps)}", (40,50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255,0,0), 2)
    cv2.putText(img, f"L Motor", (800,360), cv2.FONT_HERSHEY_COMPLEX,
                1, (0,0,255), 2)
    cv2.putText(img, f"R Motor", (1075, 360), cv2.FONT_HERSHEY_COMPLEX,
                1, (0, 0, 255), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)

cv2.destroyAllWindows()
quit()