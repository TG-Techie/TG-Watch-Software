from . import ports

import time
import board
import displayio

# from adafruit_st7789 import ST7789
from displayio import Display


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
    _INIT_SEQUENCE = (
        b"\x01\x80\x96"  # _SWRESET and Delay 150ms
        b"\x11\x80\xFF"  # _SLPOUT and Delay 500ms
        b"\x3A\x81\x55\x0A"  # _COLMOD and Delay 10ms
        b"\x36\x01\x08"  # _MADCTL
        b"\x21\x80\x0A"  # _INVON Hack and Delay 10ms
        b"\x13\x80\x0A"  # _NORON and Delay 10ms
        b"\x36\x01\xC0"  # _MADCTL
        b"\x29\x80\xFF"  # _DISPON and Delay 500ms
    )

    display = Display(
        display_bus,
        _INIT_SEQUENCE,
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
