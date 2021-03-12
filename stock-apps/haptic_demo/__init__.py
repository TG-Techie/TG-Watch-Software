from tg_gui_std.all import *
from system.applocals import *
from hardware import drivers
import adafruit_drv2605


@singleinstance
class Application(Layout):
    def vibrate(self, mode):
        drivers.haptic.sequence[0] = adafruit_drv2605.Effect(mode)
        drivers.haptic.play()

    buttons = VSplit(
        HSplit(
            Button(text="Click", press=self.vibrate(1)),
            Button(text="Sharp", press=self.vibrate(4)),
        ),
        HSplit(
            Button(text="Soft", press=self.vibrate(7)),
            Button(text="Buzz", press=self.vibrate(14)),
        ),
        HSplit(
            Button(text="Double", press=self.vibrate(10)),
            Button(text="Alert", press=self.vibrate(16)),
        ),
    )

    def _any_(self):
        self.buttons(center, (self.width, self.height))
