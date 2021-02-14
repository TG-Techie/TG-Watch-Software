from tg_gui_platform.all import *
from system.applocals import *

print(f"Settings imported")


@singleinstance
class Application(Layout):

    wid = Label(text="Settings")  # , press=lambda: print("Settings"))

    def _any_(self):
        self.wid(center, (self.width // 2, self.height // 3))
