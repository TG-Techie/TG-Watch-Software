import busio
import board
import time
from adafruit_drv2605 import *
from digitalio import DigitalInOut

enable = DigitalInOut(board.HAPTIC_ENABLE)

enable.switch_to_output()
enable.value = 1

time.sleep(0.1)

i2c = board.I2C()

haptic = DRV2605(i2c, address=94)

haptic.sequence[0] = Effect(16)
haptic.play()
