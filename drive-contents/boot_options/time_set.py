import displayio
import gc
import time
import sys

import oh_shit
import hardware
import system

from tg_gui_core import *
from tg_gui_core.stateful import StatefulAttribute
from tg_gui_std.all import *
from system.applocals import *
from setup.watchsetup import (
    DisplayioRootWrapper,
    screen,
    display,
    event_loop,
    Layout,
    Button,
    Label,
    Rect,
    singleinstance,
)

from setup.watchsetup import screen, display, event_loop
from setup.system_view import SystemView

import capsuleio
import supervisor
from time import struct_time
from system.drivers import rtc
import system
from system import clock


_selected_to_color = lambda s: default._fill_color_ if s else color.black


class TapRect(Rect):
    @StatefulAttribute(lambda self: False)
    def _selected_(self):
        pass

    def __init__(self, select_number: int, selected: State) -> None:
        self._select_number = select_number
        self._selected_state = selected
        self._is_selected = is_selected = DerivedState(
            selected, lambda a: a == select_number
        )

        super().__init__(radius=0, fill=is_selected >> _selected_to_color)

    def _select_(*_):
        pass

    def _deselect_(*_):
        pass

    def _press_(self):
        selected = self._selected_state
        selected.update(self, self._select_number)


@DisplayioRootWrapper(screen=screen, display=display, size=(240, 240))
class TimeView(Layout):
    def exit_time_set(self):
        capsuleio.bury("0")
        supervisor.reload()

    active = State(0)

    timestr = DerivedState((clock.hours, clock.mins), lambda h, m: f"{h:02}:{m:02}")
    datestr = DerivedState(
        (clock.weekdayname, clock.monthname, clock.monthday, clock.year),
        lambda w, m, d, y: (w[0:3] + " " + m[0:3] + f" {d:2}" + f" {y:4}"),
    )

    time_lbl = Label(size=7, text=timestr)
    date_lbl = Label(size=2, text=datestr)

    time_selection = HSplit(
        TapRect(0, active),
        TapRect(1, active),
        None,
        TapRect(2, active),
        TapRect(3, active),
    )

    date_selection = HSplit(
        TapRect(4, active),
        TapRect(5, active),
        TapRect(6, active),
        TapRect(7, active),
    )

    body = VSplit(
        ZStack(
            time_selection,
            time_lbl,
        ),
        ZStack(
            date_selection,
            date_lbl,
        ),
        HSplit(
            Button(text="+", press=self.increment(), size=3),
            # Button(text="->", press=self.next()),
            Button(text="Done", press=self.exit_time_set()),
        ),
    )

    def _any_(self):
        self.body(center, self.dims)

    def increment(self):
        _id_ = uid()

        hours = clock.hours.value(_id_)
        mins = clock.mins.value(_id_)
        h_ones = hours % 10
        h_tens = 10 * (hours // 10)
        weekday = clock.weekday.value(_id_)
        month = clock.month.value(_id_)
        monthday = clock.monthday.value(_id_)
        year = clock.year.value(_id_)

        if self.active == 0:
            if h_ones < 4:
                hours = (h_tens + 10) % 30 + h_ones
            else:
                hours = (h_tens + 10) % 20 + h_ones
        if self.active == 1:
            if h_tens < 20:
                hours = h_tens + ((h_ones + 1) % 10)
            else:
                hours = h_tens + ((h_ones + 1) % 4)
        if self.active == 2:
            mins = (mins + 10) % 60
        if self.active == 3:
            mins = 10 * (mins // 10) + (mins + 1) % 10
        if self.active == 4:
            weekday = (weekday + 1) % 7
        if self.active == 5:
            month = (month % 12) + 1
        if self.active == 6:
            if month in (1, 3, 5, 7, 8, 10, 12):
                monthday = (monthday % 31) + 1
            elif month in (4, 6, 9, 11):
                monthday = (monthday % 30) + 1
            else:
                if year % 4 == 0:
                    monthday = (monthday % 29) + 1
                else:
                    monthday = (monthday % 28) + 1
        if self.active == 7:
            year = 2000 + ((year % 100) + 1) % 50

        clock.set_24hour_time(
            year=year,
            month=month,
            monthday=monthday,
            hours=hours,
            mins=mins,
            secs=0,
            weekday=weekday,
        )

        clock._refresh_time()
        clock._refresh_date()

    def next(self):
        self.active = (self.active + 1) % 8


TimeView._superior_._std_startup_()
gc.collect()
print(gc.mem_free())
print("HALLO")
gc.collect()
try:
    print(gc.mem_free())
    while True:
        gc.collect()
        system._refresh()
        event_loop.loop()
        display.refresh()

except Exception as err:
    gc.collect()
    del WatchRoot, screen
    sys.print_exception(err)
    display.show(None)
    display.refresh()
    gc.collect()
    if isinstance(err, MemoryError):
        oh_shit.reset_countdown(10, err)
    else:
        oh_shit.reset_countdown(30, err)
