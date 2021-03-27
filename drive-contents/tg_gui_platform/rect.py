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

from tg_gui_core import Style, StyledWidget, StyledAttribute, styled
from . import _imple as imple


class RectStyle(Style):
    _style_colors_ = ("fill",)
    _style_elements_ = ("radius",)


@styled(rect_style=RectStyle)
class Rect(StyledWidget):

    _radius = StyledAttribute("_radius", "radius")

    def __init__(self, fill=None, radius=None, **kwargs):

        super().__init__(
            style=(None if fill is None else RectStyle.substyle(fill=fill)),
            **kwargs,
        )
        self._radius = radius

    def _build_(self):
        super()._build_()

        radius = min(self._radius, self.width // 2, self.height // 2)

        self._group = imple.SimpleRoundRect(
            *(self._rel_coord_ + self._phys_size_),
            radius=radius,
        )

        self._update_colors_(**self._style_._colors_)

    def _demolish_(self):
        if isinstance(self._fill_state, State):
            self._fill_state._deregister_handler_(self)
        super()._demolish_()

    def _update_colors_(self, *, fill):

        assert isinstance(fill, int)
        if self.isplaced():
            self._group.fill = fill

    def __del__(self):
        del self._fill_
