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
from tg_gui_core import Container, centerto


class _SplitContainer(Container):
    def __init__(self, *widgets, **kwargs):
        self._widgets = widgets
        super().__init__(**kwargs)

    def _on_nest_(self):
        for widget in self._widgets:
            if widget is not None:
                self._nest_(widget)

    def _build_(self):
        super(Container, self)._build_()
        for widget in self._nested_:
            if widget.isplaced():
                widget._build_()
        self._screen_.on_container_build(self)

    def _show_(self):
        super(Container, self)._show_()

        for widget in self._nested_:
            if widget.isbuilt():
                widget._show_()

        self._screen_.on_container_show(self)


class HSplit(_SplitContainer):
    def _form_(self, dim_spec):
        super(Container, self)._form_(dim_spec)

        sub_height = self.height
        sub_width = self.width // len(self._widgets)

        sub_size = (sub_width, sub_height)

        for widget in self._nested_:

            widget._form_(
                sub_size,
            )

    def _place_(self, pos_spec):
        super(Container, self)._place_(pos_spec)

        sub_width = self.width // len(self._widgets)
        sub_y = self.height // 2
        sub_x_offset = sub_width // 2

        for row, widget in enumerate(self._widgets):
            if widget is not None:
                widget._place_(
                    centerto(sub_width * row + sub_x_offset, sub_y),
                )
        self._widgets = None


class VSplit(_SplitContainer):
    def _form_(self, dim_spec):
        super(Container, self)._form_(dim_spec)

        sub_width = self.width
        sub_height = self.height // len(self._widgets)

        sub_size = (sub_width, sub_height)

        for widget in self._nested_:

            widget._form_(
                sub_size,
            )

    def _place_(self, pos_spec):
        super(Container, self)._place_(pos_spec)

        sub_height = self.height // len(self._widgets)
        sub_x = self.width // 2
        sub_y_offset = sub_height // 2

        for row, widget in enumerate(self._widgets):
            if widget is not None:
                widget._place_(
                    centerto(sub_x, sub_height * row + sub_y_offset),
                )
        self._widgets = None
