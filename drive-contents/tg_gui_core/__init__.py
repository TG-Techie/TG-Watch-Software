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

# base classes and application environment
from .base import (
    Widget,
    singleinstance,
    NestingError,
    PlacementError,
    RenderError,
)

from .container import Container, self
from .layout import Layout
from .stateful import State, DerivedState
from ._shared import uid, clamp

from .theming import (
    Theme,
class Theme:
    _styles_ = {}

    @classmethod
    def _add_style(cls, stylekey, styletype):
        assert stylekey not in cls._styles_
        assert isinstance(styletype, type)
        assert issubclass(styletype, Style) and not issubclass(styletype, SubStyle)
        cls._styles_[stylekey] = styletype

    def __init__(
        self,
        *,
        margin,
        radius,
        plain: Palette,
        action: SubPalette,
        warning: SubPalette,
        alert: SubPalette,
        indicator: SubPalette,
        **kwargs,
    ):
        self._id_ = uid()
        self.plain = plain

        self.action = action
        action._base_palette_ = plain
        self.warning = warning
        warning._base_palette_ = plain
        self.alert = alert
        alert._base_palette_ = plain
        self.indicator = indicator
        indicator._base_palette_ = plain

        self.margin = margin
        self.radius = radius

        styles = self._styles_
        # here we use a widget_styles dict because it can be pre-allocated
        #    unlike setting attributes on self
        self._widget_styles = widget_styles = dict.fromkeys(styles)
        for stylename, stylecls in styles.items():
            widget_style = kwargs.pop(stylename, None)
            assert widget_style is not None, (
                f"{type(self)} expecting keyword argument '{stylename}' of "
                + f"type {stylecls}"
            )
            assert isinstance(widget_style, stylecls), (
                f"expecting argument of type {stylecls} for keyword "
                + f"argument '{stylename}', given {repr(widget_style)}"
            )
            widget_styles[stylename] = widget_style
        else:
            assert len(kwargs) == 0, (
                "unexpected keyword arguments "
                + f"{', '.join(repr(kw) for kw in kwargs)} passed to "
                + f"{type(self)}"
            )

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def __getattr__(self, name):
        # attr = self._widget_styles.get(name, None)
        if name in self._styles_:
            return self._widget_styles.get(name, None)
        else:
            raise AttributeError(f"{self} has not attribute `.{name}`")
    color,
    align,
    font,
    theme,
    palette,
)

from .position_specifiers import (
    PositionSpecifier,
    ConstantPosition,
    centerto,
    leftof,
    rightof,
    below,
    above,
    center,
    top,
    bottom,
    left,
    right,
)

from .dimension_specifiers import (
    DimensionSpecifier,
    DimensionExpression,
    DimensionExpressionConstructor,
    ratio,
    height,
    width,
)


# classes and fucntions for making widget calsses 'lib tools'
from .__init__ import *
from .base import Screen  # soon to be depricated
from .container import declarable, layout_class
from .root_widget import Root

from .theming import (
    StyledWidget,
    StyledAttribute,
    Palette,
    SubPalette,
    Style,
    styled,
)

from .specifiers import (
    SpecifierReference,
    Specifier,
    AttributeSpecifier,
    ForwardMethodCall,
)
