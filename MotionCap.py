from cvzone.PoseModule import PoseDetector
import cv2
# import numpy as np
import socket
import time
# import os

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Initialize the PoseDetector class with the given parameters
detector = PoseDetector(staticMode=False,
                        modelComplexity=1,
                        smoothLandmarks=True,
                        enableSegmentation=False,
                        smoothSegmentation=True,
                        detectionCon=0.5,
                        trackCon=0.5)

# decide whether to connect
whether_to_connect = input('Do you want to connect to Unity? Press enter to skip, enter any word to confirm.')

# 初始化动作列表
posList = []
for i in range(20):
    posList.append([])
print(f"length of the list: {len(posList)}")

lastLeap = 0
###---------------------initialization ends here-----------------------###

def connect_unity(host, port):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock = socket.socket()
    sock.connect((host, port))
    print('连接已建立')


def send_to_unity(content_list):
    data = '' + ','.join([str(elem) for elem in content_list]) + ''  # 每个float用,分割
    sock.sendall(bytes(data, encoding="utf-8"))  # 发送数据
    print("向unity发送：", content_list)

def rec_from_unity():
    data = sock.recv(1024)
    data = str(data, encoding='utf-8')
    data = data.split(',')
    new_data = []
    for d in data:
        new_data.append(float(d))
    print('从环境接收：', new_data)
    return new_data

def check_leap():
    if posList[19]:
        pose1 = posList[0][1][1]
        pose2 = posList[1][1][1]
        if pose2 - pose1 >= 10 and time.time() - lastLeap > 0.5 :
            return True
        else:
            return False
    else:
        return False

def record_default(default_value_list):
    global default_position_list
    default_position_list = default_value_list.remove(1.0)



###---------------definition ends here------------------------###


if whether_to_connect:
    host = '127.0.0.1'
    port = 5005
    connect_unity(host, port)
# Loop to continuously get frames from the webcam
while True:
    # Capture each frame from the webcam
    success, img = cap.read()

    # Find the human pose in the frame
    img = detector.findPose(img)

    # Find the landmarks, bounding box, and center of the body in the frame
    # Set draw=True to draw the landmarks and bounding box on the image
    lmList, bboxInfo = detector.findPosition(img, draw=True, bboxWithHands=False)

    # Check if any body landmarks are detected
    if lmList:
        # Get the center of the bounding box around the body
        center = bboxInfo["center"]

        # Draw a circle at the center of the bounding box
        cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

        # Calculate the distance between landmarks 11 and 15 and draw it on the image
        length, img, info = detector.findDistance(lmList[11][0:2],
                                                  lmList[15][0:2],
                                                  img=img,
                                                  color=(255, 0, 0),
                                                  scale=10)

        # Calculate the Angle between landmarks 11, 13, and 15 and draw it on the image
        leftAngle, img = detector.findAngle(lmList[11][0:2],
                                        lmList[13][0:2],
                                        lmList[15][0:2],
                                            img=img,
                                            color=(0, 0, 255),
                                            scale=10)
        # Calculate the Angle between landmarks 11, 13, and 15 and draw it on the image
        rightAngle, img = detector.findAngle(lmList[12][0:2],
                                            lmList[14][0:2],
                                            lmList[16][0:2],
                                            img=img,
                                            color=(0, 0, 255),
                                            scale=10)
        # Check if the leftAngle is close to 50 degrees with an offset of 10
        isLeftCloseAngle50 = detector.angleCheck(myAngle=leftAngle,
                                                 targetAngle=50,
                                                 offset=10)

        isRightCloseAngle310 = detector.angleCheck(myAngle=rightAngle,
                                                 targetAngle=310,
                                                 offset=10)
        # Print the result of the leftAngle check
        # print(isLeftCloseAngle50)
        if isLeftCloseAngle50:
            result = [float(1)] + lmList
        else:
            result = [float(0)] + lmList

        #set default
        if isLeftCloseAngle50 and isRightCloseAngle310:
            record_default(result)
            print("default value recorded")

        if whether_to_connect:
            send_to_unity(result)
            rec_from_unity()
        # print(result)
        print(len(result))

        #refresh the list
        for i in range(19):
            posList[19 - i] = posList[18 - i]
        posList[0] = result
        print(posList)

        if check_leap():
            print("Leap Detected")
            lastLeap = time.time()

    # Display the frame in a window
    cv2.imshow("Image", img)

    # Wait for 50 millisecond between each frame
    cv2.waitKey(50)