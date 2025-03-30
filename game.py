# import math
# import random
import random
import time

import cv2
import pygame
# import tkinter as tk
from tkinter import messagebox
from cvzone.HandTrackingModule import HandDetector

width = 500
height = 500

cols = 25
rows = 20


class Cube:
    rows = 20
    w = 500

    def __init__(self, start, dirnx=1, dirny=0, color=(255, 0, 0)):
        self.pos = start
        self.dirnx = dirnx
        self.dirny = dirny  # "L", "R", "U", "D"
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMiddle = (i * dis + centre - radius, j * dis + 8)
            circleMiddle2 = (i * dis + dis - radius * 2, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)


class snake():
    body = []
    turns = {}

    def __init__(self, color, pos):
        # pos is given as coordinates on the grid ex (1,5)
        self.color = color
        self.head = Cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self, coords):
        if coords:
            (hx, hy) = (self.head.pos[0]/20, self.head.pos[1]/20)
            (x, y) = coords
            if x > hx:
                if y > hy:
                    if x-hx > y-hy:#350deg
                        self.dirnx = 1
                        self.dirny = 0
                        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                    elif x-hx < y-hy:#280deg
                        self.dirny = 1
                        self.dirnx = 0
                        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif y < hy:
                    if x - hx > -(y - hy):#10deg
                        self.dirnx = 1
                        self.dirny = 0
                        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                    elif x - hx < -(y - hy):  # 80deg
                        self.dirny = -1
                        self.dirnx = 0
                        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
            elif x < hx:
                if y > hy:
                    if -(x-hx) > y-hy:#190deg
                        self.dirnx = -1
                        self.dirny = 0
                        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                    elif -(x-hx) < y-hy:#260deg
                        self.dirny = 1
                        self.dirnx = 0
                        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif y < hy:
                    if -(x - hx) > -(y - hy):#170deg
                        self.dirnx = -1
                        self.dirny = 0
                        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                    elif -(x - hx) < -(y - hy):  # 100deg
                        self.dirny = -1
                        self.dirnx = 0
                        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            keys = pygame.key.get_pressed()

            for key in keys:
                if keys[pygame.K_LEFT]:
                    self.dirnx = -1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_RIGHT]:
                    self.dirnx = 1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_UP]:
                    self.dirny = -1
                    self.dirnx = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_DOWN]:
                    self.dirny = 1
                    self.dirnx = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        self.head = Cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0] - 1, tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1)))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

class Detection:
    def __init__(self):
        # Initialize the webcam to capture video
        # The '2' indicates the third camera connected to your computer; '0' would usually refer to the built-in camera
        self.cap = cv2.VideoCapture(0)
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # Initialize the HandDetector class with the given parameters
        self.detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

    def detect_hands(self):
        # Capture each frame from the webcam
        # 'success' will be True if the frame is successfully captured, 'img' will contain the frame
        success, img = self.cap.read()
        img = cv2.flip(img, 1)
        # Find hands in the current frame
        # The 'draw' parameter draws landmarks and hand outlines on the image if set to True
        # The 'flipType' parameter flips the image, making it easier for some detections
        hands, img = self.detector.findHands(img, draw=True, flipType= True)

        # Check if any hands are detected
        if hands:
            # Information for the first hand detected
            hand1 = hands[0]  # Get the first hand detected
            lmList1 = hand1["lmList"]  # List of 21 landmarks for the first hand
            bbox1 = hand1["bbox"]  # Bounding box around the first hand (x,y,w,h coordinates)
            center1 = hand1['center']  # Center coordinates of the first hand
            handType1 = hand1["type"]  # Type of the first hand ("Left" or "Right")

            # Count the number of fingers up for the first hand
            fingers1 = self.detector.fingersUp(hand1)
            print(f'H1 = {fingers1.count(1)}', end=" ")  # Print the count of fingers that are up
            # Calculate distance between specific landmarks on the first hand and draw it on the image
            length, info, img = self.detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img, color=(255, 0, 255),
                                                           scale=10)
            print(f"\n{hand1}")
            # Check if a second hand is detected
            if len(hands) == 2:
                # Information for the second hand
                hand2 = hands[1]
                lmList2 = hand2["lmList"]
                bbox2 = hand2["bbox"]
                center2 = hand2['center']
                handType2 = hand2["type"]

                # Count the number of fingers up for the second hand
                fingers2 = self.detector.fingersUp(hand2)
                print(f'H2 = {fingers2.count(1)}', end=" ")

                # Calculate distance between the index fingers of both hands and draw it on the image
                length, info, img = self.detector.findDistance(lmList1[8][0:2], lmList2[8][0:2], img, color=(255, 0, 0),
                                                               scale=10)
                print(f"\n{hand2}")
                return [2, hand1, hand2]
            else:
                return [1, hand1]
        else:
            return None
        # # Display the image in a window
        # cv2.imshow("Image", img)
    def scale(self, dom_hand):
        hands = self.detect_hands()
        if hands and hands[0] == 1 :
            hand = hands[1]
            if hand['type'] == dom_hand:
                position = hand['lmList'][8]
                scales = (position[0]/self.width, position[1]/self.height)
                return scales


