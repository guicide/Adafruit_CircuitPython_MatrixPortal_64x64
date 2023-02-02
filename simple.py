# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# This example implements a simple two line scroller using
# Adafruit_CircuitPython_Display_Text. Each line has its own color
# and it is possible to modify the example to use other fonts and non-standard
# characters.

import adafruit_display_text.label
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import time
#  from digitalio import DigitalInOut, Direction
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle

# If there was a display before (protomatter, LCD, or E-paper), release it so
# we can create ours
displayio.release_displays()

# This next call creates the RGB Matrix object itself. It has the given width
# and height. bit_depth can range from 1 to 6; higher numbers allow more color
# shades to be displayed, but increase memory usage and slow down your Python
# code. If you just want to show primary colors plus black and white, use 1.
# Otherwise, try 3, 4 and 5 to see which effect you like best.
matrix = rgbmatrix.RGBMatrix(
    width=64, height=64, bit_depth=1,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
        board.MTX_R2, board.MTX_G2, board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
        board.MTX_ADDRD, board.MTX_ADDRE],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE)

# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

print("Display is ", display.width, "x", display.height)

# Put each line of text into a Group, then show that group.
g = displayio.Group()

# Rect(Col, Row, Width, Height, RGB)
rect1 = Rect(14, 11, 33, 12, fill=0xc0c000)
g.append(rect1)
rect2 = Rect(15, 12, 31, 10, fill=0x000000)
g.append(rect2)

line1 = Line(x0=0, y0=63, x1=63, y1=63, color=0x00c0c0)
g.append(line1)

circle1 = Circle(x0=31, y0=55, r=8, fill=0xc000c0)
g.append(circle1)

Draw_R = adafruit_display_text.label.Label(terminalio.FONT, color=0xc00000, text="Red")
Draw_R.x = 1
Draw_R.y = 30
Draw_G = adafruit_display_text.label.Label(terminalio.FONT, color=0x00c000, text="Grn")
Draw_G.x = 23
Draw_G.y = 30
Draw_B = adafruit_display_text.label.Label(terminalio.FONT, color=0x0000c0, text="Blu")
Draw_B.x = 45
Draw_B.y = 30
Draw_64 = adafruit_display_text.label.Label(terminalio.FONT, color=0xc0c0c0, text="64x64")
Draw_64.x = 16
Draw_64.y = 16

g.append(Draw_R)
g.append(Draw_G)
g.append(Draw_B)
g.append(Draw_64)
display.show(g)
display.refresh(minimum_frames_per_second=0)

time.sleep(1)

x=0
y=14
rect3 = Rect(x, y, 1, 1, fill=0x00c000)
g.append(rect3)
# display.show(g)
# display.refresh(minimum_frames_per_second=0)

while True:
#    print(x, y)
#    time.sleep(0.001)
    rect3.x = x
    rect3.y = y
#    g.append(rect3)
#    display.show(g)
    display.refresh(minimum_frames_per_second=0)
    x += 1
    if x >= display.width:
        time.sleep(0.001)
        x = 0
        y += 1
        if y >= display.height:
            y = 0

    pass
