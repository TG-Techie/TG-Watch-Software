from tg_gui_core.stateful import State, DerivedState
import hardware
from hardware import drivers
from . import applocals
import time

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

# using classes as modules, technically reduces ram size
class clock:
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
        hours.update(now.tm_hour)
        mins.update(now.tm_min)
        secs.update(now.tm_sec)

        if clock._prev_refresh.tm_hour > now.tm_hour:
            clock._refresh_date()
        clock._prev_refresh = now

    def _refresh_date():
        global clock

        now = drivers.rtc.datetime
        year, month, weekday, monthday, yearday = clock._date

        year.update(now.tm_year)
        month.update(now.tm_mon)
        monthday.update(now.tm_mday)
        weekday.update(now.tm_wday)
        yearday.update(now.tm_yday)


class display:

    brightness = State(1.0)
    _phys_limits = (
        0.2,  # min
        1.0,  # max
    )

    def _set_brightness(brightness):
        print(f"brightness={brightness}")
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

    bat_percent = State(0)  # State(100.0)
    _min_percent = 0.0  # 20.0
    _max_percent = 95.0

    _last = time.monotonic()

    _percent_range = _max_percent - _min_percent

    def _refresh():
        now = time.monotonic()
        if now - power._last > 1:
            try:
                raw = drivers.bat_sensor.cell_percent
                display.brightness.update(display.brightness._value)
                scaled = 100.0 * min(
                    max(0, raw - power._min_percent) / power._percent_range, 1.0
                )
                display._phys_limits = (0.1, 0.5) if scaled <= 20.0 else (0.2, 1.0)
                power.bat_percent.update(scaled)
                power._last = now
            except RuntimeError as err:
                print(f"{time.monotonic()}: battery read failed: `{err}`")


def _refresh():
    global clock
    clock._refresh_time()
    power._refresh()
    # if midnight just passed:
    # clock._refresh_date()


_refresh()
clock._refresh_date()
power._refresh()
