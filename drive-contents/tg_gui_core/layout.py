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

from .base import Container, Widget, layout_class

_layout_class_to_method_name = {
    layout_class.wearable: "_wearable_",
    layout_class.portrait: "_portrait_",
    layout_class.landscape: "_landscape_",
    layout_class.desktop: "_desktop_",
    layout_class.custom: "_custom_",
}


class Layout(Container):
    def _format_(self, pos_spec, dim_spec):
        global _layout_class_to_method_name

        super(Container, self)._format_(pos_spec, dim_spec)

        layoutcls = self._screen_.layout_class

        for cls, method_name in _layout_class_to_method_name.items():
            if layoutcls is cls:
                if hasattr(self, method_name):
                    getattr(self, method_name)()
                else:
                    self._any_()
                break
        else:
            raise RuntimeError(
                f"{layoutcls} is not a valid layout class, no corresonding method"
            )

    def _build_(self):
        super(Container, self)._build_()
        self._screen_.on_container_build(self)
        for widget in self._nested_:
            if widget.isformated():
                widget._build_()

    def _show_(self):
        super(Container, self)._show_()
        for widget in self._nested_:
            widget._show_()

    def _any_(self):
        raise NotImplementedError(
            f"layout methods must be written for subclasses of layout"
        )
