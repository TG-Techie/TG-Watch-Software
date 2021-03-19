from tg_gui_platform.all import *
from system.applocals import *
from system import sensors


@singleinstance
class Application(Layout):

    gyro = Label(
        text=DerivedState(
            sensors.gyro,
            lambda x, y, z: f"Gyro\nX:{round(x,2):3}\nY:{round(y,2):3}\nZ:{round(z,2):3}",
        ),
        _alignment=align.leading,
    )
    accelerometer = Label(
        text=DerivedState(
            sensors.accel,
            lambda x, y, z: f"Accel\nX:{round(x,2):3}\nY:{round(y,2):3}\nZ:{round(z,2):3}",
        ),
        _alignment=align.trailing,
    )

    def _any_(self):
        label_size = (self.width // 2, self.height // 2)
        self.gyro((left, top), label_size)
        self.accelerometer((right, top), label_size)
