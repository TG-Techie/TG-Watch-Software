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
from .layout_classes import *
from .position_specifiers import *
from .dimension_specifiers import *

# TODO: make widgets return DimSpecs and PosSpecs when dims and coords are not set yet


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


align = ConstantGroup("align", ("leading", "center", "trailing"))


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
        r = round(255 * r ** 1.2)
        g = round(255 * g ** 1.2)
        b = round(255 * b ** 1.2)
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
        layout_class: LayoutCls,
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
    def on_widget_nest_in(self, wid: "Widget"):
        pass

    def on_widget_unnest_from(self, wid: "Widget"):
        pass

    def on_widget_render(self, wid: "Widget"):
        pass

    def on_widget_derender(self, wid: "Widget"):
        pass

    def on_container_place(self, wid: "Widget"):
        pass

    def on_container_pickup(self, wid: "Widget"):
        pass

    def on_container_render(_, widget: "Widget"):
        pass

    def on_container_derender(_, widget: "Widget"):
        pass


class Widget:

    _next_id = 0

    def __init__(self, *, margin=None):  # TODO: should use nest or superior kwarg?
        global Widget
        self._id_ = uid()

        self._superior_ = None  # type: Optional[superior]
        self._screen_ = None

        self._placement_ = None  # type: Optional[Tuple[x, y, width, height]]
        self._rel_placement_ = None
        self._phys_coord = None

        self._margin_ = margin

        self._rendered_ = False

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def isnested(self):
        return self._superior_ is not None

    def isplaced(self):
        return self._placement_ is not None  # and self.isnested()

    def isrendered(self):
        return self._rendered_

    def __get__(self, owner, ownertype=None):
        """
        Widgets act as their own descriptors, this allows them to auto nest into layouts.
        """
        if not self.isnested():
            owner._nest_(self)
        return self

    # placement sugar, still in flux
    def __call__(self, pos_spec, dim_spec):
        self._size_(dim_spec)
        self._place_(pos_spec)
        return self

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

    def _unnest_from_(self, superior):
        """
        Called by superiors to un-link the (now-ex) subordinate from the superior
        """
        if self._superior_ is superior:
            # platform tie-in
            self._screen_.on_widget_unnest_from(self)
            # clear out data
            self._screen_ = None
            self._superior_ = None
        else:
            raise RuntimeError(
                f"cannot unnest {self} from {superior}, nested in {self._superior_}"
            )

    def _on_nest_(self):
        pass

    def _on_unnest_(self):
        pass

    # auto nesting, only for layouts, etc
    # list, zstacks, and others will need to manually nest in their __init__s
    def __get__(self, owner, ownertype=None):
        if not self.isnested():
            owner._nest_(self)
        return self

    def _size_(self, dim_spec):
        assert self.isnested(), f"{self} must be nested to size it, it's not"

        # format dims
        width, height = dim_spec
        if isinstance(width, DimensionSpecifier):
            width = width._calc_dim_(self)
        if isinstance(height, DimensionSpecifier):
            height = height._calc_dim_(self)

        # make sure PositionSpecifiers have access to width/height
        self._placement_ = (None, None, width, height)
        # TODO: shange this to spearate pos and size

        # get margin
        mar = self._margin_
        if mar is None:
            self._margin_ = mar = self._screen_.default.margin

    def _place_(self, pos_spec):
        assert self.issized(), f"{self} must be sized to place it, it's not"

        # format coord
        if isinstance(pos_spec, PositionSpecifier):
            x, y = pos_spec._calc_coord_(self)
        else:
            assert isinstance(pos_spec, tuple)
            x, y = pos_spec

        FUCK(TODO, "clean this up and separate it")

        if isinstance(x, PositionSpecifier):
            x = x._calc_x_(self)
        if isinstance(y, PositionSpecifier):
            y = y._calc_y_(self)

        if self._superior_ is None and (x < 0 or y < 0):
            raise ValueError(f"right aligned coord cannot be used with root widgets")

        # adjust
        if x < 0:
            x = self._superior_.width - width + 1 + x
        if y < 0:
            y = self._superior_.height - height + 1 + y

        # save
        self._placement_ = placement = x, y, w, h = (x, y, width, height)

        # calc relative placement
        rel = self._rel_placement_
        self._rel_placement_ = rel_placement = (
            mar + x,
            mar + y,
            w - (2 * mar),
            h - (2 * mar),
        )
        rx, ry, rw, rh = rel_placement

        # calc absolute physical placement
        supx, supy = self._superior_._phys_coord_
        self._phys_coord_ = (supx + rx, supy + ry)
        self._phys_end_coord = (supx + rx + rw, supy + ry + rh)

        if was_on_screen:
            self._render_()

    def _pickup_(self):
        assert not self.isrendered()
        assert self.isplaced()
        # only containers need to worry about when to cover vs replace
        self._placement_ = None
        self._rel_placement_ = None
        self._phys_coord_ = None

    def _render_(self):
        assert self.isplaced()
        self._rendered_ = True
        screen = self._screen_
        screen.on_widget_render(self)  # platform tie-in

    def _derender_(self):
        assert self.isrendered()
        self._screen_.on_widget_derender(self)  # platform tie-in
        self._rendered_ = False

    def __del__(self):
        # remove double links
        self._superior_ = None
        self._screen_ = None
        # remove placement cache
        self._placement_ = None
        self._rel_placement_ = None
        self._phys_coord = None

    # TODO: Change this to spearate placemtn into size and position ?
    # coordinates and dimension getters
    coord = property(lambda self: self._placement_[0:2])
    _rel_coord_ = property(lambda self: self._rel_placement_[0:2])
    #!!  _phys_coord_ uses raw exposed tuple for

    dims = property(lambda self: self._placement_[2:4])
    _phys_dims_ = property(lambda self: self._rel_placement_[2:4])

    x = property(lambda self: self._placement_[0])
    _rel_x_ = property(lambda self: self._rel_placement_[0])
    _phys_x_ = property(lambda self: self._phys_coord_[0])

    y = property(lambda self: self._placement_[1])
    _rel_y_ = property(lambda self: self._rel_placement_[1])
    _phys_y_ = property(lambda self: self._phys_coord_[1])

    width = property(lambda self: self._placement_[2])
    _phys_width_ = property(lambda self: self._rel_placement_[2])

    height = property(lambda self: self._placement_[3])
    _phys_height_ = property(lambda self: self._rel_placement_[3])


