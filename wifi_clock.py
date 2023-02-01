# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
#
# Modified 2023-01-31 by guicide
# Works on 64x64 and 32x32 LED Matrices
# This example connects to your WiFi via your secrets.py file
# If the RTC thinks it is the year 2000, we get the time from
# worldtimeapi.org and reset the RTC.
# Then, once a second, the time from the RTC is updated on the display

SIXTYFOUR = True  # set to False for 32x32

import board
import busio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_display_text.label
import displayio
import framebufferio
import rgbmatrix
import terminalio
import time
import json
from rtc import RTC

# If there was a display before (protomatter, LCD, or E-paper), release it so
# we can create ours
displayio.release_displays()
g = displayio.Group()

# create an element to put the updated time into
CLOCK_TEXT = adafruit_display_text.label.Label(
            terminalio.FONT, color=0x008080, text="00:00:00")
CLOCK_TEXT.x = 8
CLOCK_TEXT.y = 55
g.append(CLOCK_TEXT)

def text_out(TxtRow, txt):
    CYAN_TEXT = adafruit_display_text.label.Label(
        terminalio.FONT,
        color=0x008080,
        text=txt)
    CYAN_TEXT.x = 3
    CYAN_TEXT.y = 3 + ((TxtRow - 1) * 10)
    # Put each line of text into a Group, then show that group.
    g.append(CYAN_TEXT)
    display.show(g)
    display.refresh(minimum_frames_per_second=0)
    display.auto_refresh = True

def clock_out(h, m, s):
    if SIXTYFOUR:
        # change the text color every second using the folowing 7 colors
        colors = [0x800000, 0x008000, 0x000080, 0x808000,
                  0x800080, 0x008080, 0x808080]
        CLOCK_TEXT.text = twoDigits(h) + ":" + twoDigits(m) + ":" + twoDigits(s)
        CLOCK_TEXT.color = colors[s % 7]
    else:
        CYAN_TEXT = adafruit_display_text.label.Label(
            terminalio.FONT, color=0x008080, text=twoDigits(h) )
        CYAN_TEXT.x = 8
        CYAN_TEXT.y = 6
        g.append(CYAN_TEXT)
        MAGENTA_TEXT = adafruit_display_text.label.Label(
            terminalio.FONT, color=0x800080, text=twoDigits(m))
        MAGENTA_TEXT.x = 8
        MAGENTA_TEXT.y = 16
        g.append(MAGENTA_TEXT)
        YELLOW_TEXT = adafruit_display_text.label.Label(
            terminalio.FONT, color=0x808000, text=twoDigits(s))
        YELLOW_TEXT.x = 8
        YELLOW_TEXT.y = 26
        g.append(YELLOW_TEXT)
    display.show(g)
    display.refresh(minimum_frames_per_second=0)
    display.auto_refresh = True

def twoDigits(n):
    d2 = n % 10
    d1 = int(n / 10)
    return str(d1) + str(d2)

def parse_time(timestring, is_dst=-1):
    """ Given a string of the format YYYY-MM-DDTHH:MM:SS.SS-HH:MM (and
        optionally a DST flag), convert to and return an equivalent
        time.struct_time (strptime() isn't available here). Calling function
        can use time.mktime() on result if epoch seconds is needed instead.
        Time string is assumed local time; UTC offset is ignored. If seconds
        value includes a decimal fraction it's ignored.
    """
    date_time = timestring.split('T')         # Separate into date and time
    year_month_day = date_time[0].split('-')  # Separate time into Y/M/D
    hour_minute_second = date_time[1].split('+')[0].split('-')[0].split(':')

    print(year_month_day[0], year_month_day[1], year_month_day[2])
    print(hour_minute_second[0], hour_minute_second[1], hour_minute_second[2])
    return time.struct_time((int(year_month_day[0]),
                            int(year_month_day[1]),
                            int(year_month_day[2]),
                            int(hour_minute_second[0]),
                            int(hour_minute_second[1]),
                            int(hour_minute_second[2].split('.')[0]),
                            -1, -1, is_dst))

def start_clock(tStr):
    ts = RTC().datetime
    print("time was ", ts)

    if tStr != "":
        time_struct = parse_time(tStr)
        RTC().datetime = time_struct

        ts = RTC().datetime
        print("time is  ", ts)

    print("Fine so far!")
    lp = 0
    hh_mm_ss = "WTF"

    while True:
        lp += 1
        ts = RTC().datetime
        hh_mm_ss = twoDigits(ts.tm_hour) + ":" + twoDigits(ts.tm_min) + ":" + twoDigits(ts.tm_sec)
        if (lp < 5) or (ts.tm_sec == 0): # when the minute changes, print some info
            print(hh_mm_ss)
            print(RTC().datetime)
        clock_out(ts.tm_hour, ts.tm_min, ts.tm_sec)
        time.sleep(1)
        pass
    return

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("ESP32 SPI webclient test")

TIME_URL = "http://worldtimeapi.org/api/ip"

# This next call creates the RGB Matrix object itself. It has the given width
# and height. bit_depth can range from 1 to 6; higher numbers allow more color
# shades to be displayed, but increase memory usage and slow down your Python
# code. If you just want to show primary colors plus black and white, use 1.
# Otherwise, try 3, 4 and 5 to see which effect you like best.
#
# These lines are for the MatrixPortal M4. If you're using a different board,
# check the guide to find the pins and wiring diagrams for your board.
# If you have a matrix with a different width or height, change that too.
# If you have a 16x32 display, try with just a single line of text.
if SIXTYFOUR:
    matrix = rgbmatrix.RGBMatrix(
        width=64, height=64, bit_depth=1,
        rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
                  board.MTX_R2, board.MTX_G2, board.MTX_B2],
        addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
                   board.MTX_ADDRD, board.MTX_ADDRE],
        clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE)
else:
    matrix = rgbmatrix.RGBMatrix(
        width=32, height=32, bit_depth=1,
        rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
                  board.MTX_R2, board.MTX_G2, board.MTX_B2],
        addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
                   board.MTX_ADDRD],
        clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE)

# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

print("Display is ", display.width, "x", display.height)

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
# print("Firmware vers.", esp.firmware_version)
# print("MAC addr:", [hex(i) for i in esp.MAC_address])

# for ap in esp.scan_networks():
#     print("\t%s\t\tRSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))

text_out(1, "Setup   Y")

text_out(2, "Wifi...")
print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except OSError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))
print(
    "IP lookup adafruit.com: %s" % esp.pretty_ip(esp.get_host_by_name("adafruit.com"))
)
print("Ping google.com: %d ms" % esp.ping("google.com"))
text_out(2, "Wifi    Y")

text_out(3, "RTC...")
ts = RTC().datetime
print("RTC says:", ts)

if ts.tm_year == 2000: # RTC has not been set
    # reload time from internet
    text_out(3, "Text...")
    print("Fetching text from", TIME_URL)
    r = requests.get(TIME_URL)
    print("-" * 40)
    TimeStr = r.text
    print(TimeStr)
    print("-" * 40)
    r.close()
    print("TEXT test is happy!")

    TimeList = json.loads(TimeStr)
    print(TimeList["datetime"])  # i.e. 2023-01-19T15:49:23.970617-07:00
    start_clock(TimeList["datetime"])
text_out(3, "RTC     Y")

start_clock("")  # resume from current remembered time, NEVER returns

while True: # we should never get here
    pass
