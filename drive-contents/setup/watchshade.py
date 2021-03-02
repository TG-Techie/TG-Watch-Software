from tg_gui_std.all import *
from system.applocals import *

import time
import system
from system import display


import hardware
import microcontroller


def _should_be_sys_reset():
    print("deiniting hardware")
    hardware.deinit()
    print("resetting mc")
    microcontroller.reset()


@singleinstance
class shade(Pages):
    page = PageState(0)

    open_stack = []

    def open_page(self, page_to_open):
        # print(self.open_stack)
        stack = self.open_stack
        if len(stack) == 0 or stack[-1] is not page_to_open:
            stack.append(self.page)
        self.page = page_to_open
        # print(self.open_stack)

    def pop_view(self):
        # print(self.open_stack)
        if len(self.open_stack):
            self.page = topage = self.open_stack.pop(-1)
        else:
            self.page = self.main_shade
        # print(self.open_stack)

    @singleinstance
    class main_shade(Layout):

        slider = Slider(value=display.brightness)

        open_time = Button(
            text="time",
            radius=ratio(height // 2),
            press=self._superior_.open_page(self._superior_.time_panel),
        )

        reset = Button(text="Reset", press=_should_be_sys_reset)

        def _wearable_(self):
            slider = self.slider((center, top), (self.width, self.height // 4))
            open_time = self.open_time(
                (left, center),
                (115, 59),
            )
            # done = self.done((center, bottom), (self.width, self.height // 4))
            reset = self.reset((right, center), (self.width // 2, self.height // 4))

        def close_shade(self):
            self._superior_.pop_view()

    @singleinstance
    class time_panel(Layout):
        back = Button(text="<", press=self._superior_.pop_view())
        fill = State(color.red)

        rect = Rect(fill=fill)
        but1 = Button(text="Calc", press=self.set_color(color.blue))
        but2 = Button(text="Calc", press=self.set_color(color.green))

        def _any_(self):
            back = self.back((left, top), (self.width // 4, self.height // 4))
            size = (self.width // 2, self.height // 2)
            b1 = self.but1((left, bottom), size)
            b2 = self.but2((right, bottom), size)
            r = self.rect((rightof(back), top), size)

        def set_color(self, color):
            self.fill = color
