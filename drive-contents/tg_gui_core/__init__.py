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
    SubStyle,
    color,
    align,
    theme,
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
    SubTheme,
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
