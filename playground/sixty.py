import board
from adafruit_seesaw import seesaw, rotaryio
from adafruit_seesaw import digitalio as seesawio
import wifi
import socketpool
import os
import digitalio
import neopixel
import displayio
from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import bitmap_label,  wrap_text_to_lines
from adafruit_debouncer import Debouncer
import terminalio
import time
import adafruit_requests
import ssl
import ElementTree as ET


# Set up Receiver
HOST = "192.168.1.119"
PORT = 23

buffer = bytearray(1024)

# Setup wifi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

# Make the display context
avr = displayio.Group()
board.DISPLAY.show(avr)

# set progress bar width and height relative to board's display
width = 183
height = 30

x = 28
#y = board.DISPLAY.height // 3
y = 100

# Create a new progress_bar object at (x, y)
progress_bar = HorizontalProgressBar(
    (x, y),
    (width, height),
    fill_color=0x000000,
    outline_color=0xFFFFFF,
    bar_color=0x0000ff,
    direction=HorizontalFillDirection.LEFT_TO_RIGHT
)

# Append progress_bar to the avr group
avr.append(progress_bar)

def receiver_connect():
    # Connect to the receiver
    try:
        pool = socketpool.SocketPool(wifi.radio)
        s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        s.connect((HOST, PORT))
    except OSError:
        pool = socketpool.SocketPool(wifi.radio)
        s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        s.connect((HOST, PORT))
    print("Connected!")

try:
    pool = socketpool.SocketPool(wifi.radio)
    s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    s.connect((HOST, PORT))
except OSError:
    pool = socketpool.SocketPool(wifi.radio)
    s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    s.connect((HOST, PORT))
print("Connected!")

url = "http://192.168.1.119:8080/goform/AppCommand.xml"

xml_vol_body = '''
    <?xml version="1.0" encoding="utf-8"?>
    <tx>
        <cmd id="1">GetAllZoneVolume</cmd>
    </tx>'''

requests = adafruit_requests.Session(pool, ssl.create_default_context())

vol_request = requests.post(url, data=xml_vol_body)
# print(r.text)

vol_root = ET.fromstring(vol_request.text)
# print("Root Type: ", type(root), root)
# print("Root tag: ", root.tag)

vol_request.close()

xml_vol = vol_root[0][1][4].text
vol = int(xml_vol)
progress_bar.value = vol

vol_label = bitmap_label.Label(terminalio.FONT, text="Volume: ", scale=2, x=28, y=65)
avr.append(vol_label)
vol_text = bitmap_label.Label(terminalio.FONT, text=str(vol), scale=2, x=120, y=65)
avr.append(vol_text)

xml_source_body = '''
    <?xml version="1.0" encoding="utf-8"?>
    <tx>
        <cmd id="1">GetAllZoneSource</cmd>
    </tx>'''

source_request = requests.post(url, data=xml_source_body)

source_root = ET.fromstring(source_request.text)
source_request.close()

xml_source = source_root[0][1][0].text
if xml_source is "CD":
    display_source = "Vinyl"
elif xml_source is "TUNER":
    display_source = "Tuner"
else:
    display_source = "CD"

# Add input and volume labels and data to display
input_label = bitmap_label.Label(terminalio.FONT, text="Input: ", scale=2, x=28, y=25)
avr.append(input_label)
input_text = bitmap_label.Label(terminalio.FONT, text=display_source, scale=2, x=110, y=25)
avr.append(input_text)

while True:

    time.sleep(30)
    vol_request = requests.post(url, data=xml_vol_body)
    # print(r.text)

    vol_root = ET.fromstring(vol_request.text)
    # print("Root Type: ", type(root), root)
    # print("Root tag: ", root.tag)

    vol_request.close()

    xml_vol = vol_root[0][1][4].text
    vol = int(xml_vol)
    progress_bar.value = vol

    print("Updating volume...")
    avr[2].text = xml_vol

    time.sleep(30)
    source_request = requests.post(url, data=xml_source_body)
    source_root = ET.fromstring(source_request.text)
    source_request.close()

    xml_source = source_root[0][1][0].text

    if xml_source == "CD":
        display_source = "Vinyl"
    elif xml_source == "TUNER":
        display_source = "Tuner"
    else:
        display_source = "CD"

    print("Updating source: ", xml_source)
    avr[4].text = display_source