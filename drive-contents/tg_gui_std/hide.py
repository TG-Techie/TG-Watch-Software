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
from tg_gui_core.base import Container, Widget
from tg_gui_core.stateful import State


class Hide(Container):
    def __init__(self, subject, *, when):
        assert isinstance(subject, Widget)
        assert isinstance(when, State)

        super().__init__()

        self._subject = subject
        self._when = when

    def _on_nest_(self):
        self._nest_(self._subject)

    # bypass Container's as the implenation is lower level
    _format_ = Widget._format_

    def _form_(self, dim_spec):
        self._subject._form_(dim_spec)
        super(Container, self)._form_(self._subject.dims)

    def _place_(self, pos_spec):
        super()._place_(pos_spec)
        self._subject._place_((0, 0))

    def _build_(self):
        super(Container, self)._build_()
        self._subject._build_()
        self._screen_.on_container_build(self)

        self._when._register_handler_(self, self._update_visbility)

    def _demolish_(self):
        self._when._deregister_handler_(self)
        super()._demolish_()

    def _show_(self):
        super(Container, self)._show_()
        self._update_visbility(self._when.value(self))
        self._screen_.on_container_show(self)

    def _update_visbility(self, hide_it):
        if self.isshowing():
            subject = self._subject
            is_showing = subject.isshowing()
            show_it = not hide_it
            if show_it and not is_showing:  # should and can show it
                subject._show_()
            elif not show_it and is_showing:  # should and can hide it
                subject._hide_()
            else:
                assert show_it == is_showing, f"{show_it} should be {is_showing}"
