import time
import pyautogui
from tkinter import Tk
import cv2
import numpy as np
import win32api
import win32gui
from PIL import ImageGrab


def get_fishing_size():
    root = Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    lx = (1450 / 1920) * screen_width
    ly = (650 / 1080) * screen_height
    rx = (1670 / 1920) * screen_width
    ry = (870 / 1080) * screen_height
    root.destroy()
    return lx, ly, rx, ry


def get_window_pos(name):
    name = name
    handle = win32gui.FindWindow(None, name)
    # 獲取視窗控制程式碼
    if handle == 0:
        return None
    else:
        # 返回座標值和handle
        return win32gui.GetWindowRect(handle), handle


def compare_image_green(image1, image2):
    h1 = cv2.calcHist([image1], [1], None, [246], [10, 256])
    h2 = cv2.calcHist([image2], [1], None, [246], [10, 256])
    h1 = cv2.normalize(h1, h1, 0, 1, cv2.NORM_MINMAX, -1)
    h2 = cv2.normalize(h2, h2, 0, 1, cv2.NORM_MINMAX, -1)
    similarity = cv2.compareHist(h1, h2, 0)
    return similarity


def compare_image_gray(image1, image2):
    h1 = cv2.calcHist([image1], [0], None, [256], [0, 255])
    h2 = cv2.calcHist([image2], [0], None, [256], [0, 255])
    h1 = cv2.normalize(h1, h1, 0, 1, cv2.NORM_MINMAX, -1)
    h2 = cv2.normalize(h2, h2, 0, 1, cv2.NORM_MINMAX, -1)
    similarity = cv2.compareHist(h1, h2, 0)
    return similarity


def thresh_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
    return thresh


def circle_image(image_in):
    img = cv2.cvtColor(image_in, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        mask = np.zeros(img.shape, dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)

    image_out = cv2.bitwise_and(image_in, image_in, mask=mask)
    return image_out, mask


# initialization
print("INITIALIZATION")
print("License by Nick Yang")
print("To STOP program, click RIGHT MOUSE BOTTOM")
times = 0
fish_start = cv2.imread("fish_start.png")
fish_start_thresh = thresh_image(fish_start)
fish_get = cv2.imread("fish_get.png")
fish_get_circle, fish_get_circle_mask = circle_image(fish_get)
end_times = input("Please key-in your fishing Times: ")
print("Your fishing times:", end_times)
print("Please switch to your simulator manually")
end_times = int(end_times)
LX, LY, RX, RY = get_fishing_size()
time_counts = 0
stage = 0
right_click = 0
while times < end_times:
    try:
        # (x1, y1, x2, y2), handle = get_window_pos("夜神模擬器")
        # win32gui.SetForegroundWindow(handle)
        grb = ImageGrab.grab().crop((LX, LY, RX, RY)).convert("RGB")
        image = np.array(grb)
        image_circle = cv2.bitwise_and(image, image, mask=fish_get_circle_mask)
        image_thresh = thresh_image(image)
        value = cv2.matchShapes(fish_start_thresh, image_thresh, 1, 0)
        noise_x = np.random.normal(0, 10, 1)
        noise_y = np.random.normal(0, 10, 1)
        # cv2.imshow("1", image_thresh)
        # cv2.imshow("2", fish_start_thresh)
        # cv2.waitKey()
        # print("start: ", value)
        if (value <= 0.01) & (stage == 0):
            pyautogui.leftClick(x=(LX + RX)/2 + noise_x, y=(LY + RY)/2 + noise_y, duration=0.20)
            print("Start FISHING")
            stage = 1
            time.sleep(0.5)

        value_green = compare_image_green(image_circle, fish_get_circle)
        # print("Similarity (for debug):", value_green)
        if (value_green >= 0.85) & (stage == 1):
            pyautogui.leftClick(x=(LX + RX)/2 + noise_x, y=(LY + RY)/2 + noise_y, duration=0.05)
            print("Get FISH")
            stage = 0
            times = times + 1
            print("Fishing times:", times)
            time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)

    # processing time
    time.sleep(0.1)
    time_counts = time_counts + 1
    # end process
    right_click = win32api.GetKeyState(0x02)
    if (right_click == 1) & (time_counts > 10):
        print("END PROGRAM")
        break
