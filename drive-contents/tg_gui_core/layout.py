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

from .base import Container, Widget
from .layout_classes import *


class Layout(Container):
    def _render_(self):
        Widget._render_(self)
        for wid in self._nested_:
            if wid.isplaced():
                wid._render_()
        self._screen_.on_container_render(self)

    def _derender_(self):
        for wid in self._nested_:
            if wid.isplaced():
                wid._derender_()
        Widget._derender_(self)
        self._screen_.on_container_derender(self)

    def _place_(self, coord, dims):
        Widget._place_(self, coord, dims)

        layoutcls = self._screen_.layout_class

        if layoutcls is LayoutCls.wearable:
            if hasattr(self, "_wearable_"):
                self._wearable_()
            else:
                self._any_()
        elif isinstance(layoutcls, LayoutCls.mobile):
            if hasattr(self, "_mobile_"):
                self._mobile_(layoutcls.width, layoutcls.height)
            else:
                self._any_()
        else:
            raise ValueError(
                f"unknown LayoutCls variant or object, {type(layoutcls)}"
            )

        self._screen_.on_container_place(self)

    def _pickup_(self):
        self._screen_.on_container_pickup(self)
        for wid in self._nested_:
            wid._pickup_()
        Widget._pickup_(self)

    def _relayout_proto_(self):
        self._layout_()
        self._unlayout_()

    def _any_(self):
        raise NotImplementedError(
            f"layout methods must be written for subclasses of layout"
        )

    # def _wearable_(self):
    #     self._any_()
    #
    # def _mobile_(self, width: SizeClass, height: SizeClass):
    #     self._any_()
