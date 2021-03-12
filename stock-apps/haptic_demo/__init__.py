from tg_gui_platform.all import *
from system.applocals import *
from hardware import drivers
import adafruit_drv2605


@singleinstance
class Application(Layout):
    def vibrate(self, mode):
        drivers.haptic.sequence[0] = adafruit_drv2605.Effect(mode)
        drivers.haptic.play()

    but1 = Button(text="Click", press=self.vibrate(1))
    but2 = Button(text="Sharp", press=self.vibrate(4))
    but3 = Button(text="Soft", press=self.vibrate(7))
    but4 = Button(text="Buzz", press=self.vibrate(14))

    def _any_(self):
        size = (self.width // 2, self.height // 2)
        b1 = self.but1((left, top), size)
        b2 = self.but2((right, top), size)
        b3 = self.but3((left, bottom), size)
        b4 = self.but4((right, bottom), size)
