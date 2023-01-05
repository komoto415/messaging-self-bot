
import subprocess
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
import time
import pyperclip
import json
import re
import urllib

APP_VERSION = "app-1.0.9008"
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
ID_TO_READABLE = dict()
NUM_OPEN_DMS = 12

template_locations = dict()

with open("id_to_readable.json", "r") as json_f:
    ID_TO_READABLE = json.load(json_f)

def get_template_result(template, region_w, region_h):
    x = y = 0

    # Capture an image of the region of interest on the screen
    screenshot = np.array(ImageGrab.grab(bbox=(x, y, x + region_w, y + region_h)))

    # Convert the images to grayscale
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # cv2.imwrite('template_gray.png', template_gray)
    # cv2.imwrite('screenshot_gray.png', screenshot_gray)

    # Apply template matching
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    return result

def get_template_result_coordinates(template, result):
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    template_h, template_w = template.shape[:2]
    top_left = max_loc

    return template_h, template_w, top_left

def draw_bounding_box(image, template_h, template_w, top_left):
    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
    cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), 2)

    # Show the result
    cv2.imshow('Result', image)
    cv2.waitKey(0)

def start_up():
    # Set the path to the Discord executable
    path = f'C:\\Users\\Jeffrey\\AppData\\Local\\Discord\\{APP_VERSION}\\Discord.exe'

    # Launch Discord
    subprocess.run([path])

    # Do some zeroing out just so we can get a more consistent state after focusing the window
    # Calculate the coordinates of the center of the screen
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    # Move the mouse to the center of the screen
    pyautogui.moveTo(x, y, duration=0.1)
    # Maximize the window
    pyautogui.hotkey('winleft', 'up')

    pyautogui.hotkey('ctrl', '0')
    time.sleep(.3)
    pyautogui.hotkey('ctrl', '=')
    pyautogui.hotkey('ctrl', '=')
    pyautogui.hotkey('ctrl', '=')

def calculate_locations(template_h, template_w, top_left):
    x = top_left[0] + template_w
    y = top_left[1] + template_h
    return x, y

def get_to_smiley():
    try:
        icon_center_x, icon_center_y = template_locations["smiley"]
    except KeyError as _:
        # Load the reference image of the icon
        template = cv2.imread('templates\\smiley_server_template.png')

        # values for 1920x1080 where the discord app is zoomed in 3x
        region_w = SCREEN_WIDTH / 16
        region_h = SCREEN_HEIGHT / 4

        result = get_template_result(template, region_w, region_h)
        template_h, template_w, top_left = get_template_result_coordinates(template, result)

        icon_center_x, icon_center_y = calculate_locations(template_h / 2, template_w / 2, top_left)
        template_locations["smiley"] = (icon_center_x, icon_center_y)

    pyautogui.moveTo(icon_center_x, icon_center_y, duration=0.1)
    pyautogui.click()

def get_to_dms():
    get_to_smiley()
    try:
        icon_center_x, icon_center_y = template_locations["dms"]
    except KeyError as _:
        # Load the reference image of the icon
        template = cv2.imread('templates\\discord_icon.jpg')

        # values for 1920x1080 where the discord app is zoomed in 3x
        region_w = SCREEN_WIDTH / 16
        region_h = SCREEN_HEIGHT / 8

        # need to resize to account for larger template than screenshot
        resize_size = int(min(region_h, region_w))
        template = cv2.resize(template, (resize_size, resize_size))

        result = get_template_result(template, region_w, region_h)
        template_h, template_w, top_left = get_template_result_coordinates(template, result)

        icon_center_x, icon_center_y = calculate_locations(template_h / 2, template_w / 2, top_left)
        template_locations["dms"] = (icon_center_x, icon_center_y)

    pyautogui.moveTo(icon_center_x, icon_center_y, duration=0.1)
    pyautogui.click()

def get_to_friends_tab():
    try:
        friends_tab_x, friends_tab_y = template_locations["friends_tab"]
    except KeyError as _:
        template = cv2.imread('templates\\friends_tab_template.png')

        # values for 1920x1080 where the discord app is zoomed in 3x
        region_w = SCREEN_WIDTH / 4
        region_h = SCREEN_HEIGHT / 4

        result = get_template_result(template, region_w, region_h)
        template_h, template_w, top_left = get_template_result_coordinates(template, result)

        friends_tab_x, friends_tab_y = calculate_locations(template_h / 3, template_w / 32, top_left)
        template_locations["friends_tab"] = (friends_tab_x, friends_tab_y)

    pyautogui.moveTo(friends_tab_x, friends_tab_y, duration=0.1)
    pyautogui.click()

