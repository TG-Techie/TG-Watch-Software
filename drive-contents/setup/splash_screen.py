import gc
import time
import displayio

from hardware import display

from adafruit_display_text import label

# from adafruit_progressbar import ProgressBar
import terminalio

splash = displayio.Group()
display.show(splash)

splash_text = label.Label(
    terminalio.FONT, text="TG-Watch", color=0xFFFFFF, scale=4, x=25, y=80
)
