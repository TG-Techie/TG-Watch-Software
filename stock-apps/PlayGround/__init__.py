from tg_gui_std.all import *
from system.applocals import *

from system import clock


@declarable
class View(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._body = self._scan_class_for_body()

    def _on_nest_(self):
        self._nest_(self._body)

    def _form_(self, dim_spec):
        self._body._form_(dim_spec)
        super(Container, self)._form_(self._body.dims)

    def _place_(self, pos_spec):
        super(Container, self)._place_(pos_spec)
        self._body._place_(center)

    def _build_(self):
        super(Container, self)._build_()
        self._body._build_()
        self._screen_.on_container_build(self)

    def _show_(self):
        super(Container, self)._show_()
        self._body._show_()
        self._screen_.on_container_show(self)

    def _scan_class_for_body(self):
        cls = type(self)
        body_attr = getattr(cls, "body")
        if isinstance(body_attr, property):
            return self.body
        elif isinstance(body_attr, Widget):
            return body_attr
        else:
            raise TypeError(f"{self} had no declared body attribute or property")


@singleinstance
class Application(Layout):

    switch_but = Button(text="switch", press=self.switch())

    @singleinstance
    class switcher(Pages):
        # page = PageState(self.page2)
        page = State(0)

        # page1 = Rect(fill=color.red)

        @singleinstance
        class page2(View):
            value = State(0.5)
            indicator = State(False)
            timestr = DerivedState(
                (clock.hours, clock.mins), lambda h, m: f"{h:02}:{m:02}"
            )

            body = VSplit(
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

            # def _any_(self):
            #     split = self.split(center, (self.width, self.height))

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
