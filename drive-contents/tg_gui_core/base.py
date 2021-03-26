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

from ._shared import *
from .position_specifiers import *
from .dimension_specifiers import *


class NestingError(RuntimeError):
    pass


class PlacementError(RuntimeError):
    pass


class RenderError(RuntimeError):
    pass


def singleinstance(cls):
    return cls()


class InheritedAttribute:
    def __init__(self, attrname, initial):
        self._attrname = attrname
        self._priv_attrname = "_inherited_" + attrname + "_attr_"
        self._initial = initial

    def __repr__(self):
        return f"<InheritedAttribute: .{self._attrname}>"

    def __get__(self, owner, ownertype):
        privname = self._priv_attrname
        assert hasattr(owner, privname), (
            f"``{owner}.{self._attrname}`` attribute not initialized, "
            + f"inherited `{type(owner).__name__}.{self._attrname}` attributes must be "
            + f"initialized to the inital `{self._initial}` or some other value"
        )
        privattr = getattr(owner, privname)
        if privattr is not self._initial:  # normal get behavior
            return privattr
        else:  # get the inherited attribute
            heirattr = getattr(owner._superior_, self._attrname)
            if heirattr is not self._initial:
                # init the inherited attr
                setattr(owner, privname, heirattr)
            return heirattr

    def __set__(self, owner, value):
        setattr(owner, self._priv_attrname, value)


class Screen:
    def __init__(
        self,
        *,
        min_visible,
        min_size,
        border,
        min_margin,
        theme,
        layout_class,
    ):
        self._id_ = uid()

        self.layout_class = layout_class

        self.min_visible = min_visible
        self.min_size = min_size
        self.border = border
        self.min_margin = min_margin

        self.theme = theme

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

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


class Widget:  # protocol

    _screen_ = InheritedAttribute("_screen_", None)

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

    def isbuilt(self):
        return self.isplaced() and self._screen_.widget_is_built(self)

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

    def __call__(self, pos_spec, dim_spec):
        self._form_(dim_spec)
        self._place_(pos_spec)
        return self

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
            # self._screen_ = superior._screen_
        elif current is superior:  # if double nesting in same thing
            print(
                f"WARNING: {self} already nested in {current}, "
                + "double nesting in the same widget is not advisable"
            )
        else:
            raise ValueError(
                f"{self} already nested in {current}, " + f"cannot nest in {superior}"
            )

        self._screen_.on_widget_nest_in(self)
        # self._on_nest_()

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
            width = width._resolve_specified_(self)
        if isinstance(height, DimensionSpecifier):
            height = height._resolve_specified_(self)

        margin = self._margin_spec
        if margin is None:
            margin = self._screen_.min_margin

        if isinstance(margin, DimensionSpecifier):
            margin = margin._resolve_specified_(self)

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
        assert not self.isbuilt()
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
