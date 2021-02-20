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

import gc
from .base import *


class RootWrapper(Container):
    def __init__(self, *, screen: Screen, size, startup=False, **kwargs):
        assert len(size) == 2, f"expected two dimensions found, {size}"

        Widget.__init__(self)

        self._superior_ = None
        self._screen_ = screen

        self._nested_ = []

        self._screen_ = screen
        self._inst_kwargs = kwargs
        self._size = size
        self._startup = startup

    def __call__(self, cls):
        self._root_wid_inst = root_wid_inst = cls()
        self._nest_(root_wid_inst)
        return root_wid_inst

    @property
    def _phys_coord_(self):
        return (0, 0)

    @property
    def wrapped(self):
        return self._root_wid_inst

    def _place_(self, coord: int, dims: int):
        raise NotImplementedError()
        assert dims > (0, 0), f"root's dims must be > (0, 0), found {dims}"

        if self._superior_ is None and (x < 0 or y < 0):
            raise ValueError(f"right aligned coord cannot be used with root widgets")

        was_on_screen = self.isrendered()
        if was_on_screen:
            self._derender_()

        self._placement_ = self._rel_placement_ = (0, 0) + dims
        self._abs_coord = (0, 0)

        self._place_nested_()

        if was_on_screen:
            self._render_()

    def _pickup_(self):
        self._pickup_nested_()
        Widget._pickup_(self)

    def _render_(self):
        self._rendered_ = True
        self._render_nested_()

    def _derender_(self):
        self._rendered_ = False
        self._derender_nested_()

    def _place_nested_(self):
        self._root_wid_inst(*self.fill)

    def _pickup_nested_(self):
        self._root_wid_inst._pickup_()

    def _render_nested_(self):
        self._root_wid_inst._render_()

    def _derender_nested_(self):
        self._root_wid_inst._derender_()

    def isnested(self):
        raise TypeError(f"roots cannot be nested")

    def _std_startup_(self):
        self._nest_(self._root_wid_inst)
        gc.collect()
        self._place_((0, 0), self._size)
        gc.collect()
        self._render_()
        gc.collect()

    # possible future api
    def _proto_change_layoutcls(self, layoutcls):
        raise NotImplementedError()
