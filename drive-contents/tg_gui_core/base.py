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


import random as _random

from .constant_groups import *
from .position_specifiers import *
from .dimension_specifiers import *


class NestingError(RuntimeError):
    pass


class PlacementError(RuntimeError):
    pass


class RenderError(RuntimeError):
    pass


_next_id = _random.randint(0, 11)


def uid():
    global _next_id
    id = _next_id
    _next_id += 1
    return id


def clip(lower, value, upper):
    return min(max(lower, value), upper)


def singleinstance(cls):
    return cls()


align = ConstantGroup(
    "align",
    (
        "leading",
        "center",
        "trailing",
    ),
)

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


class color:
    # TODO: consider make ready only using proerties and lambdas vs performance
    _clear = None  # tentative
    red = 0xFF0000
    orange = 0xFFA500
    yellow = 0xFFFF00
    green = 0x00FF00
    blue = 0x0000FF
    purple = 0xCC8899

    white = 0xFFFFFF
    lightgray = 0xC4C4C4
    gray = 0x909090
    darkgray = 0x606060
    black = 0x000000

    def fromfloats(r, g, b):
        r = round(255 * r ** 1.125)
        g = round(255 * g ** 1.125)
        b = round(255 * b ** 1.125)
        return (r << 16) | (g << 8) | (b << 0)


class Palette:
    def __init__(
        self,
        *,
        fill_color,
        text_color,
        selected_text,
        selected_fill,
        backfill,
    ):
        self.fill_color = fill_color
        self.selected_fill = selected_fill
        self.text_color = text_color
        self.selected_text = selected_text
        self.backfill = backfill


class Palettes:
    def __init__(self, *, primary, secondary):
        self.primary = primary
        self.secondary = secondary


class Defaults:
    def __init__(
        self,
        *,
        margin,
        radius,
        font_size,
        _fill_color_,
        _selected_fill_,
        _text_color_,
        _selected_text_,
    ):
        self.margin = margin
        self.radius = radius
        self.font_size = font_size

        self._fill_color_ = _fill_color_
        self._selected_fill_ = _selected_fill_
        self._text_color_ = _text_color_
        self._selected_text_ = _selected_text_


class Screen:
    def __init__(
        self,
        *,
        min_size,
        palettes: Palettes,
        default: Defaults,
        layout_class: Constant,
        outer: "Screen" = None,
    ):
        self._id_ = uid()
        self.default = default
        self.layout_class = layout_class
        self.outer = outer

        self.min_size = min_size
        self.palettes = palettes

        self._pointables_ = []
        self._pressables_ = []
        self._altpressables_ = []

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def __getattr__(self, name):
        if self.outer is not None:
            try:
                return getattr(self.outer, name)
            except:
                pass
        raise AttributeError(f"unable to get attribute `.{name}`")

    # platform tie-in functions

    def on_widget_nest_in(_, wid: "Widget"):
        raise NotImplementedError

    def on_widget_unnest_from(_, wid: "Widget"):
        raise NotImplementedError

    def on_widget_build(_, wid: "Widget"):
        raise NotImplementedError

    def on_widget_demolish(_, wid: "Widget"):
        raise NotImplementedError

    def on_widget_show(_, wid: "Widget"):
        raise NotImplementedError

    def on_widget_hide(_, wid: "Widget"):
        raise NotImplementedError

    # container tie-ins

    def on_container_build(_, wid: "Widget"):
        raise NotImplementedError

    def on_container_demolish(_, wid: "Widget"):
        raise NotImplementedError

    def on_container_show(_, widget: "Widget"):
        raise NotImplementedError

    def on_container_hide(_, widget: "Widget"):
        raise NotImplementedError

    def widget_is_built(_, widget: "Widget"):
        raise NotImplementedError


