import sys
import oh_shit
from hardware import drivers
import capsuleio

if not (capsuleio.unearth() in (None, "0")):
    from boot_options import time_set

if drivers._read_bat_percent() < 4:
    from boot_options import low_battery
else:
    # show splash while loading watch_gui
    from boot_options import splash_screen

    # init the gui system
    from boot_options import watch_gui

    # clean up splash
    sys.modules.pop(splash_screen.__name__)
    del splash_screen

    if __name__ == "__main__":
        watch_gui.run()
