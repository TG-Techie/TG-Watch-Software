from tg_gui_std.all import *
from system.applocals import *


@singleinstance
class Application(Layout):

    r, g, b = State(0.5), State(0.5), State(0.5)
    rgb = DerivedState((r, g, b), lambda r, g, b: color.fromfloats(r, g, b))

    sample_color = Rect(fill=rgb)
    hexout = Label(text=DerivedState(rgb, lambda rgb: hex(rgb)))

    r_slider = Slider(value=r)
    g_slider = Slider(value=g)
    b_slider = Slider(value=b)

    def _any_(self):
        sample_size = (self.width // 2, self.height // 4)
        sample_color = self.sample_color((left, top), sample_size)
        hexout = self.hexout((right, top), sample_size)

        slider_size = (self.width, self.height // 4)
        r_slider = self.r_slider((center, below(sample_color)), slider_size)
        g_slider = self.g_slider(below(r_slider), slider_size)
        b_slider = self.b_slider(below(g_slider), slider_size)