def redrawWindow(finger_pos=None):  # 修改函数以接收手指位置参数
    global win
    win.fill((0, 0, 0))
    drawGrid(width, rows, win)
    s.draw(win)
    snack.draw(win)

    # 绘制黄色手指位置格子
    if finger_pos:
        dis = width // rows
        i, j = finger_pos
        pygame.draw.rect(win, (255, 255, 0), (i * dis + 1, j * dis + 1, dis - 2, dis - 2))

    pygame.display.update()

def drawGrid(w, rows, surface):
    sizeBtwn = w // rows

    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, w))
        pygame.draw.line(surface, (255, 255, 255), (0, y), (w, y))


def randomSnack(rows, item):
    positions = item.body

    while True:
        x = random.randrange(1, rows - 1)
        y = random.randrange(1, rows - 1)
        if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
            continue
        else:
            break

    return (x, y)


def game_main():
    global s, snack, win
    win = pygame.display.set_mode((width, height))
    s = snake((255, 0, 0), (10, 10))
    s.addCube()
    snack = Cube(randomSnack(rows, s), color=(0, 255, 0))
    flag = True
    clock = pygame.time.Clock()

    while flag:
        pygame.time.delay(100)
        clock.tick(2)
        coordinates = control.scale(use_hand)

        # 转换手指坐标到格子坐标
        finger_pos = None
        if coordinates:
            # 将归一化坐标转换为实际像素坐标
            x = int(coordinates[0] * width)
            y = int(coordinates[1] * height)
            # 转换为格子坐标
            grid_size = width // rows
            i = x // grid_size
            j = y // grid_size
            finger_pos = (i, j)

        s.move(coordinates)
        headPos = s.head.pos

        if headPos[0] >= 20 or headPos[0] < 0 or headPos[1] >= 20 or headPos[1] < 0:
            print("Score:", len(s.body))
            s.reset((10, 10))
            messagebox.showinfo('GAME OVER',f"You died because of colliding with the boundaries!\n"
                                            f"Score:{len(s.body)}")
            with open("history.txt", 'a+') as f:
                f.write(f'\n score:{len(s.body)} at {time.time()}')
            pygame.quit()
        if s.body[0].pos == snack.pos:
            s.addCube()
            snack = Cube(randomSnack(rows, s), color=(0, 255, 0))

        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z: z.pos, s.body[x + 1:])):
                print("Score:", len(s.body))
                s.reset((10, 10))
                messagebox.showinfo('GAME OVER', f"You died due to biting yourself!\n"
                                                 f"Score:{len(s.body)}")
                with open("history.txt", 'a+') as f:
                    f.write(f'\n score:{len(s.body)} at {time.time()}')
                pygame.quit()
                break

        redrawWindow(finger_pos)

def main():
    global use_hand, control
    use_hand = 'Right'
    control = Detection()
    i = 5
    print("Please raise your Dominant hand.")
    while i:
        hands = control.detect_hands()
        if hands and hands[0] == 1:
            i -=1
            use_hand = hands[1]['type']
        time.sleep(0.25)
    print(f"Dominant hand set to: {use_hand}")
    print(control.scale(use_hand))
    game_main()



main()


