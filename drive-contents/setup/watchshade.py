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
            (clock.weekdayname, clock.monthname, clock.monthday),
            lambda w, m, d: (w[0:3] + " " + m[0:3] + f" {d:02}"),
        )

        time_lbl = Label(size=7, text=timestr)
        date_lbl = Label(size=3, text=datestr)

        time_selection = HSplit(
            Hide(Rect(radius=1), when=DerivedState(active, lambda a: a != 0)),
            Hide(Rect(radius=1), when=DerivedState(active, lambda a: a != 1)),
            Label(text=""),
            Hide(Rect(radius=1), when=DerivedState(active, lambda a: a != 2)),
            Hide(Rect(radius=1), when=DerivedState(active, lambda a: a != 3)),
        )

        body = VSplit(
            ZStack(
                time_selection,
                time_lbl,
            ),
            date_lbl,
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
            if self.active == 0:
                if h_ones < 3:
                    hours = (h_tens + 10) % 30 + h_ones
                else:
                    hours = (h_tens + 10) % 20 + h_ones
            if self.active == 1:
                if h_tens < 2:
                    hours = h_tens + ((h_ones + 1) % 10)
                else:
                    hours = h_tens + ((h_ones + 1) % 3)
            if self.active == 2:
                mins = (mins + 10) % 60
            if self.active == 3:
                mins = 10 * (mins // 10) + (mins + 1) % 10

            rtc.datetime = struct_time(
                (
                    temp.tm_year,
                    temp.tm_mon,
                    temp.tm_mday,
                    hours,
                    mins,
                    0,
                    temp.tm_wday,
                    -1,
                    -1,
                )
            )

        def next(self):
            _id_ = uid()
            self.active = (self.active + 1) % 4
