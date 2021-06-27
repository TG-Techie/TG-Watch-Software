import displayio
import gc
import time
import sys

import oh_shit
import hardware
import system

from tg_gui_core import Widget, Layout, left, top
from tg_gui_platform.root_wrapper import DisplayioRootWrapper

from setup.watchsetup import screen, display, event_loop
from setup.system_view import SystemView


_SWIPE_HEIGHT = const(15)
_SWIPE_WIDTH = const(20)


@DisplayioRootWrapper(screen=screen, display=display, size=(240, 240))
class WatchRoot(Layout):

    swipeup = Widget(margin=0)
    swipedown = Widget(margin=0)
    swipeleft = Widget(margin=0)
    swiperight = Widget(margin=0)
    system_view = SystemView()

    def _wearable_(self):
        view = self.system_view((left, top), self.dims)
        self.swipeup((0, 240), (self.width, _SWIPE_HEIGHT))
        self.swipedown((0, 0), (self.width, _SWIPE_HEIGHT))
        # self.swipeleft((240, 0), (_SWIPE_WIDTH, self.height))
        # self.swiperight((0, 0), (_SWIPE_WIDTH, self.height))


swipeup = WatchRoot.swipeup
swipedown = WatchRoot.swipedown
# swipeleft = WatchRoot.swipeleft
# swiperight = WatchRoot.swiperight

swipeup._start_coord_ = lambda _: None
swipeup._update_coord_ = lambda _: None
swipeup._last_coord_ = lambda coord: (
    WatchRoot.system_view.swipe_up() if coord[1] <= 0 else None
)

swipedown._start_coord_ = lambda _: None
swipedown._update_coord_ = lambda _: None
swipedown._last_coord_ = lambda coord: (
    WatchRoot.system_view.swipe_down() if coord[1] >= _SWIPE_HEIGHT else None
)


system_view = WatchRoot.system_view
event_loop.add_touch_timeout(25, lambda: system_view.pop_to_face())

WatchRoot._superior_._std_startup_()
gc.collect()
print(gc.mem_free())


def run():
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
        sys.print_exception(err)
        display.show(None)
        display.refresh()
        gc.collect()
        if isinstance(err, MemoryError):
            oh_shit.reset_countdown(10, err)
        else:
            oh_shit.reset_countdown(30, err)
