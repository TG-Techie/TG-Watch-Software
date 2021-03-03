from . import ports
import board
import time

from pulseio import PWMOut
from digitalio import DigitalInOut

from adafruit_ds3231 import DS3231
from adafruit_focaltouch import Adafruit_FocalTouch
from adafruit_lc709203f import LC709203F
from adafruit_drv2605 import DRV2605


def deinit():
    global touchscreen
    try:
        del touchscreen
    except:
        pass

    global rtc
    try:
        del rtc
    except:
        pass

    global backlight
    try:
        backlight.deinit()
    except:
        pass

    global bat_sensor
    try:
        bat_sensor.deinit()
    except:
        pass

    global vbus_detect
    try:
        vbus_detect.deinit()
    except:
        pass

    global haptic
    try:
        haptic.deinit()
    except:
        pass


def _reset_touchscreen(pin):
    # global touchscreen_reset
    print("resetting touchscreen")
    pin.value = True
    time.sleep(0.005)

    pin.value = False
    time.sleep(0.005)

    pin.value = True
    time.sleep(0.3)


def _enable_haptic():
    haptic_enable.value = 1


def _disable_haptic():
    haptic_enable.value = 0


try:
    haptic_enable = DigitalInOut(board.HAPTIC_ENABLE)
    haptic_enable.switch_to_output()

    touchscreen_reset = DigitalInOut(board.CTP_RST)
    touchscreen_reset.switch_to_output()

    _reset_touchscreen(touchscreen_reset)

    touchscreen = Adafruit_FocalTouch(ports.i2c)

    backlight = PWMOut(board.BACKLIGHT, frequency=200)
    backlight.duty_cycle = 65535

    rtc = DS3231(ports.i2c)

    bat_sensor = LC709203F(ports.i2c)

    _enable_haptic()
    haptic = DRV2605(ports.i2c, address=0x5E)

    vbus_detect = DigitalInOut(board.VBUS_PRESENT)
    vbus_detect.switch_to_input()

except Exception as err:

    deinit()

    raise err
