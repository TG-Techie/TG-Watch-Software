import supervisor
import microcontroller


import time
import gc
import sys


def reset_countdown(secs, err):
    gc.collect()
    if secs < 15:
        secs = 15
    elif secs > 200:
        secs = 200

    try:
        import hardware
        import terminalio
        from adafruit_display_text.label import Label

        display = hardware.display
        hardware.drivers.backlight.duty_cycle = 65535
        display.show(None)
        display.refresh()
        display.auto_refresh = True

        label = Label(
            terminalio.FONT,
            text="  " * 16 + "\n" * 3,
            y=10,
            x=10,
            scale=2,
        )
        display.show(label)
    except:
        hardware = None

    sys.print_exception(err)
    print(
        f"resetting system in {secs} seconds, the watch will disconnect. hit ctrl-c to enter repl"
    )

    for remaining in reversed(range(secs)):
        print(f"{remaining} seconds until reset, hit ctrl-c to enter repl")
        if hardware is not None:
            label.text = f"critical error\n resetting in {remaining}"
        time.sleep(1)
    else:
        print("reseting...")

        if hardware is not None:
            print("deiniting hardware")
            hardware.deinit()

        microcontroller.reset()
