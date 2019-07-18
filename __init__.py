import sys
from enum import Enum
import time
import cv2
import numpy
from PIL import ImageGrab
from PIL import Image
import pyautogui
import random
import pytweening


# Setting a bezier curve on mouse movement to simulate an human
# Code from: https://github.com/asweigart/pyautogui/issues/80
def getPointOnCurve(x1, y1, x2, y2, n, tween=None, offset=0):
    if getPointOnCurve.tween and getPointOnCurve.offset:
        tween = getPointOnCurve.tween               
        offset = getPointOnCurve.offset             
    x = ((x2 - x1) * n) + x1
    y = ((y2 - y1) * n) + y1
    if tween and offset:
        offset = (n - tween(n)) * offset
        if abs(x2 - x1) > abs(y2 - y1):
            y += offset
        else:
            x += offset
    return (x, y)

getPointOnCurve.tween = None
getPointOnCurve.offset = 0

def set_curve(func, tween=None, offset=0):
   func.tween = tween
   func.offset = offset

pyautogui.getPointOnLine = getPointOnCurve 
set_curve(getPointOnCurve, pytweening.easeInOutCubic, 300)


# Images
class _img():
    matchsearch = cv2.imread("images/matchsearch.jpg")
    inqueue = cv2.imread("images/inqueue.jpg")
    loadingscreen = cv2.imread("images/loadingscreen.jpg")
    matchfound = cv2.imread("images/matchfound.jpg")
    gamestarted = cv2.imread("images/gamestarted.jpg")
    defeat = cv2.imread("images/defeat.jpg")
    playagain = cv2.imread("images/playagain.jpg")
    surrender = cv2.imread("images/surrender.jpg")

class Stage(Enum):
    LauncherMenu = 1
    InQueue = 2
    MatchAccepted = 3
    LoadingScreen = 4
    GameStarted = 5
    GameFinished = 6

# Init
threshold = 0.8

def GrabScreenshot():
    return ImageGrab.grab().convert("RGB")
        

def LookFor(item, screenshot):
    screen = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)
    result = cv2.matchTemplate(screen, item, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        return max_loc
    return None


def Click(loc, item):
    x, y = loc
    item_height,item_width,tq = item.shape
    pyautogui.moveTo(x+(item_width/2), y+(item_height/2),.5)
    pyautogui.mouseDown()
    time.sleep(.3)
    pyautogui.mouseUp()
    #Randomize idle mouse returned position to not look like a robot
    pyautogui.moveTo(500+random.randint(0,700), 300+random.randint(0,300), .5)

def Surrender():
    print("Typing surrender")
    pyautogui.mouseDown()
    time.sleep(.3)
    pyautogui.mouseUp()
    pyautogui.press('enter')
    time.sleep(.5)
    pyautogui.typewrite('/')
    time.sleep(.5)
    pyautogui.typewrite('f')
    time.sleep(.5)
    pyautogui.typewrite('f')
    time.sleep(.5)
    pyautogui.press('enter')
    time.sleep(3)

def progress(count):
    width = 40
    completed = int(count * width / 10)
    display = '#' * completed + '_' * (width - completed)
    sys.stdout.write('[%s] Waiting 10 minutes\r' % display)
    sys.stdout.flush()

def WaitForMatchEnd():
    print("Waiting 10 minutes")
    progress(0)
    for x in range(10):
        time.sleep(60)
        progress(x+1)
    sys.stdout.write('\n')


_stage = Stage.LauncherMenu

while True:
    time.sleep(1)
    screenshot = GrabScreenshot()

    if _stage == Stage.LauncherMenu:
        print("Looking for play button")
        _loc = LookFor(_img.playagain, screenshot)
        if _loc != None:
            Click(_loc, _img.playagain)
        else:
            _loc = LookFor(_img.matchsearch, screenshot)
            if _loc != None:
                Click(_loc, _img.matchsearch)
                _stage = Stage.InQueue
                print("Looking for a match")
        next

    if _stage == Stage.InQueue:
        _loc = LookFor(_img.matchfound, screenshot)
        if _loc != None:
            Click(_loc, _img.matchfound)
            print("Match accepted")
        else:
            _loc = LookFor(_img.loadingscreen, screenshot)
            if _loc != None:
                _stage = Stage.LoadingScreen
                print("On Loading Screen")
                time.sleep(60)
        next
    
    if _stage == Stage.LoadingScreen:
        _loc = LookFor(_img.gamestarted, screenshot)
        if _loc != None:
            _stage = Stage.GameStarted
            print("Game Started")

    if _stage == Stage.GameStarted:
        WaitForMatchEnd()
        _stage = Stage.GameFinished
        next

    if _stage == Stage.GameFinished:
        Surrender()
        screenshot = GrabScreenshot()
        _loc = LookFor(_img.surrender, screenshot)
        if _loc != None:
            Click(_loc, _img.surrender)
            _stage = Stage.LauncherMenu