from tg_gui_std.all import *
from system.applocals import *

import time
import system
from system import clock, power

# from .appview import app_view


@singleinstance
class default_face(Layout):

    # lock_text = DerivedState(
    #     system.display.is_locked,
    #     lambda l: "Locked" if l else "Unlocked",
    # )

    timestr = DerivedState((clock.hours, clock.mins), lambda h, m: f"{h:02}:{m:02}")
    datestr = DerivedState(
        (clock.weekdayname, clock.monthname, clock.monthday),
        lambda w, m, d: (w[0:3] + " " + m[0:3] + f" {d:02}"),
    )

    percent = Label(
        text=DerivedState(
            (power.bat_percent, power.charging),
            lambda b, s: f"^{round(b)}%" if s else f"{round(b)}%",
        ),
        size=3,
        _alignment=align.trailing,
    )

    time_lbl = Label(size=7, text=timestr)
    date_lbl = Label(size=3, text=datestr)
    # lock_indicator = Label(text=lock_text, _alignment=align.leading)

    def _wearable_(self):
        launch_size = (self.width // 2, self.height // 4)
        # shade = self.shade_but(
        #     (center, top),
        #     (5 * self.width // 12, self.height // 6),
        # )
        time = self.time_lbl((center, self.height // 6), (self.width, self.height // 3))
        date = self.date_lbl(below(time), (self.width, self.height // 5))
        # apps = self.apps_but((right, bottom), launch_size)
        # other = self.other_but((left, bottom), launch_size)

        self.percent((right, top), (self.width // 3, self.height // 6))
        # self.lock_indicator((left, top), (2 * self.width // 3, self.height // 6))
