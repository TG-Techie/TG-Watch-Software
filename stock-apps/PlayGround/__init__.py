from tg_gui_std.all import *
from system.applocals import *

from system import clock


@singleinstance
class Application(Layout):

    switch_but = Button(text="switch", press=self.switch())

    @singleinstance
    class switcher(Pages):
        # page = PageState(self.page2)
        page = State(0)

        # page1 = Rect(fill=color.red)

        @singleinstance
        class page2(Layout):
            value = State(0.5)
            indicator = State(False)
            timestr = DerivedState(
                (clock.hours, clock.mins), lambda h, m: f"{h:02}:{m:02}"
            )

            split = VSplit(
                HSplit(
                    Label(text=value >> (lambda s: f"{round(s, 3)}")),
                    ProgressBar(progress=value),
                ),
                Slider(value=value),
                HSplit(
                    Label(text=timestr),
                    # Rect(fill=indicator >> (lambda i: color.green if i else color.red)),
                    Hide(Rect(), when=~indicator),
                ),
                Button(text="foo", press=self.toggle_color),
            )

            def _any_(self):
                split = self.split(center, (self.width, self.height))

            def toggle_color(self):
                self.indicator = not self.indicator

        how_much = State(0.5)

        page3 = VSplit(
            Label(text=how_much >> (lambda hm: hm * 100) >> round >> str),
            Slider(value=how_much),
        )

    def _any_(self):
        self.switcher(top, (self.width, 3 * self.height // 4))
        self.switch_but(bottom, (self.width, self.height // 4))

    def switch(self):
        switcher = self.switcher
        switcher.page = (switcher.page + 1) % len(switcher)