class Container(Widget):
    def __init__(self):
        global Widget

        super().__init__(margin=0)

        self._nested_ = []

        self._setup_()

    @property
    def fill(self):
        return ((0, 0), self.dims)

    def _setup_(self):
        pass  # used for setting up of reuables contianers, "compound widgets"

    def _nest_(self, widget: Widget):
        if widget not in self._nested_:
            self._nested_.append(widget)
            widget._nest_in_(self)

    def _unnest_(self, widget: Widget):
        if widget in self._nested_:
            widget._unnest_from_(self)
        while widget in self._nested_:
            self._nested_.remove(widget)

    def _place_(self, coord, dims):
        super()._place_(coord, dims)
        self._place_nested_()
        self._screen_.on_container_place(self)

    def _pickup_(self, visual):
        self._screen_.on_container_pickup(self)
        self._pickup_nested_()
        super()._pickup_(visual)

    def _render_(self):
        super()._render_()
        self._render_nested_()

    def _derender_(self):
        super()._derender_()
        self._derender_nested_()

    def _render_nested_(self):
        raise NotImplementedError(
            f"{type(self).__name__}._render_nested_ not implemented"
        )

    def _derender_nested_(self):
        raise NotImplementedError(
            f"{type(self).__name__}._derender_nested_ not implemented"
        )

    def _place_nested_(self):
        raise NotImplementedError(
            f"{type(self).__name__}._place_nested_ not implemented"
        )

    def _pickup_nested_(self):
        raise NotImplementedError(
            f"{type(self).__name__}._pickup_nested_ not implemented"
        )

    def __del__(self):
        super().__del__()
        nested = self._nested_
        while len(nested):
            del nested[0]
