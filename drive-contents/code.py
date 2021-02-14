import displayio
import gc
import time
import sys

import oh_shit

try:
    import hardware
except Exception as err:
    if "SCK in use" in err.args or "lock timed out" in err.args[0]:
        import oh_shit

        oh_shit.reset_countdown(30, err)
    raise err

import system
from system import clock


from tg_gui_core import *
from setup.watchsetup import (
    DisplayioRootWrapper,
    screen,
    display,
    event_loop,
    Layout,
    Button,
    Rect,
    singleinstance,
)

from tg_gui_std.all import Pages, PageState

print(gc.mem_free())


from setup.system_view import SystemView

print(gc.mem_free())

SWIPE_HEIGHT = const(15)
SWIPE_WIDTH = const(20)


@DisplayioRootWrapper(screen=screen, display=display, size=(240, 240))
class WatchRoot(Layout):

    swipeup = Widget(margin=0)
    swipedown = Widget(margin=0)
    swipeleft = Widget(margin=0)
    swiperight = Widget(margin=0)
    system_view = SystemView()

    def _wearable_(self):
        view = self.system_view((left, top), self.dims)
        self.swipeup((0, 240), (self.width, SWIPE_HEIGHT))
        self.swipedown((0, 0), (self.width, SWIPE_HEIGHT))
        self.swipeleft((240, 0), (SWIPE_WIDTH, self.height))
        self.swiperight((0, 0), (SWIPE_WIDTH, self.height))


swipeup = WatchRoot.swipeup
swipedown = WatchRoot.swipedown
swipeleft = WatchRoot.swipeleft
swiperight = WatchRoot.swiperight
# print(f"swipeup={swipeup}, swipedown={swipedown}")

swipeup._start_coord_ = lambda coord: None  # print('swipeup._start_coord_', coord)
swipeup._update_coord_ = lambda _: None
swipeup._last_coord_ = lambda coord: (
    WatchRoot.system_view.swipe_up() if coord[1] <= 0 else None
)

swipedown._start_coord_ = lambda _: None
swipedown._update_coord_ = lambda _: None
swipedown._last_coord_ = lambda coord: (
    WatchRoot.system_view.swipe_down() if coord[1] >= SWIPE_HEIGHT else None
)
print(gc.mem_free())


WatchRoot._superior_._std_startup_()
gc.collect()

# a = Rect(fill=color.red)
# b = Rect(fill=color.blue)
# a._id_ = "'red'"
# b._id_ = "'blue'"
#
# WatchRoot.system_view.appview.app = a
# WatchRoot.system_view.appview.app = b
# print(WatchRoot.system_view.appview._nested_)
if __name__ == "__main__":

    try:
        gc.collect()
        print(gc.mem_free())
        while True:
            gc.collect()
            # print("loop:", gc.mem_free())
            # _ in range(30):
            system._refresh()
            event_loop.loop()
            display.refresh()

    except Exception as err:
        gc.enable()
        print("exiting")
        del WatchRoot, screen
        gc.collect()

        sys.print_exception(err)
        try:
            with open("error.text", "w") as file:
                sys.print_exception(err, file=file)
        except:
            pass
        display.show(None)
        display.refresh()
        # hardware.deinit()
        if isinstance(err, MemoryError):
            oh_shit.reset_countdown(10, err)
        else:
            oh_shit.reset_countdown(30, err)

else:
    display.auto_refresh = True
