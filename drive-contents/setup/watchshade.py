from tg_gui_std.all import *

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
        if self.page is self.torch_panel:
            self.page = self.main_shade
        super()._hide_()

    @singleinstance
    class main_shade(Layout):

        slider = Slider(value=display.brightness)

        open_time = Button(
            text="time",
            radius=ratio(height // 2),
            press=lambda: None,
        )

        print(f"Layout._decalrable_={Layout._decalrable_}")
        open_torch = Button(
            text="torch",
            radius=ratio(height // 2),
            press=self._superior_.open_page(self._superior_.torch_panel),
        )

        reset = Button(text="Reset", press=_should_be_sys_reset)

        def _any_(self):
            slider = self.slider(top, (self.width, self.height // 4))
            size = (self.width // 2, self.height // 4)
            open_time = self.open_time((left, center), size)
            reset = self.reset((right, center), size)
            open_torch = self.open_torch(below(open_time), size)

        def close_shade(self):
            self._superior_.pop_view()

    @singleinstance
    class torch_panel(Layout):
        rect = Rect(fill=color.white)
        back = Button(
            text="<",
            press=self._superior_.pop_view(),
            margin=12,
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
