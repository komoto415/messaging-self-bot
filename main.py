import cv2
import numpy as np
from PIL import ImageGrab
import subprocess
import os
import shutil
import time
import pyautogui
import pyperclip
import urllib
import json
import re
import keyboard

DISCORD_APP_VERSION = "app-1.0.9008"
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
NUM_OPEN_DMS = 3
# NUM_OPEN_DMS = 32
template_locations = dict()
DEFAULT_REGION_W = SCREEN_WIDTH / 3
DEFAULT_REGION_H = SCREEN_HEIGHT / 6

# Define the callback function for the hotkey
def stop_program():
    # Set a flag to stop the program
    keyboard.unhook_all()
    print("program should now stop")
    os._exit(0)

# Register the hotkey 'Ctrl+Alt+Q' with the callback function
keyboard.add_hotkey('ctrl+alt+q', stop_program)

with open("id_to_readable.json", "r") as json_f:
    ID_TO_READABLE = json.load(json_f)

def calculate_template_center_x_y(template_h, template_w, top_left):
    x = top_left[0] + (template_w / 2)
    y = top_left[1] + (template_h / 2)
    return x, y

def resize_template(template, region_w=DEFAULT_REGION_W, region_h=DEFAULT_REGION_H):
    template_h, template_w, _ = template.shape
    template_aspect_ratio = template_w / template_h
    while template_w > region_w or template_h > region_h:
        if template_w > region_w:
            template_w = region_w
            template_h = int(template_w / template_aspect_ratio)
        if template_h > region_h:
            template_h = region_h
            template_w = int(template_h * template_aspect_ratio)

    return cv2.resize(template, (int(template_w), int(template_h)))

def get_template_result(template, region_w=DEFAULT_REGION_W, region_h=DEFAULT_REGION_H):
    template_h, template_w, _ = template.shape
    if template_w > region_w or template_h > region_h:
        print('needs resizing')
        template = resize_template(template, region_w, region_h)
    screenshot = np.array(ImageGrab.grab(bbox=(0, 0, region_w, region_h)))

    # Convert the images to grayscale
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    cv2.imwrite('template_gray.png', template_gray)
    cv2.imwrite('screenshot_gray.png', screenshot_gray)

    # Apply template matching
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    return result

def get_template_result_coordinates(template, result):
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    template_h, template_w, _ = template.shape
    top_left = max_loc

    return template_h, template_w, top_left

def get_template_result_location(template, region_w=DEFAULT_REGION_W, region_h=DEFAULT_REGION_H):
    template_h, template_w, _ = template.shape
    if template_w > region_w or template_h > region_h:
        print('needs resizing')
        template = resize_template(template, region_w, region_h)
        template_h, template_w, _ = template.shape

    result = get_template_result(template, region_w, region_h)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc

    # draw_bounding_box(cv2.imread('screenshot_gray.png'), template_h, template_w, top_left)

    return calculate_template_center_x_y(template_h, template_w, top_left)

def draw_bounding_box(image, template_h, template_w, top_left):
    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
    cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), 2)

    # Show the result
    cv2.imshow('Result', image)
    cv2.waitKey(0)

def focus_discord():
    # Set the path to the Discord executable
    path = f'C:\\Users\\Jeffrey\\AppData\\Local\\Discord\\{DISCORD_APP_VERSION}\\Discord.exe'

    # Launch Discord
    subprocess.run([path])

def dm_up_dm_down():
    pyautogui.hotkey('alt', 'up')
    time.sleep(0.3)
    pyautogui.hotkey('alt', 'down')

def store_in_clipboard_paste_enter(string):
    pyperclip.copy(string)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')

def start_up():
    focus_discord()
    # Do some zeroing out just so we can get a more consistent state after focusing the window
    # Calculate the coordinates of the center of the screen
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    # Move the mouse to the center of the screen
    pyautogui.moveTo(x, y, duration=0.1)
    # Maximize the window
    pyautogui.hotkey('winleft', 'up')

    # fix window zoom to 3x
    pyautogui.hotkey('ctrl', '0')
    time.sleep(.3)
    pyautogui.hotkey('ctrl', '=')
    pyautogui.hotkey('ctrl', '=')
    pyautogui.hotkey('ctrl', '=')

def get_to_dms():
    try:
        icon_center_x, icon_center_y = template_locations["dms"]
    except KeyError as _:
        # Load the reference image of the icon
        template = cv2.imread('templates\\dms.png')
        icon_center_x, icon_center_y = get_template_result_location(template)
        template_locations["dms"] = (icon_center_x, icon_center_y)

    pyautogui.moveTo(icon_center_x, icon_center_y, duration=0.1)
    pyautogui.click()
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'alt', 'up')
    pyautogui.hotkey('ctrl', 'alt', 'down')

def get_to_friends_tab():
    get_to_dms()
    time.sleep(0.2)
    try:
        friends_tab_x, friends_tab_y = template_locations['friends_tab']
    except KeyError as _:
        template = cv2.imread('templates\\friends_tab.png')
        friends_tab_x, friends_tab_y = get_template_result_location(template)
        template_locations['friends_tab'] = (friends_tab_x, friends_tab_y)

    pyautogui.moveTo(friends_tab_x, friends_tab_y, duration=0.1)
    pyautogui.click()

