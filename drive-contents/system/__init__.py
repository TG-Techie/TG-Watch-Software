from tg_gui_core import State, DerivedState, uid
import hardware
from hardware import drivers
from . import applocals, clock
import time
import low_battery
import microcontroller
import gc


# prototype memory monitor
_mem_monitor_counter = 0
_mem_monitor_refresh_counts = const(10)
_mem_monitor = State(None)  # start with None


def _refresh_mem_monitor():
    global _mem_monitor_counter
    # update on zero (so updates on initial state)
    if _mem_monitor_counter == 0:
        _mem_monitor.update(None, gc.mem_free())
    # tick counter
    _mem_monitor_counter = (_mem_monitor_counter + 1) % _mem_monitor_refresh_counts


class display:
    _id_ = uid()

    brightness = State(1.0)
    _phys_limits = (
        0.2,  # min
        1.0,  # max
    )

    def _set_brightness(brightness):
        # print(f"brightness={brightness}")
        global display
        # brightness = display.brightness.getvalue(None, display._set_brightness)

        display._write_brightness(brightness)

    def _write_brightness(brightness):
        phys_min, phys_max = display._phys_limits
        phys_range = phys_max - phys_min
        drivers.backlight.duty_cycle = round(
            65535 * (phys_range * brightness ** 2 + phys_min)
        )

    brightness._register_handler_(None, _set_brightness)


class power:
    _id_ = uid()

    bat_percent = State(0)  # State(100.0)
    charging = State(False)
    _min_percent = 0.0  # 20.0
    _max_percent = 95.0

    _last = -2

    _percent_range = _max_percent - _min_percent

    def _refresh():
        now = time.monotonic()
        if now - power._last > 1:
            try:
                raw = drivers.bat_sensor.cell_percent
                scaled = 100.0 * min(
                    max(0, raw - power._min_percent) / power._percent_range, 1.0
                )
                display._phys_limits = (0.1, 0.5) if scaled <= 20.0 else (0.2, 1.0)
                display._set_brightness(display.brightness.value(power))
                power.bat_percent.update(power, scaled)
                power.charging.update(power, drivers.vbus_detect.value)
                power._last = now
            except RuntimeError as err:
                print(f"{time.monotonic()}: battery read failed: `{err}`")

    def _boot():
        bat_percent = power.bat_percent.value(power)

        print(f"bat_percent={bat_percent}")

        if bat_percent < 2.0:
            low_battery.loop()
            microcontroller.reset()

        if bat_percent > 20.0:
            display.brightness.update(power, 0.8)

        else:
            display.brightness.update(power, 0.3)


class sensors:
    _id_ = uid()

    speed = 1

    gyro = (State(0), State(0), State(0))
    accel = (State(0), State(0), State(0))

    _last = time.monotonic()

    def _refresh():
        now = time.monotonic()
        if now - sensors._last > sensors.speed:
            y, x, z = drivers.accel.acceleration
            for state, value in zip(sensors.accel, (x, y, z)):
                state.update(sensors, value)
            y, x, z = drivers.accel.gyro
            for state, value in zip(sensors.gyro, (x, y, z)):
                state.update(sensors, value)
            sensors._last = now


def _refresh():
    global clock
    clock._refresh_time()
    power._refresh()
    sensors._refresh()
    _refresh_mem_monitor()
    # if midnight just passed:
    # clock._refresh_date()


_refresh()
clock._refresh_date()
power._refresh()
power._boot()
