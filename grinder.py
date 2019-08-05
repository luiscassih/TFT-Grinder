# Author Luis C
# July 2019
# Disclaimer: I am not responsible for the consequences of using this script or getting you banned from Riot Games.
# This is only for educational purpose. Be warned the risk for its use.

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
    #presurrender = cv2.imread("images/presurrender.jpg")
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
matchesCount = 0
secondsToWait = 600
_stage = Stage(int(sys.argv[1])) if len(sys.argv) == 2 else Stage.LauncherMenu
startedLoading = None

def log(message):
    print(time.strftime("%d/%m/%Y %H:%M:%S >_"), message)

def GrabScreenshot():
    return ImageGrab.grab().convert("RGB")
        
def LookFor(item, screenshot):
    screen = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)
    result = cv2.matchTemplate(screen, item, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        return max_loc
    return None

def Click(loc, item, randomReturn = True):
    x, y = loc
    item_height,item_width,tq = item.shape
    pyautogui.moveTo(x+(item_width/2), y+(item_height/2),.5)
    pyautogui.mouseDown()
    time.sleep(.3)
    pyautogui.mouseUp()
    if randomReturn:
        #Randomize idle mouse returned position to not look like a robot
        pyautogui.moveTo(500+random.randint(0,700), 400, .5)

def progress(count, totalSeconds):
    width = 70
    completed = int(count * width / totalSeconds)
    display = '#' * completed + '_' * (width - completed)
    timeLeft = time.strftime("%M:%S", time.gmtime(totalSeconds-count))
    sys.stdout.write('[%s] %s minutes left\r' % (display, timeLeft))
    sys.stdout.flush()

def surrender():
    log("Trying to surrender")
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

def WaitForMatchEnd():
    log("Waiting for match to end")
    progress(0,secondsToWait)
    for x in range(secondsToWait):
        time.sleep(1)
        progress(x+1, secondsToWait)
    sys.stdout.write('\n')
    log("Done, but waiting a random 0-5 extra seconds to not be like a robot []-D")
    time.sleep(random.randint(0,5))

while True:
    time.sleep(1)
    screenshot = GrabScreenshot()

    if _stage == Stage.LauncherMenu:
        log("Looking for play button")
        _loc = LookFor(_img.playagain, screenshot)
        if _loc != None:
            Click(_loc, _img.playagain)
        else:
            _loc = LookFor(_img.matchsearch, screenshot)
            if _loc != None:
                Click(_loc, _img.matchsearch)
                _stage = Stage.InQueue
                log("Looking for a match")
        next

    if _stage == Stage.InQueue:
        _loc = LookFor(_img.matchfound, screenshot)
        if _loc != None:
            Click(_loc, _img.matchfound)
            log("Match accepted")
        else:
            _loc = LookFor(_img.loadingscreen, screenshot)
            if _loc != None:
                _stage = Stage.LoadingScreen
                log("On Loading Screen")
                startedLoading = time.time()
                time.sleep(60)
        next
    
    if _stage == Stage.LoadingScreen:
        _loc = LookFor(_img.gamestarted, screenshot)
        if _loc != None:
            Click(_loc, _img.gamestarted, False)
            _stage = Stage.GameStarted
            log("Game Started")
        else:
            if startedLoading != None and (time.time() - startedLoading) >= 300:
                log("5 Minutes has passed and still the game has not stared, something went wrong.")
                # WIP - check and kill League process and then login again.

    if _stage == Stage.GameStarted:
        WaitForMatchEnd()
        _stage = Stage.GameFinished
        next

    if _stage == Stage.GameFinished:
        surrender()
        stillInGame = True
        while stillInGame:
            time.sleep(1)
            screenshot = GrabScreenshot()
            _loc = LookFor(_img.surrender, screenshot)
            if _loc != None:
                Click(_loc, _img.surrender)
                log("Surrender button clicked, waiting 5 seconds to verify")
                time.sleep(5)
            else: 
                _loc = LookFor(_img.playagain, screenshot)
                if _loc != None:
                    stillInGame = False
                else:
                    _loc = LookFor(_img.matchsearch, screenshot)
                    if _loc != None:
                        stillInGame = False
                    else:
                        #So, there's no button? maybe the surrender wasn't triggered
                        surrender()
        matchesCount += 1
        log("Match done. Tokens farmed: " + str(matchesCount * 4) + ", for a total " + str(matchesCount) + " matches." )
        _stage = Stage.LauncherMenu