def get_dm_header_coordinates():
    try:
        header_x, header_y = template_locations["dm_header"]
    except KeyError as _:
        template = cv2.imread('templates\\dm_header_template.png')

        # values for 1920x1080 where the discord app is zoomed in 3x
        region_w = SCREEN_WIDTH / 2
        region_h = SCREEN_HEIGHT / 12

        result = get_template_result(template, region_w, region_h)
        template_h, template_w, top_left = get_template_result_coordinates(template, result)

        header_x, header_y = calculate_locations(template_h / 1.8, template_w / 2, top_left)
        template_locations["dm_header"] = (header_x, header_y)

    return header_x, header_y

def check_if_still_friends():
    ...

def store_in_clipboard_paste_enter(string):
    pyperclip.copy(string)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')

def send_messages(header_x, header_y):
    over_name_x = header_x + 35
    pyautogui.hotkey('alt', 'down')
    group_dms_visited = set()
    dms_visited = set()
    while len(group_dms_visited) + len(dms_visited) < NUM_OPEN_DMS and len(ID_TO_READABLE) > 0:
        pyautogui.hotkey('alt', 'down')
        time.sleep(0.4)
        pyautogui.moveTo(header_x - 50, header_y, duration=0.1)

        template = cv2.imread('templates\\dm_icon_template.png')

        # values for 1920x1080 where the discord app is zoomed in 3x
        region_w = SCREEN_WIDTH / 3
        region_h = SCREEN_HEIGHT / 10

        result = get_template_result(template, region_w, region_h)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        threshold = 0.8
        pyautogui.click()
        pyautogui.moveTo(over_name_x, header_y, duration=0.1)

        if max_val < threshold:
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')
            pyautogui.press('enter')
            group_dm_name = pyperclip.paste()
            # if not group_dm_name in group_dms_visited:
            group_dms_visited.add(group_dm_name)
            continue

        # open the drop down the menu and copy user ID
        pyautogui.rightClick()
        pyautogui.press('up')
        pyautogui.press('enter')
        user_id = pyperclip.paste()
        time.sleep(1)
        if user_id in ID_TO_READABLE and not user_id in dms_visited:
            # leave and re-enter chat so that message box is focused
            pyautogui.hotkey('alt', 'up')
            time.sleep(0.3)
            pyautogui.hotkey('alt', 'down')
            with open(f".\\messages\\{ID_TO_READABLE[user_id]}@{user_id}\\message.txt", 'r') as message_file:
                lines = message_file.readlines()
                for line in lines:
                    time.sleep(0.5)
                    line = line.strip()
                    if line.startswith('@'):
                        # do file stuff
                        ...
                    else:
                        blocks = re.split(r'(https?://[^\s]+)|\s+', line)
                        clean_blocks = [block for block in blocks if block != '' and block is not None]
                        message = ""
                        for block in clean_blocks:
                            try:
                                result = urllib.parse.urlparse(block)

                                # Check if the parsed URL can be reconstructed as the original string
                                if result.scheme in urllib.parse.uses_netloc and result.netloc:
                                    # If the URL can be reconstructed, the string is a URL
                                    store_in_clipboard_paste_enter(message)
                                    store_in_clipboard_paste_enter(block)
                                    message = ''
                                    continue
                            except ValueError:
                                ...
                            if len(block) + len(message) > 4000:  # change to 2000 if i no longer have nitro
                                store_in_clipboard_paste_enter(message)
                                message = ''

                            message += block + ' '
                        store_in_clipboard_paste_enter(message)
            del ID_TO_READABLE[user_id]
        dms_visited.add(user_id)
    print(len(dms_visited) + len(group_dms_visited))

if __name__ == '__main__':
    start_up()
    # get_to_dms()
    # time.sleep(0.5)
    # get_to_friends_tab()
    # time.sleep(0.5)
    # header_x, header_y = get_dm_header_coordinates()
    # time.sleep(0.5)
    # send_messages(header_x, header_y)