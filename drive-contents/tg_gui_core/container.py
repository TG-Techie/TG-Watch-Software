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

from ._shared import ConstantGroup
from .base import Widget, InheritedAttribute, NestingError
from .specifiers import SpecifierReference, AttributeSpecifier

# attribute specifier constructors for declared containers

layout_class = ConstantGroup(
    "size_class",
    (
        "wearable",
        "portrait",
        "landscape",
        "desktop",
        "custom",
    ),
)


def _find_declared_superior(attr_spec, widget):
    assert isinstance(widget, Widget)
    container = widget if isinstance(widget, Container) else widget._superior_
    while not container._decalrable_:
        prev = container
        container = container._superior_
        if container is None:
            raise NestingError(f"{widget} not used in a declared container")
    return container


self = SpecifierReference("self", _find_declared_superior)
superior = self._superior_ = AttributeSpecifier(self, "_superior_")


def declarable(cls):
    """
    dcecorator to mark that a contianer is declarable (like layout or Pages).
    this is used for attr_specs to finf the referenced self in `self.blah`
    """
    assert isinstance(cls, type), f"can only decorate classes"
    assert issubclass(
        cls, Container
    ), f"{cls} does not subclass Container, it must to be @declarable"
    cls._decalrable_ = True
    return cls


class Container(Widget):  # protocol
    _decalrable_ = False

    _theme_ = InheritedAttribute("_theme_", None)

    def __init__(self):
        global Widget

        super().__init__(margin=0)

        self._nested_ = []
        self._theme_ = None

    def _nest_(self, widget: Widget):
        if widget not in self._nested_:
            self._nested_.append(widget)
            widget._nest_in_(self)

    def _unnest_(self, widget: Widget):
        if widget in self._nested_:
            widget._unnest_from_(self)
        while widget in self._nested_:
            self._nested_.remove(widget)

    def _form_(self, dim_spec):
        raise NotImplementedError(
            f"{type(self).__name__}._form_(...) not implemented,"
            + " see tg_gui_core/base.py for the template"
        )
        # Template:
        # container subcless specific form code here
        super(Container, self)._form_(dim_spec)

    def _deform_(self):
        for widget in self._nested_:
            if widget.isformed():
                widget._deform_()
        super()._deform_()

    def _place_(self, pos_spec):
        raise NotImplementedError(
            f"{type(self).__name__}._place_(...) not implemented,"
            + " see tg_gui_core/base.py for the template"
        )
        # Template:
        super(Container, self)._place_(pos_spec)
        # container subcless specific place code here

    def _pickup_(self):
        for widget in self._nested_:
            if widget.isplaced():
                widget._pickup_()
        super()._deform_()

    def _build_(self):
        raise NotImplementedError(
            f"{type(self).__name__}._build_() not implemented,"
            + " see tg_gui_core/base.py for the template"
        )
        # Template:
        super(Container, self)._build_()
        # container subcless specific build code here
        self._screen_.on_container_build(self)

    def _demolish_(self):
        for widget in self._nested_:
            if widget.isbuilt():
                widget._demolish_()
        super()._demolish_()
        self._screen_.on_container_demolish(self)

    def _show_(self):
        raise NotImplementedError(
            f"{type(self).__name__}._show_() not implemented,"
            + " see tg_gui_core/base.py for the template"
        )
        # Tempalte:
        super(Container, self)._show_()
        # container subcless specific show code here
        self._screen_.on_container_show(self)

    def _hide_(self):
        for widget in self._nested_:
            if widget.isshowing():
                widget._hide_()
        super()._hide_()
        self._screen_.on_container_hide(self)

    def __del__(self):
        nested = self._nested_
        while len(nested):
            del nested[0]
        super().__del__()
