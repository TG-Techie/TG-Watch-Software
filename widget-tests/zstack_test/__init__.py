from tg_gui_std.all import *
from tg_gui_std.zstack import ZStack
from system.applocals import *

print(f"calc imported")


def StatefulButton(text, *, action):
    return ZStack(
        Button(text="", press=self.increment()),
        Label(text=text, size=3),
    )


@singleinstance
class Application(Layout):
    counter = State(0)

    body = StatefulButton(counter >> str, action=self.increment())

    def _any_(self):
        self.body(center, (self.width // 2, self.height // 2))

    def increment(self):
        self.counter += 1
