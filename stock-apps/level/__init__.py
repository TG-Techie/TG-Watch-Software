from tg_gui_platform.all import *
from system.applocals import *
from system import sensors
import math


@singleinstance
class Application(Layout):

    accel_mag = DerivedState(
        sensors.accel, lambda x, y, z: math.sqrt(x ** 2 + y ** 2 + z ** 2)
    )

    percent_x = DerivedState(
        (sensors.accel[0], accel_mag),
        lambda x, m: abs(x) / m if m != 0 else 0,
    )

    percent_y = DerivedState(
        (sensors.accel[1], accel_mag),
        lambda y, m: abs(y) / m if m != 0 else 0,
    )

    x_label = Label(text="X:")
    y_label = Label(text="Y:")

    x = ProgressBar(progress=percent_x, margin=0)
    y = ProgressBar(progress=percent_y, margin=0)

    def _any_(self):
        bar_size = ((3 * self.width) // 4, self.height // 2)
        label_size = (self.width - bar_size[0], bar_size[1])
        x_bar = self.x((right, top), bar_size)
        self.x_label(leftof(x_bar), label_size)
        y_bar = self.y((right, bottom), bar_size)
        self.y_label(leftof(y_bar), label_size)

    def _show_(self):
        sensors.speed = 0.25
        super()._show_()

    def _hide_(self):
        super()._hide_()
        sensors.speed = 1
