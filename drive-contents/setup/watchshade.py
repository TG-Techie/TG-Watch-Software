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

    temp_brightness = None

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
            # press=self._superior_.open_page(self._superior_.time_panel),
            press=self._superior_.pop_view(),
        )

        open_torch = Button(
            text="torch",
            radius=ratio(height // 2),
            press=self._superior_.open_page(self._superior_.torch_panel),
        )

        reset = Button(text="Reset", press=_should_be_sys_reset)

        def _wearable_(self):
            slider = self.slider((center, top), (self.width, self.height // 4))

            open_time = self.open_time(
                (left, center),
                (self.width // 2, self.height // 4),
            )

            # done = self.done((center, bottom), (self.width, self.height // 4))
            reset = self.reset((right, center), (self.width // 2, self.height // 4))
            open_torch = self.open_torch(
                (left, below(reset)),
                (self.width // 2, self.height // 4),
            )

        def close_shade(self):
            self._superior_.pop_view()

    @singleinstance
    class torch_panel(Layout):
        back = Button(text="<", press=self._superior_.pop_view())
        fill = State(color.white)

        rect = Rect(fill=fill)

        def _any_(self):
            r = self.rect((0, 0), (self.height, self.width))
            back = self.back((left, top), (self.width // 4, self.height // 4))

        def _render_(self):
            # print("torch rendered")
            shade.temp_brightness = display.brightness._value
            display.brightness.update(1.0)

            Widget._render_(self)
            for wid in self._nested_:
                if wid.isplaced():
                    wid._render_()
            self._screen_.on_container_render(self)

        def _derender_(self):
            # print("torch derendered")
            display.brightness.update(shade.temp_brightness)

            for wid in self._nested_:
                if wid.isplaced():
                    wid._derender_()
            Widget._derender_(self)
            self._screen_.on_container_derender(self)
