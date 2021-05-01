import busio
import board

import displayio

displayio.release_displays()

import time

from pulseio import PWMOut
from digitalio import DigitalInOut

from adafruit_ds3231 import DS3231
from adafruit_focaltouch import Adafruit_FocalTouch
from adafruit_lc709203f import LC709203F
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from adafruit_drv2605 import DRV2605

# TODO: add setting to account for Haptic I2C magic bug

_min_bat_percent = 0.0
_max_bat_percent = 95.0
_percent_bat_range = _max_bat_percent - _min_bat_percent


def init():
    init_ports()
    init_display()
    init_sensors()


def deinit():
    deinit_sensors()
    deinit_display()
    deinit_ports()


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


def _read_bat_percent():
    global bat_sensor
    bat_int_val = bat_int.value

    for _ in range(30):
        try:
            raw = bat_sensor.cell_percent
            break
        except RuntimeError as err:
            pass
    else:
        print(
            f"{time.monotonic()}: battery read failed with intr ({bat_int_val}): `{err}`"
        )
        raise err

    return 100.0 * min(max(0, raw - _min_bat_percent) / _percent_bat_range, 1.0)


# --- object initing ---
def init_ports():
    global i2c, spi
    # init hardware io
    try:
        i2c = board.I2C()
        spi = board.SPI()
    except Exception as err:
        print("initing ports failed")
        deinit()
        raise err


def init_sensors():
    # init the sensors
    try:

        global touchscreen_reset, touchscreen
        touchscreen_reset = DigitalInOut(board.CTP_RST)
        touchscreen_reset.switch_to_output()
        _reset_touchscreen(touchscreen_reset)
        touchscreen = Adafruit_FocalTouch(i2c)

        global backlight
        backlight = PWMOut(board.BACKLIGHT, frequency=200)
        backlight.duty_cycle = 65535

        global rtc
        rtc = DS3231(i2c)

        global bat_sensor, bat_int
        bat_sensor = LC709203F(i2c)
        bat_int = DigitalInOut(board.BAT_INT)
        bat_int.switch_to_input()

        global accel
        accel = LSM6DSOX(i2c)

        global haptic, haptic_enable
        haptic_enable = DigitalInOut(board.HAPTIC_ENABLE)
        haptic_enable.switch_to_output()

        _enable_haptic()
        # haptic = DRV2605(i2c, address=0x5E)
        haptic = DRV2605(i2c, address=0x5A)

        global vbus_detect
        vbus_detect = DigitalInOut(board.VBUS_PRESENT)
        vbus_detect.switch_to_input()

    except Exception as err:
        print("initing sensors failed")
        deinit()

        raise err


def init_display():
    # init the display
    try:
        global display_bus, display
        display_bus = displayio.FourWire(
            spi,
            command=board.TFT_DC,
            chip_select=board.TFT_CS,
            reset=board.TFT_RST,
            baudrate=1000_000_000,
        )

        display = displayio.Display(
            display_bus,
            (  # init sequence
                b"\x01\x80\x96"  # _SWRESET and Delay 150ms
                b"\x11\x80\xFF"  # _SLPOUT and Delay 500ms
                b"\x3A\x81\x55\x0A"  # _COLMOD and Delay 10ms
                b"\x36\x01\x08"  # _MADCTL
                b"\x21\x80\x0A"  # _INVON Hack and Delay 10ms
                b"\x13\x80\x0A"  # _NORON and Delay 10ms
                b"\x36\x01\xC0"  # _MADCTL
                b"\x29\x80\xFF"  # _DISPON and Delay 500ms
            ),
            width=240,
            height=240,
            rowstart=80,
            rotation=180,
            # backlight_pin=board.BACKLIGHT,
            auto_brightness=False,
            brightness=0,
            auto_refresh=False,
        )

        display.show(None)
        display.auto_refresh = False
        display.refresh()

    except Exception as err:
        print(f"display initing failed")
        deinit()
        raise err


# --- object deiniting ---
def deinit_ports():
    try:
        i2c.deinit()
    except:
        pass

    try:
        spi.deinit()
    except:
        pass


def deinit_display():
    global display
    try:
        display.show(None)
        display.refresh()
    except:
        pass

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


def deinit_sensors():
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

    global accel
    try:
        accel.deinit()
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
