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


from tg_gui_core.stateful import StatefulAttribute  # soon to be depricated
from tg_gui_core import (
    Widget,
    Specifier,
    align,
    DimensionSpecifier,
    StyledWidget,
    StyledAttribute,
    Style,
    State,
    align,
    styled,
    font,
)

from . import _imple as imple


class ButtonStyle(Style):
    _style_colors_ = ("fill", "text", "selected_fill", "selected_text")
    _style_elements_ = ("font", "alignment", "radius")


FIXME = lambda a: a


@styled(button_style=ButtonStyle)
class Button(StyledWidget):
    @StatefulAttribute(lambda self: False)
    def _selected_(self):
        self._change_coloring_to(self._selected_)

    _font = StyledAttribute("_font", "font")
    _alignment = StyledAttribute("_alignment", "alignment")
    _radius = StyledAttribute("_radius", "radius")

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_} {repr(self._text)}>"

    def __init__(
        self,
        text,
        *,
        action,
        font=None,
        alignment=None,
        radius=None,
        _y_adj=0,
        _x_adj=0,
        **kwargs,
    ):
        self._text = text
        super().__init__(**kwargs)

        self._y_adj = _y_adj
        self._x_adj = _x_adj

        self._font = font
        self._alignment = alignment
        self._radius = radius

        self._action_spec = action

        self._press_ = lambda: None

        self._colors = None
        self._selected_colors = None

    def _select_(self):
        self._selected_ = True

    def _deselect_(self):
        self._selected_ = False

    def _on_nest_(self):

        action = self._action_spec
        if isinstance(action, Specifier):
            action = action._resolve_specified_(self)
        self._press_ = action

    def _build_(self):

        super()._build_()
        radius = min(self._radius, self.width // 2, self.height // 2)

        self._group = group = imple.Group(max_size=2)

        self._rect = rect = imple.SimpleRoundRect(
            *(self._rel_coord_ + self._phys_size_),
            radius=radius,
        )

        rel_x, rel_y = self._rel_coord_
        self._label = label = imple.Label(
            text=" ",
            color=0xFFFFFF,  # temp color
            coord=(rel_x + self._x_adj, rel_y + self._y_adj),
            dims=self._phys_size_,
            alignment=self._alignment,
            scale=FIXME(2),  # imple.font_to_scale(self._font)
        )
        self._set_text(self._text)
        self._update_colors_(**self._style_._colors_)

        group.append(rect)
        group.append(label)

    def _set_text(self, text):
        # hot patch

        while len(text) <= 3:
            text = f" {text} "
        # print(self, repr(text))
        self._label.text = text

    def _update_colors_(self, fill, text, selected_fill, selected_text):
        self._colors = colors = (fill, text)
        self._selected_colors = selected_colors = (selected_fill, selected_text)
        self._change_coloring_to(self._selected_)

    def _change_coloring_to(self, selected):
        self._rect.fill, self._label.color = (
            self._selected_colors if selected else self._colors
        )
        # selected = self._selected_
        # self._rect.fill = selected_fill if selected else fill
        # self._label.color = selected_text if selected else text
