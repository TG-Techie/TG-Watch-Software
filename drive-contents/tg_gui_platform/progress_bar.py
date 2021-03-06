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


class ProgressBar(Widget):
    def __init__(self, *, progress, palette=None, _fill_space=False, **kwargs):
        super().__init__(**kwargs)

        self._fill_space = _fill_space
        self._progress_state = progress
        self._palette = None

    def _on_nest_(self):
        if self._palette is None:
            self._palette = self._screen_.palettes.primary

    def _build_(self):
        super()._build_()

        self._group = imple.Group(max_size=2)

        rx, ry = self._rel_coord_
        pw, ph = self._phys_size_

        radius = ph // 2

        if self._fill_space:
            self._group = group = imple.ProgressBar(
                rx,
                ry,
                pw,
                ph,
                progress=0.0,
                stroke=1,
                bar_color=self._palette.fill_color,
            )
        else:
            self._group = group = imple.ProgressBar(
                x=rx + radius,
                y=ry + ph // 2 - 6,
                width=pw - 2 * radius,
                height=12,
                progress=0.0,
                stroke=1,
                bar_color=self._palette.fill_color,
            )

        progress_state = self._progress_state
        # if isinstance(progress_state, State):
        progress_state._register_handler_(self, self._update_progress)
        self._update_progress(progress_state.value())
        # else:
        #     self._update_progress(self._progress_state)
        super()._build_()

    def _demolish_(self):
        if isinstance(self._progress_state, State):
            self._progress_state._deregister_handler_(self)
        super()._demolish_()

    def _update_progress(self, value):
        if self.isbuilt():
            self._group.progress = clip(0.0, value, 1.0)
