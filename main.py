import cv2
import tkinter
##import win32api
##import win32con
#import pywintypes
import numpy as np
import easyocr
import keyboard
from PIL import ImageGrab
import re
import math
import os

screen_res = [1920, 1080]
windowed = True

reg_list = [(int(0.0625*screen_res[0]), int(0.398*screen_res[1]), int(0.5*screen_res[0]), int(0.43*screen_res[1])),
(int(0.32*screen_res[0]), int(0.463*screen_res[1]), int(0.5*screen_res[0]), int(0.5*screen_res[1]))]
#0=coords, 1=heading

display = []
text = ""
index = 0
temp = []

def register_data():
    global text
    global temp
    bboxxz = reg_list[0]
    bboxh = reg_list[1]
    temp = []

    lower_white = np.array([205, 205, 205], dtype=np.uint8)
    upper_white = np.array([255, 255, 255], dtype=np.uint8)

    xz = np.array(ImageGrab.grab(bbox=(bboxxz)))
    mask = cv2.inRange(xz, lower_white, upper_white)
    xz = cv2.bitwise_and(xz, xz, mask=mask)
    ##xz = cv2.cvtColor(xz, cv2.COLOR_RGB2BGR)
    ##xz = cv2.cvtColor(xz, cv2.COLOR_RGB2GRAY)
    try:
        coords = reader.readtext(xz)[0][1]
        coords = coords.split()
    except:
        heading = ["Try again"]

    angle = np.array(ImageGrab.grab(bbox=(bboxh)))
    mask = cv2.inRange(angle, lower_white, upper_white)
    angle = cv2.bitwise_and(angle, angle, mask=mask)
    ##angle = cv2.cvtColor(angle, cv2.COLOR_RGB2BGR)
    ##angle = cv2.cvtColor(angle, cv2.COLOR_RGB2GRAY)
    try:
        heading = reader.readtext(angle)[0][1]
    except:
        heading = ["Try again"]
    try:
        heading = [heading.split('(')[1].split('/')[0]]
    except:
        try:
            heading = [heading.split('(')[1]]
        except:
            try:
                heading = [heading.split('/')[0]]
            except:
                heading = [heading]
    heading[0] = heading[0].replace('.', '')
    if heading[0][0] == '_':
        heading[0] = '-' + heading[0][1:]
    print(heading)
    try:
        heading[0] = int(heading[0])/10
    except:
        heading = ["Try again"]
    
    try :
        coords = [int(coords[0]), int(coords[2].split('[')[0])]
    except:
        try:
            coords = [coords[0], coords[1].split('[')[0]]
            if int(coords[1][0]) < 3:
                coords[1] = int(coords[1][3:])
            else:
                coords[1] = int(coords[1][2:])
            coords[0] = int(coords[0])
        except:
            coords = ["Try again"]

    if index == 0:
        text = f'Coord1: {coords}, {heading}\nCoord2:'
    else:
        text = f'Coord1: {display[0]}, {display[1]}\nCoord2: {coords}, {heading}'
    temp = [coords, heading]
    update_label()

def set_data():
    global display
    global index
    global temp
    global text

    display += temp

    if index == 0:
        index = 1
    else:
        index = 0
        display[1][0] *= -1
        display[3][0] *= -1

        print(display)

        matrix = np.array([[math.sin(math.radians(display[1][0])), -1*math.sin(math.radians(display[3][0]))], 
        [math.cos(math.radians(display[1][0])), -1*math.cos(math.radians(display[3][0]))]])

        ans_matrix = np.array([display[2][0] - display[0][0], 
        display[2][1] - display[0][1]])

        sol = np.linalg.solve(matrix, ans_matrix)

        text = f'Coord1: {display[0]}, {display[1]}\nCoord2: {display[2]}, {display[3]}\nStronghold: {int(display[0][0] + sol[0]*math.sin(math.radians(display[1][0])))}, {int(display[0][1] + sol[0]*math.cos(math.radians(display[1][0])))}'
        print(text)
        update_label()

def clear_data():
    global display
    global text

    display = []
    text = ""
    update_label()

def update_label():
    global text
    label.config(text=text)

root = tkinter.Tk()
root.overrideredirect(True)
root.geometry("+1000+400")
root.lift()
root.attributes("-topmost", True)
root.attributes("-disabled", True)
root.attributes("-transparentcolor", "white")

label = tkinter.Label(root, text='', font=('Times New Roman', '24'), fg='yellow', bg='white')

##label = tkinter.Label(text='', font=('Times New Roman','24'), fg='yellow', bg='white')
##label.master.overrideredirect(True)
##label.master.geometry("+500+300")
##label.master.lift()
##label.master.wm_attributes("-topmost", True)
##label.master.wm_attributes("-disabled", True)
##label.master.wm_attributes("-transparentcolor", "white")

##mode_label = tkinter.Label(text=f"Mode: {modes[mode]}", font=('Times New Roman', '12'), fg='yellow', bg='white')
##mode_label.master.overrideredirect(True)
##mode_label.master.geometry("+500+300")
##mode_label.master.lift()
##mode_label.master.wm_attributes("-topmost", True)
##mode_label.master.wm_attributes("-disabled", True)
##mode_label.master.wm_attributes("-transparentcolor", "white")

##hWindow1 = pywintypes.HANDLE(int(label.master.frame(), 16))
##hWindow2 = pywintypes.HANDLE(int(mode_label.master.frame(), 16))
##exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
##win32api.SetWindowLong(hWindow1, win32con.GWL_EXSTYLE, exStyle)
##win32api.SetWindowLong(hWindow2, win32con.GWL_EXSTYLE, exStyle)

label.pack()

dirname = os.path.dirname(__file__)
reader = easyocr.Reader(lang_list=['en'], download_enabled=False, model_storage_directory=dirname)

keyboard.add_hotkey('[', register_data)
keyboard.add_hotkey(']', set_data)
keyboard.add_hotkey('|', clear_data)
root.mainloop() #loop
