import gc
import time
import displayio

from hardware import display

from adafruit_display_text import label
from adafruit_progressbar import ProgressBar
import terminalio

splash = displayio.Group()
display.show(splash)

splash_text = label.Label(terminalio.FONT,
    text="TG-Watch", color=0xffffff,
    scale=4, x=25, y=80
)

progress_bar = ProgressBar(30, 120, 180, 7,
    progress=0.0,
    stroke=0,
    bar_color=0xffffff
)

splash.append(splash_text)
splash.append(progress_bar)
time.sleep(.05)
display.refresh()

def update_progress(amount):
    global progress_bar
    for diff in range(int(progress_bar.progress*100), int(amount*100)):
        progress_bar.progress = diff/100
        display.refresh()
        time.sleep(.001)
    progress_bar.progress = amount
    display.refresh()

update_progress(.35)
