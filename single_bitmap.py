# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
# Modified 2023-01-31 by guicide
# Works on 64x64 and 32x32 LED Matrices
# This example uses one bitmap, so the display is updated when any pixel is changed
# See the "alternating bitmaps" example to see the display update after the bitmap is changed.
# with one bitmap:  161 redraws per minute (107 if bit_depth = 3)
# with two bitmaps: 291 redraws per minute (244 if bit_depth = 3)

SIXTYFOUR = True  # set to False for 32x32
COLORS = 8

import random
import board
import displayio
import framebufferio
import rgbmatrix
from rtc import RTC

displayio.release_displays()

# Fill bitmap with random 0-7 values
def randomize(bmp):
    SPACING = 1 # you may leave blank rows/cols on the display - try SPACING = 2
    for x in range(0, bmp.width, SPACING):
        for y in range(0, bmp.height, SPACING):
            bmp[y * bmp.height + x] = int(random.random() * COLORS)

if SIXTYFOUR:
    # bit_depth of 1 is about 33% faster than 3
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

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

print("Display is ", display.width, "x", display.height)

# create the only bitmap this example needs
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

# define an 8 color palette
palette[0] = 0x000000 # black
palette[1] = 0x9400D3 # purple
palette[2] = 0x0000FF # blue
palette[3] = 0x00FFFF # cyan
palette[4] = 0x00FF00 # green
palette[5] = 0xFFFF00 # yellow
palette[6] = 0xFF7F00 # orange
palette[7] = 0xFF0000 # red
display.auto_refresh = True
lp = 0 # just an FYI counter

while True:
    lp += 1
    ts = RTC().datetime
    if lp % 10 == 1:
        print("lp ", lp, ts.tm_min, ts.tm_sec)
    randomize(b1) # randomly fill the bitmap
