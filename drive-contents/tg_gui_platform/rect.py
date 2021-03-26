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


class Rect(Widget):
    def __init__(self, radius=None, fill=None, **kwargs):
        super().__init__(**kwargs)

        self._fill_state = fill
        self._radius_src = radius

    def _build_(self):
        super()._build_()

        radius = self._radius_src
        if radius is None:
            radius = self._screen_.default.radius
        if isinstance(radius, DimensionSpecifier):
            radius = radius._resolve_specified_()

        self._radius = min(radius, self.width // 2, self.height // 2)

        self._group = imple.SimpleRoundRect(
            *(self._rel_coord_ + self._phys_size_),
            radius=self._radius,
        )

        # self._update_color()
        fill_state = self._fill_state
        if isinstance(fill_state, State):
            fill_state._register_handler_(self, self._update_color)
            self._update_color(fill_state.value(self))
        else:
            self._update_color(fill_state)

    def _demolish_(self):
        if isinstance(self._fill_state, State):
            self._fill_state._deregister_handler_(self)
        super()._demolish_()

    def _update_color(self, fill):

        if fill is None:
            fill = self._screen_.default._fill_color_
        assert isinstance(fill, int)
        if self.isplaced():
            self._group.fill = fill

    def __del__(self):
        del self._fill_
