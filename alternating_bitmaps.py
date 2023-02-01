# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
# Modified 2023-01-31 by guicide
# Works on 64x64 and 32x32 LED Matrices
# This example uses two bitmaps, so the display is not updated until
# the other bitmap is made "active"
# See the "single bitmap" example to see the display
# update as the bitmap is changed.

SIXTYFOUR = True  # set to False for 32x32
COLORS = 8

import random
import board
import displayio
import framebufferio
import rgbmatrix

displayio.release_displays()

# Fill bitmap with random 0-7 values
def randomize(output):
    SPACING = 1 # you may leave blank rows/cols on the display - try SPACING = 2
    for x in range(0, output.width, SPACING):
        for y in range(0, output.height, SPACING):
            output[y * output.height + x] = int(random.random() * COLORS)

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
lp = 0 # counter (also tells us which bitmap to use)

while True:
    lp += 1 # inc loop counter
    print("lp ", lp)
    randomize(b[lp & 1]) # randomly fill a bitmap
    display.show(g[lp & 1]) # show a bitmap