class Widget:
    def __init__(self, *, margin=None):
        global Widget
        self._id_ = uid()

        self._superior_ = None
        self._screen_ = None

        self._size_ = None
        self._phys_size_ = None

        self._coord_ = None
        self._rel_coord_ = None
        self._phys_coord_ = None

        self._is_shown = False

        self._margin_spec = margin

    dims = property(lambda self: self._size_)
    width = property(lambda self: self._size_[0])
    height = property(lambda self: self._size_[1])

    coord = property(lambda self: self._coord_)
    x = property(lambda self: self._coord_[0])
    y = property(lambda self: self._coord_[1])

    # internal protocols
    # ._phys_size_
    # ._size_
    # ._coord_
    # ._rel_coord_
    # ._phys_coord_
    # ._phys_end_coord_

    def isnested(self):
        return self._superior_ is not None

    def isformed(self):
        return self._size_ is not None

    def isplaced(self):
        return self._coord_ is not None  # and self.isnested()

    isformated = isplaced

    def isbuilt(self):
        return self.isformated() and self._screen_.widget_is_built(self)

    def isshowing(self):
        return self._is_shown

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def __get__(self, owner, ownertype=None):
        """
        Widgets act as their own descriptors, this allows them to auto nest into layouts.
        """
        if not self.isnested():
            owner._nest_(self)
        return self

    # placement sugar, still in flux (keep near _format_)
    def __call__(self, pos_spec, dim_spec):
        self._format_(pos_spec, dim_spec)
        return self

    def _format_(self, pos_spec, dim_spec):
        self._form_(dim_spec)
        self._place_(pos_spec)

    def _deformat_(self):
        self._pickup_()
        self._deform_()

    def _build_(self):
        assert self.isplaced()
        self._screen_.on_widget_build(self)  # platform tie-in

    def _demolish_(self):
        assert self.isbuilt()
        self._screen_.on_widget_demolish(self)  # platform tie-in

    def _show_(self):
        assert self.isnested()
        self._is_shown = True
        self._screen_.on_widget_show(self)

    def _hide_(self):
        assert self.isshowing()
        self._is_shown = False
        self._screen_.on_widget_hide(self)

    def _nest_in_(self, superior):
        """
        Called by the superior of a widget (self) to link the widget as it's subordinate.
        """
        # nesting is permanent, this should be called by the parent widget once
        current = self._superior_
        if current is None:

            self._superior_ = superior
            self._screen_ = superior._screen_
            self._screen_.on_widget_nest_in(self)
        elif current is superior:  # if double nesting in same thing
            print(
                f"WARNING: {self} already nested in {current}, "
                + "double nesting in the same widget is not advisable"
            )
        else:
            raise ValueError(
                f"{self} already nested in {current}, " + f"cannot nest in {superior}"
            )

        self._on_nest_()

    def _unnest_from_(self, superior=None):
        """
        Called by superiors to un-link the (now-ex) subordinate from the superior
        """
        if superior is None:
            superior = self._superior_
        if superior is self._superior_:
            # platform tie-in
            self._screen_.on_widget_unnest_from(self)
            # clear out data
            self._screen_ = None
            self._superior_ = None
        else:
            raise RuntimeError(
                f"cannot unnest {self} from {superior}, it is nested in {self._superior_}"
            )

    def _form_(self, dim_spec):
        assert self.isnested(), f"{self} must be nested to size it, it's not"
        assert not self.isformed(), f"{self} is already formed"

        # format dims
        width, height = dim_spec
        if isinstance(width, DimensionSpecifier):
            width = width._calc_dim_(self)
        if isinstance(height, DimensionSpecifier):
            height = height._calc_dim_(self)

        margin_spec = self._margin_spec
        if margin_spec is None:
            margin_spec = self._screen_.default.margin

        if isinstance(margin_spec, DimensionSpecifier):
            margin = margin_spec._calc_dim_(self)
        else:
            margin = margin_spec

        self._margin_ = margin
        self._size_ = (width, height)
        self._phys_size_ = (width - margin * 2, height - margin * 2)

    def _deform_(self):
        assert self.isformed()
        self._margin_ = None
        self._size_ = None
        self._phys_size_ = None

    def _place_(self, pos_spec):
        assert self.isformed(), f"{self} must be sized to place it, it's not"
        assert not self.isplaced(), f"{self} already placed"

        # format coord
        if isinstance(pos_spec, PositionSpecifier):
            x, y = pos_spec._calc_coord_(self)
        else:
            assert isinstance(pos_spec, tuple)
            x, y = pos_spec

        if isinstance(x, PositionSpecifier):
            x = x._calc_x_(self)
        if isinstance(y, PositionSpecifier):
            y = y._calc_y_(self)

        # for negative numbers adjust to right aligned
        if x < 0:
            x = self._superior_.width - self.width + 1 + x
        if y < 0:
            y = self._superior_.height - self.height + 1 + y

        # calc and store the placements
        margin = self._margin_
        spr_x, spr_y = self._superior_._phys_coord_

        self._coord_ = (x, y)
        self._rel_coord_ = rx, ry = (x + margin, y + margin)
        self._phys_coord_ = px, py = (spr_x + rx, spr_y + ry)

        pw, ph = self._phys_size_
        self._phys_end_coord_ = (px + pw, py + ph)

    def _pickup_(self):
        assert not self.isrendered()
        assert self.isplaced()
        # only containers need to worry about when to cover vs replace
        self._coord_ = None
        self._rel_coord_ = None
        self._phys_coord_ = None
        self._phys_end_coord_ = None

    def _on_nest_(self):
        pass

    def _on_unnest_(self):
        pass

    def __del__(self):
        # deconstruct from current stage
        if self.isshowing():
            self._hide_()
        if self.isbuilt():
            self._demolish_()
        if self.isplaced():
            self._pickup_()
        if self.isformed():
            self._deform_()
        if self.isnested():
            self._superior_._unnest_(self)

        # remove double links
        self._superior_ = None
        self._screen_ = None
        # remove placement cache
        self._size_ = None
        self._phys_size_ = None
        self._coord_ = None
        self._rel_coord_ = None
        self._phys_coord_ = None


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


class Container(Widget):
    _decalrable_ = False

    def __init__(self):
        global Widget

        super().__init__(margin=0)

        self._nested_ = []

    @property
    def fill(self):
        return ((0, 0), self.dims)

    def _nest_(self, widget: Widget):
        if widget not in self._nested_:
            self._nested_.append(widget)
            widget._nest_in_(self)

    def _unnest_(self, widget: Widget):
        if widget in self._nested_:
            widget._unnest_from_(self)
        while widget in self._nested_:
            self._nested_.remove(widget)

    def _format_(self, pos_spec, dim_spec):
        raise NotImplementedError(
            f"{type(self).__name__}._format_(...) not implemented,"
            + " see tg_gui_core/base.py for the template"
        )
        # Template:
        # container subcless specific format code here
        super()._format_(pos_spec, dim_spec)

    def _deformat_(self, pos_spec, dim_spec):
        super()._deformat_(pos_spec, dim_spec)
        for widget in self._nested_:
            if widget.isformated():
                widget._deformat_()
        self._screen_.on_container_deformat(self)

    def _build_(self):
        raise NotImplementedError(
            f"{type(self).__name__}._build_() not implemented,"
            + " see tg_gui_core/base.py for the template"
        )
        # Template:
        super()._build_()
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
        super()._show_()
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
