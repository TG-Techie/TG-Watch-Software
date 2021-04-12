import time
import sys
import microcontroller
from hardware import drivers


if drivers._read_bat_percent() < 4:
    if drivers.vbus_detect.value:
        from setup import low_battery_splash

    while drivers._read_bat_percent() < 4:
        time.sleep(5)
        print(f"[time: {time.monotonic()}] battery too low, waiting to boot")
    else:
        print("battery charged to 4+ percent, restarting")
        microcontroller.reset()
else:
    # show splash while loading watch_gui
    from setup import splash_screen

    import watch_gui

    # clean up splash
    sys.modules.pop(splash_screen.__name__)
    del splash_screen

    watch_gui.run()
