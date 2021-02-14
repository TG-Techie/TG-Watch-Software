from . import ports

import time
import board
import displayio
from adafruit_st7789 import ST7789


def deinit():
    global display
    display.show(None)
    display.refresh()

    global display_bus
    try:
        del display_bus
    except:
        pass

    try:
        del display
    except:
        pass

    displayio.release_displays()


try:
    display_bus = displayio.FourWire(
        ports.spi,
        command=board.TFT_DC,
        chip_select=board.TFT_CS,
        reset=board.TFT_RST,
        baudrate=1000_000_000,
    )

    display = ST7789(
        display_bus,
        width=240,
        height=240,
        rowstart=80,
        rotation=180,
        # backlight_pin=board.BACKLIGHT,
        auto_brightness=False,
        brightness=0,
        auto_refresh=False,
    )

except Exception as err:
    deinit()
    raise err

display.show(displayio.Group())
display.refresh()
time.sleep(0.05)
# display.brightness = 1.0
