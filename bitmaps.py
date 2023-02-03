# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
# Modified 2023-01-31 by guicide
# Works on 64x64 and 32x32 LED Matrices
# This example uses one or two bitmaps:
# with 1: the display is updated as the bitmap is updated
# this causes a sweeping effect to appear
# 161 redraws per minute (107 if bit_depth = 3)
# with 2: the display is not updated until the other bitmap is made "active"
# this is better for animation and also faster
# 291 redraws per minute (244 if bit_depth = 3)

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
def randomize(output):
    SPACING = 1 # you may leave blank rows/cols on the display - try SPACING = 2
    for x in range(0, output.width, SPACING):
        for y in range(0, output.height, SPACING):
            output[y * output.height + x] = int(random.random() * COLORS)

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

# create the two bitmaps this example needs
b = [displayio.Bitmap(display.width, display.height, COLORS),
     displayio.Bitmap(display.width, display.height, COLORS)]
# create a palette with the same number of colors
palette = displayio.Palette(COLORS)
# create two TileGrids to tie the bitmaps to the palette
tg = [displayio.TileGrid(b[0], pixel_shader=palette),
      displayio.TileGrid(b[1], pixel_shader=palette)]
# create two Display Groups
g = [displayio.Group(scale=1),
     displayio.Group(scale=1)]
# add the TileGrids to the Display Groups
g[0].append(tg[0])
g[1].append(tg[1])

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
lp = -1 # counter (also tells us which bitmap to use)
ts = RTC().datetime
old_secs = ((ts.tm_hour * 60 + ts.tm_min) * 60 + ts.tm_sec)

while True:
    lp += 1 # inc loop counter
    ts = RTC().datetime
    m = 1 if lp >> 4 & 1 and lp & 1 else 0
    randomize(b[m]) # randomly fill a bitmap
    display.show(g[m]) # show a bitmap
    if lp & 0x0f == 0x0f:
        secs = ((ts.tm_hour * 60 + ts.tm_min) * 60 + ts.tm_sec)
        print("lp ", lp, "two bitmaps" if lp >> 4 & 1 else "one bitmap", secs - old_secs, "seconds")
        old_secs = secs
