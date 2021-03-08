from tg_gui_platform.all import *
from system.applocals import *

import time
import system
from system import clock, power

# from .appview import app_view


@singleinstance
class default_face(Layout):

    timestr = DerivedState((clock.hours, clock.mins), lambda h, m: f"{h:02}:{m:02}")
    datestr = DerivedState(
        (clock.weekdayname, clock.monthname, clock.monthday),
        lambda w, m, d: (w[0:3] + " " + m[0:3] + f" {d:02}"),
    )

    percent = Label(
        text=DerivedState(
            (power.bat_percent, power.charging),
            lambda b, s: f"^{round(b):3}%" if s else f"v{round(b):3}%",
        ),
        size=3,
        _alignment=align.trailing,
    )

    time_lbl = Label(size=7, text=timestr)
    date_lbl = Label(size=3, text=datestr)

    # apps_but = Button(
    #     text="Apps",
    #     margin=0,
    #     size=3,
    #     radius=ratio(height // 2),
    #     press=self._superior_.open_page(self._superior_.launcher),
    #     palette=palette.secondary,
    #     _y_adj=-5,
    # )
    # other_but = Button(
    #     text="cla",
    #     margin=0,
    #     size=3,
    #     radius=ratio(height // 2),
    #     press=lambda: self._superior_.app_view.close_app(),
    #     palette=palette.secondary,
    #     _y_adj=-5,
    #     _x_adj=3,
    # )

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
