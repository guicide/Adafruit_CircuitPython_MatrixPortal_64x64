# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import random
import time
import board
import displayio
import framebufferio
import rgbmatrix
from rtc import RTC

SIXTYFOUR = True
COLORS = 8

displayio.release_displays()

# Fill cells with random 0-7 values
def fillBitmap(bmb, prv):
    STEP = 1
    for x in range(0, bmb.width, STEP):
        for y in range(1, bmb.height, STEP):
            bmb[y * bmb.height + x] = prv[y * bmb.height + x - bmb.width]
        bmb[0 * bmb.height + x] = int(random.random() * COLORS)  # first row

# bit_depth=1 is used here because we only use primary colors, and it makes
# the animation run a bit faster because RGBMatrix isn't taking over the CPU
# as often.
if SIXTYFOUR:
    matrix = rgbmatrix.RGBMatrix(
        width=64, height=64, bit_depth=1,
        rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
                  board.MTX_R2, board.MTX_G2, board.MTX_B2],
        addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
                   board.MTX_ADDRD, board.MTX_ADDRE],
        clock_pin=board.MTX_CLK,
                    latch_pin=board.MTX_LAT,
                   output_enable_pin=board.MTX_OE)
else:
    matrix = rgbmatrix.RGBMatrix(
        width=32, height=32, bit_depth=1,
        rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
                  board.MTX_R2, board.MTX_G2, board.MTX_B2],
        addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
                   board.MTX_ADDRD],
        clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT,
                    output_enable_pin=board.MTX_OE)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

print("Display is ", display.width, "x", display.height)

b1 = displayio.Bitmap(display.width, display.height, COLORS)
b2 = displayio.Bitmap(display.width, display.height, COLORS)
palette = displayio.Palette(COLORS)
tg1 = displayio.TileGrid(b1, pixel_shader=palette)
tg2 = displayio.TileGrid(b2, pixel_shader=palette)
g1 = displayio.Group(scale=1)
g2 = displayio.Group(scale=1)
g1.append(tg1)
g2.append(tg2)

# First time, show the Conway tribute
palette[0] = 0x000000  # black
palette[1] = 0x800080  # magenta
palette[2] = 0x000080  # blue
palette[3] = 0x008080  # cyan
palette[4] = 0x008000  # green
palette[5] = 0x808000  # yellow
palette[6] = 0x804000  # orange
palette[7] = 0x800000  # red
display.auto_refresh = True
lp = 0

MAX_ITER = COLORS * 4

def mandelbrot(c):
    z = 0
    n = 0
    while abs(z) <= 2 and n < MAX_ITER:
        z = z*z + c
        n += 1
    return n

xWidth = 1.0
yWidth = 0.8
xStart = -1.255
yStart = -0.39

def mandy(bmp):
    global x, xWidth, y, yWidth
    for x in range(bmp.width):
        cx = xStart - (xWidth / 2) + (xWidth * x / 64)
        for y in range(bmp.height):
            cy = yStart - (yWidth / 2) + (yWidth * y / 64)
            if x == 0 and y == 0:
                print(cx, cy)
            c = complex(cx, cy)
            m = mandelbrot(c)
            bmp[y * bmp.height + x] = m % COLORS
    xWidth *= 0.99
    yWidth *= 0.99

while lp < 500:
    lp = lp + 1
    ts = RTC().datetime
    print("lp=", lp, ts.tm_sec)
    if lp & 1:
#        fillBitmap(b1, b2)  # build b1
        mandy(b1)  # build b1
        display.show(g1)  # and display it
    else:
#        fillBitmap(b2, b1)  # build b2
        mandy(b2)  # build b2
        display.show(g2)  # and display it
    time.sleep(0.1)

while True:
    pass