def get_to_header():
    try:
        header_x, header_y = template_locations['header']
    except KeyError as _:
        template = cv2.imread('templates\\friends_header.png')
        header_x, header_y = get_template_result_location(template)
        template_locations['header'] = (header_x, header_y)

    pyautogui.moveTo(header_x, header_y, duration=0.1)

def get_num_open_dms():
    global NUM_OPEN_DMS
    # pyautogui.hotkey('ctrl', 'shift', 'i')
    # get_dms_js = "document.getE lementsByTagName('ul')[1].getElementsByTagName('li')[0].getAttribute('aria-setsize')"
    # time.sleep(6)
    # store_in_clipboard_paste_enter(get_dms_js)
    # pyautogui.hotkey('shift', 'tab')
    # time.sleep(0.4)
    # pyautogui.hotkey('ctrl', 'c')
    # pyautogui.hotkey('ctrl', 'shift', 'i')
    # NUM_OPEN_DMS = int(pyperclip.paste()) - 4
    # print(NUM_OPEN_DMS)

    friends_tab = False
    pyautogui.hotkey('alt', 'down')
    dms_seen = 0

    time.sleep(0.1)
    while not friends_tab:
        pyautogui.hotkey('alt', 'down')
        time.sleep(0.3)
        template = cv2.imread('templates\\friends_header.png')
        result = get_template_result(template)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        friends_tab = max_val >= 0.9
        if not friends_tab:
            dms_seen += 1

    NUM_OPEN_DMS = dms_seen
    print(NUM_OPEN_DMS)

def check_if_still_friends():
    ...

def send_messages():
    template = cv2.imread('templates\\dm_icon.png')
    header_x, header_y = template_locations["header"]
    # values for 1920x1080 where the discord app is zoomed in 3x
    region_w = SCREEN_WIDTH / 3
    region_h = SCREEN_HEIGHT / 10
    pyautogui.hotkey('alt', 'down')
    pyautogui.hotkey('alt', 'down')
    pyautogui.moveTo(header_x, header_y, duration=0.1)

    group_dms_visited = set()
    dms_visited = set()
    while len(group_dms_visited) + len(dms_visited) < NUM_OPEN_DMS and len(ID_TO_READABLE) > 0:
        time.sleep(0.8)
        result = get_template_result(template)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        threshold = 0.9

        if max_val < threshold:
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')
            pyautogui.press('enter')
            group_dm_name = pyperclip.paste()
            group_dms_visited.add(group_dm_name)
            pyautogui.hotkey('alt', 'down')
            continue

        # open the drop down the menu and copy user ID
        pyautogui.rightClick()
        pyautogui.press('up')
        pyautogui.press('enter')
        user_id = pyperclip.paste()
        time.sleep(.5)
        if user_id in ID_TO_READABLE and not user_id in dms_visited:
            # leave and re-enter chat so that message box is focused
            dm_up_dm_down()
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('del')

            recipient_message_dir = f".\\messages\\{ID_TO_READABLE[user_id]}@{user_id}"
            try:
                with open(f"{recipient_message_dir}\\message.txt", 'r') as message_file:
                    lines = message_file.readlines()
                    for line in lines:
                        time.sleep(0.5)
                        line = line.strip()
                        if line.startswith('@'):
                            file_name = line[1:]
                            if not os.path.exists(file_path := f'{recipient_message_dir}\\{file_name}'):
                                print('file not found')
                                continue

                            # files = os.listdir(recipient_message_dir)
                            subprocess.run(['explorer', recipient_message_dir])
                            time.sleep(2)

                            file_found = False
                            while not file_found:
                                pyautogui.press('down')
                                pyautogui.press('F2')
                                pyautogui.hotkey('ctrl', 'a')
                                pyautogui.hotkey('ctrl', 'c')
                                pyautogui.hotkey('enter')
                                curr_file_name = pyperclip.paste()
                                file_found = curr_file_name == file_name

                                if file_found:
                                    # print(curr_file_name)
                                    time.sleep(0.2)
                                    pyautogui.hotkey('ctrl', 'c')
                                    pyautogui.hotkey('ctrl', 'w')
                                    focus_discord()
                                    dm_up_dm_down()
                                    time.sleep(0.3)
                                    pyautogui.hotkey('ctrl', 'v')
                                    pyautogui.press('enter')

                                    shutil.move(file_path, f"{recipient_message_dir}\\sent_files\\{file_name}")

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
                print(f'SENT MESSAGE TO {ID_TO_READABLE[user_id]}')
            except FileNotFoundError:
                print('NO MESSAGE FILE SET')
                print(f'MESSAGE WAS NOT SENT {ID_TO_READABLE[user_id]}')
            del ID_TO_READABLE[user_id]
            for _ in range(len(dms_visited) + len(group_dms_visited)):
                pyautogui.hotkey('alt', 'down')
        dms_visited.add(user_id)
        pyautogui.hotkey('alt', 'down')

    print(len(dms_visited) + len(group_dms_visited))

if __name__ == '__main__':
    start_up()
    get_to_friends_tab()
    time.sleep(0.2)
    get_to_header()

    time.sleep(0.2)
    print(t_0 := time.time())
    get_num_open_dms()
    print(t_1 := time.time())
    print(t_1 - t_0)
    # time.sleep(0.2)
    # send_messages()
