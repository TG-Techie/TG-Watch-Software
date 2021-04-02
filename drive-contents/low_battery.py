from hardware import drivers
import board
from time import sleep
from adafruit_lc709203f import LC709203F

bat_sensor = LC709203F(board.I2C())
bat = 0.0


def _refresh():
    global bat, bat_sensor
    try:
        bat = bat_sensor.cell_percent / 0.95
    except RuntimeError as err:
        print(f"Battery read failed: `{err}`")


def loop():
    drivers.deinit()

    print("Low power loop entered")

    while bat < 2.0:
        _refresh()
        print(f"Battery too low: {bat}%")
        sleep(5)
