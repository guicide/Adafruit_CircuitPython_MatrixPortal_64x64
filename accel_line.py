# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
#
# Modified 2023-01-31 by guicide
# Works on 64x64 and 32x32 LED Matrices
# This example reads the accelerometer occasionally
# and draws a line from 32,32 to 32+x, 32+y

SIXTYFOUR = True  # set to False for 32x32
if SIXTYFOUR:
    SQUARE = 64
    CENTER = 32
    LIMIT = 2
else:
    SQUARE = 32
    CENTER = 16
    LIMIT = 1
COLORS = 4

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
# create the only bitmap this example needs
global b1
b1 = displayio.Bitmap(display.width, display.height, COLORS)
# create a palette with the same number of colors
palette = displayio.Palette(COLORS)
# create a TileGrid to tie the bitmap to the palette
tg1 = displayio.TileGrid(b1, pixel_shader=palette)
# create a Display Group
g1 = displayio.Group(scale=1)
# add the TileGrid to the Display Group
g1.append(tg1)
# "show" the bitmap on the display
display.show(g1)

# define a 4 color palette
palette[0] = 0x000000 # black
palette[1] = 0x00FF00 # green
palette[2] = 0xFF0000 # red
palette[3] = 0x0000FF # blue
display.auto_refresh = True

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_lsm303_accel.LSM303_Accel(i2c)

def xy(x, y, i):
    b1[(y * b1.height) + x] = i

def plot(f_x, f_y):
    # clear previous bits
    for x in range(0, b1.width, 1):
        for y in range(0, b1.height, 1):
            xy(x, y, 0)
    xy(CENTER, CENTER, 3) # mark center
    d = 0.2
    while (d <= LIMIT): # for d=0.2 to 2 step 0.1
        xy(int(CENTER + round(f_x * d, 0)), int(CENTER + round(f_y * d, 0)), 1)
        d += 0.1
    xy(int(CENTER + round(f_x * d, 0)), int(CENTER + round(f_y * d, 0)), 2)

lp = 0 # just an FYI counter

while True:
    lp += 1
    f_x, f_y, f_z = sensor.acceleration
    f_x = round(f_x, 3)
    f_y = round(f_y, 3)
    f_z = round(f_z, 3)
    print(lp, f_x, f_y, f_z)
    plot(f_x, f_y)
    time.sleep(0.25)
