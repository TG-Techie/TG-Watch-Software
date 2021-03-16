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
from ._shared import uid
from .container import Container


class Root(Container):
    def __init__(self, *, screen: Screen, size, **kwargs):
        assert len(size) == 2, f"expected two dimensions found, {size}"

        self._id_ = uid()

        # self._superior_ = None
        self._screen_ = screen

        self._size_ = size

        self._is_linked = False
        self._is_shown = False

        self._margin_ = 0  # it is a container after all

        self._inst_kwargs = kwargs
        self._nested_ = []
        self._wrapped_widget = None

    def __call__(self, cls):
        self._wrapped_widget = root_wid_inst = cls()
        self._nest_(root_wid_inst)
        return root_wid_inst

    # _size_ is raw, exposed
    _phys_size_ = property(lambda self: self._size_)

    # possibly make settable in the future
    _coord_ = property(lambda self: (0, 0))
    _rel_coord_ = property(lambda self: (0, 0))
    _phys_coord_ = property(lambda self: (0, 0))

    @property
    def _superior_(self):
        return None

    @property
    def wrapped(self):
        return self._wrapped_widget

    def isnested(self):
        # cannot be not nested sooooooo (thus it is always fufilling taht capability)
        return True

    def _std_startup_(self):
        # self does not need to be formated as it already has form and position
        self._form_(None)
        self._place_(None)
        gc.collect()
        self._build_()
        gc.collect()

        # finally
        # print(f"showing root {self}")
        self._show_()
        # print(f"shown")

    def _form_(self, check):
        assert check is None  # exists to ensure proper use
        # print(self, self._wrapped_widget)
        self._wrapped_widget._form_(self._size_)

    def _deform_(self):
        self._wrapped_widget._deform_()

    def _place_(self, check):
        assert check is None  # exists to ensure proper use
        # print(self, self._wrapped_widget)
        self._wrapped_widget._place_((0, 0))

    def _pickup_(self):
        self._wrapped_widget._pickup_()

    def _build_(self):
        self._screen_.on_widget_build(self)
        self._wrapped_widget._build_()
        self._screen_.on_container_build(self)

    def _demolish_(self):
        self._wrapped_widget._demolish_()
        self._screen_.on_widget_demolish(self)
        self._screen_.on_container_demolish(self)

    def _show_(self):
        self._is_shown = True
        self._wrapped_widget._show_()

    def _hide_(self):
        self._is_shown = False
        self._wrapped_widget._hide_()
