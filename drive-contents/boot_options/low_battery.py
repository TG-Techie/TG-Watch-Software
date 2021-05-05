import time
import microcontroller
from hardware import drivers

if drivers.vbus_detect.value:
    from . import low_battery_splash

while drivers._read_bat_percent() < 4:
    time.sleep(5)
    print(f"[time: {time.monotonic()}] battery too low, waiting to boot")
else:
    print("battery charged to 4+ percent, restarting")
    microcontroller.reset()
