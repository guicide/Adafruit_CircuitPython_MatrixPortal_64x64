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
COLORS = 4

import random
import time
import board
import displayio
import framebufferio
import rgbmatrix

displayio.release_displays()

# Conway's "Game of Life" is played on a grid with simple rules, based
# on the number of filled neighbors each cell has and whether the cell itself
# is filled.
#   * If the cell is filled, and 2 or 3 neighbors are filled, the cell stays
#     filled
#   * If the cell is empty, and exactly 3 neighbors are filled, a new cell
#     becomes filled
#   * Otherwise, the cell becomes or remains empty
#
# The complicated way that the "m1" (minus 1) and "p1" (plus one) offsets are
# calculated is due to the way the grid "wraps around", with the left and right
# sides being connected, as well as the top and bottom sides being connected.
#
# This function has been somewhat optimized, so that when it indexes the bitmap
# a single number [x + width * y] is used instead of indexing with [x, y].
# This makes the animation run faster with some loss of clarity. More
# optimizations are probably possible.

def apply_life_rule(old, new):
    width = old.width
    height = old.height
    for y in range(height):
        yyy = y * width
        ym1 = ((y + height - 1) % height) * width
        yp1 = ((y + 1) % height) * width
        xm1 = width - 1
        for x in range(width):
            xp1 = (x + 1) % width
            neighbors = (
                (old[xm1 + ym1] > 0) + (old[xm1 + yyy] > 0) + (old[xm1 + yp1] > 0) +
                (old[x   + ym1] > 0) +                        (old[x   + yp1] > 0) +
                (old[xp1 + ym1] > 0) + (old[xp1 + yyy] > 0) + (old[xp1 + yp1] > 0))
            new[x+yyy] = neighbors == 3 or (neighbors == 2 and old[x+yyy])
            if new[x+yyy] > 0 and new[x+yyy] < COLORS - 1:
#                new[x+yyy] = 2 # all cells are yellow
                new[x+yyy] += 1 # new cells are yellow, existing cells are cyan
            xm1 = x

# Fill 'fraction' out of all the cells.
def randomize(output, fraction=0.33):
    BORDER = 8
    for x in range(output.width):
        for y in range(output.height):
            if SIXTYFOUR == True and (x < BORDER or x > (output.width - BORDER) or y < BORDER or y > (output.height - BORDER)):
                output[y * output.height + x] = 0
            else:
                output[y * output.height + x] = (random.random() < fraction) << 1

# Fill the grid with a tribute to John Conway
def conway(output):
    # based on xkcd's tribute to John Conway (1937-2020) https://xkcd.com/2293/
    conway_data = [
        b'  +++   ',
        b'  + +   ',
        b'  + +   ',
        b'   +    ',
        b'+ +++   ',
        b' + + +  ',
        b'   +  + ',
        b'  + +   ',
        b'  + +   ',
    ]
    for i in range(output.height * output.width):
        output[i] = 0
    for i, si in enumerate(conway_data):
        y = int(output.height/2) - len(conway_data) - 2 + i
        for j, cj in enumerate(si):
            output[(output.width - 8)//2 + j, y] = (cj & 1) << 1

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

palette[0] = 0x000000 # black
palette[1] = 0x800000 # red
palette[2] = 0x808000 # yellow
palette[3] = 0x008080 # cyan

# First time, show the Conway tribute
conway(b[0])
display.show(g[0])
display.auto_refresh = True
time.sleep(1) # leave figure on screen for 1 second before beginning animation
n = 40
lp = 0

while True:
    lp += 1 # inc FYI loop counter
    print("lp ", lp)
    # run n generations.
    # For the Conway tribute on 64x32, 40 frames is appropriate.  For random
    # values, 400 frames seems like a good number.  Working in this way, with
    # two bitmaps, reduces copying data and makes the animation a bit faster
    for i in range(n):
        display.show(g[i & 1])
        apply_life_rule(b[i & 1], b[1 - (i & 1)])
        pass

    time.sleep(3) # pause 3 seconds after each animation
    # After n generations, fill the board with random values
    randomize(b[0])
    n = 400
