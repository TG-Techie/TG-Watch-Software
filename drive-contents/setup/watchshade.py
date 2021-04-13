from tg_gui_std.all import *
from system.applocals import *

import time
from time import struct_time
from system.drivers import rtc
import system
from system import display, clock
from system import _mem_monitor as mem_monitor


import hardware
import microcontroller


def _should_be_sys_reset():
    print("deiniting hardware")
    hardware.deinit()
    print("resetting mc")
    microcontroller.reset()


@singleinstance
class shade(Pages):
    page = PageState(self.main_shade)
    # _hot_rebuild_ = True

    open_stack = []

    def open_page(self, page_to_open):
        stack = self.open_stack
        if len(stack) == 0 or stack[-1] is not page_to_open:
            stack.append(self.page)
        self.page = page_to_open

    def pop_view(self):
        if len(self.open_stack):
            self.page = topage = self.open_stack.pop(-1)
        else:
            self.page = self.main_shade

    def _hide_(self):
        print(self, self.page)
        if self.page is self.torch_panel or self.page is self.time_panel:
            self.page = self.main_shade
        super()._hide_()

    @singleinstance
    class main_shade(Layout):

        slider = Slider(value=display.brightness)

        open_time = Button(
            text="time",
            radius=ratio(height // 2),
            press=self._superior_.open_page(self._superior_.time_panel),
        )

        print(f"Layout._decalrable_={Layout._decalrable_}")
        open_torch = Button(
            text="torch",
            radius=ratio(height // 2),
            press=self._superior_.open_page(self._superior_.torch_panel),
        )

        reset = Button(text="Reset", press=_should_be_sys_reset)

        monitor = Label(text=mem_monitor >> str)

        def _any_(self):
            slider = self.slider(top, (self.width, self.height // 4))
            size = (self.width // 2, self.height // 4)
            open_time = self.open_time((left, center), size)
            reset = self.reset((right, center), size)
            open_torch = self.open_torch(below(open_time), size)
            monitor = self.monitor(rightof(open_torch), size)

        def close_shade(self):
            self._superior_.pop_view()

    @singleinstance
    class torch_panel(Layout):
        rect = Rect(fill=color.white)
        back = Button(
            text="<",
            press=self._superior_.pop_view(),
            margin=default.margin * 2,
        )

        def _any_(self):
            self.rect(center, self.dims)
            self.back(
                (left, top),
                (7 * self.width // 24, 7 * self.height // 24),
            )

        def _show_(self):
            # stash the current brightness so the torch can be full brightness
            shade.previous_brightness = display.brightness.value(self)
            display.brightness.update(self, 1.0)
            super()._show_()

        def _hide_(self):
            super()._hide_()
            # always restore the original brightness
            display.brightness.update(self, shade.previous_brightness)

    @singleinstance
    class time_panel(Layout):
        active = State(0)

        timestr = DerivedState((clock.hours, clock.mins), lambda h, m: f"{h:02}:{m:02}")
        datestr = DerivedState(
            (clock.weekdayname, clock.monthname, clock.monthday, clock.year),
            lambda w, m, d, y: (w[0:3] + " " + m[0:3] + f" {d:2}" + f" {y:4}"),
        )

        time_lbl = Label(size=7, text=timestr)
        date_lbl = Label(size=2, text=datestr)

        time_selection = HSplit(
            Rect(
                radius=1,
                fill=DerivedState(
                    active, lambda a: color.black if a != 0 else default._fill_color_
                ),
            ),
            Rect(
                radius=1,
                fill=DerivedState(
                    active, lambda a: color.black if a != 1 else default._fill_color_
                ),
            ),
            None,
            Rect(
                radius=1,
                fill=DerivedState(
                    active, lambda a: color.black if a != 2 else default._fill_color_
                ),
            ),
            Rect(
                radius=1,
                fill=DerivedState(
                    active, lambda a: color.black if a != 3 else default._fill_color_
                ),
            ),
        )

        date_selection = HSplit(
            Rect(
                radius=1,
                fill=DerivedState(
                    active, lambda a: color.black if a != 4 else default._fill_color_
                ),
            ),
            Rect(
                radius=1,
                fill=DerivedState(
                    active, lambda a: color.black if a != 5 else default._fill_color_
                ),
            ),
            Rect(
                radius=1,
                fill=DerivedState(
                    active, lambda a: color.black if a != 6 else default._fill_color_
                ),
            ),
            Rect(
                radius=1,
                fill=DerivedState(
                    active, lambda a: color.black if a != 7 else default._fill_color_
                ),
            ),
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
                Button(text="^", press=self.increment()),
                Button(text="->", press=self.next()),
            ),
        )

        def _any_(self):
            self.body(center, self.dims)

        def increment(self):
            temp = rtc.datetime
            hours = temp.tm_hour
            mins = temp.tm_min
            h_ones = hours % 10
            h_tens = 10 * (hours // 10)
            weekday = temp.tm_wday
            month = temp.tm_mon
            monthday = temp.tm_mday
            year = temp.tm_year

            if self.active == 0:
                if h_ones < 4:
                    hours = (h_tens + 10) % 30 + h_ones
                else:
                    hours = (h_tens + 10) % 20 + h_ones
            if self.active == 1:
                if h_tens < 2:
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
                month = (month + 1) % 12
            if self.active == 6:
                if month in (0, 2, 4, 6, 7, 9, 11):
                    monthday = (monthday % 31) + 1
                elif month in (3, 5, 8, 11):
                    monthday = (monthday % 30) + 1
                else:
                    if year % 4 == 0:
                        monthday = (monthday % 29) + 1
                    else:
                        monthday = (monthday % 28) + 1
            if self.active == 7:
                year = 2000 + ((year % 100) + 1) % 50

            rtc.datetime = struct_time(
                (
                    year,
                    month,
                    monthday,
                    hours,
                    mins,
                    0,
                    weekday,
                    -1,
                    -1,
                )
            )

        def next(self):
            self.active = (self.active + 1) % 8
