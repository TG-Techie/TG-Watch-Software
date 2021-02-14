from tg_gui_platform.all import *
from system.applocals import *

print(f"calc imported")


@singleinstance
class Application(Layout):
    fill = State(color.red)

    rect = Rect(fill=fill)
    but1 = Button(text="Blue", press=self.set_color(color.blue))
    but2 = Button(text="Green", press=self.set_color(color.green))

    def _any_(self):
        size = (self.width // 2, self.height // 2)
        b1 = self.but1((left, bottom), size)
        b2 = self.but2((right, bottom), size)
        r = self.rect(top, size)

    def set_color(self, color):
        self.fill = color
