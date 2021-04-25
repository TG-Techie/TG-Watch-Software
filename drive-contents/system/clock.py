from time import struct_time
from hardware import drivers as _drivers
from tg_gui_core import State, DerivedState

# helper maps to
_months = (
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
_full_weekdays = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
_abrvd_weekdays = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

# start user exposed interace
year = State(0000)
month = State(00)
weekday = State(0)
monthday = State(00)
yearday = State(000)

monthname = DerivedState(
    month,
    lambda m: _months[((m + 1) % 12) - 1],  # got a month == 25 sometimes
)
weekdayname = DerivedState(weekday, lambda w: _full_weekdays[w])

hours = State(0)
mins = State(0)
secs = State(0)

# this after function: end user exposed interace
def set_24hour_time(
    year=None,
    month=None,
    monthday=None,
    hours=None,
    mins=None,
    secs=None,
    weekday=None,
):

    now = _drivers.rtc.datetime
    next = {
        "tm_year": now.tm_year,
        "tm_mon": now.tm_mon,
        "tm_mday": now.tm_mday,
        "tm_hour": now.tm_hour,
        "tm_min": now.tm_min,
        "tm_sec": now.tm_sec,
        "tm_wday": now.tm_wday,
        "tm_yday": -1,
        "tm_isdst": -1,
    }

    # set each feild of next to the input value if the caller gave a value
    if year is not None:
        next["tm_year"] = year

    if month is not None:
        next["tm_mon"] = month

    if monthday is not None:
        next["tm_mday"] = monthday

    if hours is not None:
        next["tm_hour"] = hours

    if mins is not None:
        next["tm_min"] = mins

    if secs is not None:
        next["tm_sec"] = secs

    # this accepts ints or abreviations
    if weekday is not None:
        global _abrvd_weekdays
        if isinstance(weekday, str):
            n = _abrvd_weekdays.index(weekday.lower())
        else:
            n = weekday
        next["tm_wday"] = n

    # warn for occasional error due to RTC IC heisenbug
    if next["tm_year"] >= 2100:
        raise RuntimeError(
            "something is wrong with the rtc IC, year set to"
            + f" {next['tm_year']} which is very unlikely"
        )

    # set the time over I2C
    _drivers.rtc.datetime = now_struct = struct_time(**next)
    print("time set to:", (_struct_time_to_str(now_struct)))

    # update user facing state
    _refresh_time()
    _refresh_date()


# end user exposed interace


# internal helper functions for formamtting and updating the user exposed state
# pre-packed groupings for ease of use
_time = hours, mins, secs
_date = year, month, weekday, monthday, yearday
_prev_refresh = _drivers.rtc.datetime


def _refresh_time():
    global _prev_refresh

    now = _drivers.rtc.datetime
    hours, mins, secs = _time

    # if is 24 hour time:
    hours.update(None, now.tm_hour)
    mins.update(None, now.tm_min)
    secs.update(None, now.tm_sec)

    if _prev_refresh.tm_hour > now.tm_hour:
        _refresh_date()
    _prev_refresh = now


def _refresh_date():

    now = _drivers.rtc.datetime
    year, month, weekday, monthday, yearday = _date

    year.update(None, now.tm_year)
    month.update(None, now.tm_mon)
    monthday.update(None, now.tm_mday)
    weekday.update(None, now.tm_wday)
    yearday.update(None, now.tm_yday)


def _struct_time_to_str(tm):
    return (
        f"date(us): {_abrvd_weekdays[tm.tm_wday]} "
        f"{tm.tm_mon}/{tm.tm_mday}/{tm.tm_year}, "
        f"time(24): {tm.tm_hour}:{tm.tm_min}:{tm.tm_sec}, "
    )
