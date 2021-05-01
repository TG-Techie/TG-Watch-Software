import sys
import oh_shit
from hardware import drivers

# # try to import the hardware, this check may not be needed anymore
# try:
#     from hardware import drivers
# except Exception as err:
#     if "SCK in use" in err.args or "lock timed out" in err.args[0]:
#         import oh_shit
#
#         oh_shit.reset_countdown(30, err)
#     raise err


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
