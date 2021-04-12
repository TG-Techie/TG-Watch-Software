from tg_gui_core import State, DerivedState, uid
import hardware
from hardware import drivers
import time
import low_battery
import microcontroller
import gc

_to_month = (
    "INVALID MONTH",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "Novemer",
    "December",
)
_to_weekday = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)

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


# using classes as modules, technically reduces ram size
class clock:
    _id_ = uid()

    year = State(0000)
    month = State(00)
    weekday = State(0)
    monthday = State(00)
    yearday = State(000)

    monthname = DerivedState(
        month,
        lambda m: _to_month[((m + 1) % 12) - 1],  # got a month == 25 sometimes
    )
    weekdayname = DerivedState(weekday, lambda w: _to_weekday[w])

    hours = State(0)
    mins = State(0)
    secs = State(0)

    _time = hours, mins, secs
    _date = year, month, weekday, monthday, yearday
    _prev_refresh = drivers.rtc.datetime

    def _refresh_time():
        global clock

        now = drivers.rtc.datetime
        hours, mins, secs = clock._time

        # if is 24 hour time:
        hours.update(clock, now.tm_hour)
        mins.update(clock, now.tm_min)
        secs.update(clock, now.tm_sec)

        if clock._prev_refresh.tm_hour > now.tm_hour:
            clock._refresh_date()
        clock._prev_refresh = now

    def _refresh_date():
        global clock

        now = drivers.rtc.datetime
        year, month, weekday, monthday, yearday = clock._date

        year.update(clock, now.tm_year)
        month.update(clock, now.tm_mon)
        monthday.update(clock, now.tm_mday)
        weekday.update(clock, now.tm_wday)
        yearday.update(clock, now.tm_yday)


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

    _last = -2

    def _refresh():
        now = time.monotonic()
        if now - power._last > 1:
            try:
                power.charging.update(power, drivers.vbus_detect.value)

                value = drivers._read_bat_percent()
                display._set_brightness(display.brightness.value(power))
                power.bat_percent.update(power, value)

                power._last = now
            except RuntimeError as err:
                pass

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
