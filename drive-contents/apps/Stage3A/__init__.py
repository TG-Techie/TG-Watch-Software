from tg_gui_platform.all import *
from system.applocals import *


@singleinstance
class Application(Layout):

    some_data = State(0.5)

    our_label = Label(text="Can You See Me?")
    our_slider = Slider(value=some_data)

    def _any_(self):
        our_label = self.our_label(top, (self.width, self.height // 2))
        our_slider = self.our_slider(bottom, (9 * self.width // 10, self.height // 2))
