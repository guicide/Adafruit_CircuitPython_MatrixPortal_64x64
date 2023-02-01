# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
#
# Modified 2023-01-31 by guicide
# Works on 64x64 and 32x32 LED Matrices
# This example reads the accelerometer one a second
# and displays the x, y, z coords

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
import adafruit_lsm303_accel

# If there was a display before (protomatter, LCD, or E-paper), release it so
# we can create ours
displayio.release_displays()
g = displayio.Group()

TEXT1 = adafruit_display_text.label.Label(terminalio.FONT, color=0x008080, text="")
TEXT1.x = 3
TEXT1.y = 3
g.append(TEXT1)

TEXT2 = adafruit_display_text.label.Label(terminalio.FONT, color=0x808000, text="")
TEXT2.x = 3
TEXT2.y = 13
g.append(TEXT2)

TEXT3 = adafruit_display_text.label.Label(terminalio.FONT, color=0x800080, text="")
TEXT3.x = 3
TEXT3.y = 23
g.append(TEXT3)

TEXT4 = adafruit_display_text.label.Label(terminalio.FONT, color=0x008000, text="")
TEXT4.x = 3
TEXT4.y = 33
g.append(TEXT4)

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
display.show(g)
display.refresh(minimum_frames_per_second=0)
display.auto_refresh = True

TEXT1.text = "Sensor..."
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_lsm303_accel.LSM303_Accel(i2c)
TEXT1.text = "Sensor  Y"

while True:
    f_x, f_y, f_z = sensor.acceleration
    f_x = round(f_x, 3)
    f_y = round(f_y, 3)
    f_z = round(f_z, 3)
    print(f_x, f_y, f_z)
    TEXT2.text = str(f_x)
    TEXT3.text = str(f_y)
    TEXT4.text = str(f_z)
    time.sleep(1) # pause a second
