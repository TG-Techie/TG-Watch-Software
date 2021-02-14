from time import struct_time

try:
    import code
except:
    pass
import system
from system.drivers import rtc

weekdays = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def set_time(
    year=None,
    month=None,
    monthday=None,
    hours=None,
    mins=None,
    secs=None,
    weekday=None,
):

    now = rtc.datetime
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

    if year is not None:
        next["tm_year"] = year
        # rtc.datetime = struct_time(**next)

    if month is not None:
        next["tm_mon"] = month
        # rtc.datetime = struct_time(**next)

    if monthday is not None:
        next["tm_mday"] = monthday
        # rtc.datetime = struct_time(**next)

    if hours is not None:
        next["tm_hour"] = hours
        # rtc.datetime = struct_time(**next)

    if mins is not None:
        next["tm_min"] = mins
        # rtc.datetime = struct_time(**next)

    if secs is not None:
        next["tm_sec"] = secs
        # rtc.datetime = struct_time(**next)

    if weekday is not None:
        global weekdays
        if isinstance(weekday, str):
            n = weekdays.index(weekday.lower())
        else:
            n = weekday
        next["tm_wday"] = n
        # rtc.datetime = struct_time(**next)

    if next["tm_year"] >= 2100:
        raise RuntimeError(
            "something is wrong with the rtc IC, year set to"
            + f" {next['tm_year']} which is out of bounds"
        )
    rtc.datetime = struct_time(**next)

    print("time set to:", (struct_time_to_str(rtc.datetime)))

    system._refresh()
    system.clock._refresh_date()


def struct_time_to_str(tm):
    return (
        f"date(us): {weekdays[tm.tm_wday]} "
        f"{tm.tm_mon}/{tm.tm_mday}/{tm.tm_year}, "
        f"time(24): {tm.tm_hour}:{tm.tm_min}:{tm.tm_sec}, "
    )


def now():
    now = rtc.datetime
    print("current time:", (struct_time_to_str(now)))


now = rtc.datetime
print(struct_time_to_str(now))
