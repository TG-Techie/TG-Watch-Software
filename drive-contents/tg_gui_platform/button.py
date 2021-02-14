# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from tg_gui_core import *
from . import _imple as imple


class Button(Widget):
    @StatefulAttribute(lambda self: False)
    def _selected_(self):
        self._update_colors()

    def __init__(
        self,
        *,
        text,
        press,
        size=None,
        palette=None,
        radius=None,
        _alignment=align.center,
        _y_adj=0,
        _x_adj=0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._radius_src = radius
        self._y_adj = _y_adj
        self._x_adj = _x_adj

        self._text_state = text
        self._alignment = _alignment
        self._size = size

        self._press_spec = press
        self._palette = palette

    def _pickup_(self):
        unlink_from_src(widget=self, src=self._text_state)
        super()._pickup_()

    def _select_(self):
        self._selected_ = True

    def _deselect_(self):
        self._selected_ = False

    def _on_nest_(self):
        screen = self._screen_
        palette = self._palette
        if palette is None:
            self._palette = screen.palettes.primary

        press_spec = self._press_spec
        if isinstance(press_spec, AttributeSpecifier):
            self._press_ = press_spec._get_attribute_(self)
        elif isinstance(press_spec, ForwardMethodCall):
            self._press_ = press_spec._get_method_(self)
        else:
            self._press_ = press_spec

    def _place_(self, coord, dims):
        global imple
        super()._place_(coord, dims)

        size = self._size
        if size is None:
            size = self._screen_.default.font_size

        radius = self._radius_src
        if radius is None:
            radius = self._screen_.default.radius
        if isinstance(radius, DimensionSpecifier):
            radius = radius._calc_dim_(self)

        radius = min(radius, self.width // 2, self.height // 2)

        self._group = group = imple.Group(max_size=2)

        self._rect = rect = imple.SimpleRoundRect(*self._rel_placement_, radius=radius)
        # self._rect = rect = imple.NewRoundRect(*self._rel_placement_, r=radius)
        self._label = label = imple.Label(
            text=" ",
            color=0xFFFFFF,  # temp color
            coord=(self._rel_x_ + self._x_adj, self._rel_y_ + self._y_adj),
            dims=self._phys_dims_,
            alignment=self._alignment,
            scale=size,
        )
        self._update_text()
        self._update_colors()
        group.append(rect)
        group.append(label)

    def _render_(self):
        self._update_colors()
        self._update_text()
        super()._render_()

    def _update_text(self):
        text = src_to_value(
            src=self._text_state,
            widget=self,
            handler=self._update_text,
            default=" ",
        )
        # hot patch
        if len(text) == 1:
            text = f" {text} "
        # print(self, repr(text))
        self._label.text = text

    def _update_colors(self):
        # print("updating color", self, self._rect, self._label)
        selected = self._selected_
        palette = self._palette
        self._rect.fill = palette.selected_fill if selected else palette.fill_color
        self._label.color = palette.selected_text if selected else palette.text_color
