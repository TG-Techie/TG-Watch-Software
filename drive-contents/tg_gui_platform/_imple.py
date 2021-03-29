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
import displayio

# import vectorio
import terminalio
import math

from tg_gui_core import font, align

from adafruit_display_text.label import Label as Dispio_Label

# from adafruit_progressbar import ProgressBar

font_to_platform_size = {
    font.giant: 7,
    font.largetitle: 4,
    font.title: 3,
    font.heading: 2,
    font.subheading: 2,
    font.label: 2,
    font.body: 2,
    font.footnote: 1,
}

Group = displayio.Group


class SimpleRoundRect(displayio.TileGrid):
    # pylint: disable=too-many-arguments
    """A round-corner rectangle with lower memory usage than RoundRect. All the corners
        have the same radius and no outline.

    :param x: The x-position of the top left corner.
    :param y: The y-position of the top left corner.
    :param width: The width of the rounded-corner rectangle.
    :param height: The height of the rounded-corner rectangle.
    :param radius: The radius of the rounded corner.
    :param fill: The color to fill the rounded-corner rectangle. Can be a hex value for a color or
                 ``None`` for transparent.
    """

    def __init__(self, x, y, width, height, radius=0, fill=0xFF0000):

        # the palette and shpae can only be stored after __init__
        palette = displayio.Palette(2)
        shape = displayio.Shape(
            width,
            height,
            # mirror_x is False due to a core displayio bug
            mirror_x=False,
            mirror_y=True,
        )
        super().__init__(shape, pixel_shader=palette, x=x, y=y)

        # configure the color and palette
        palette.make_transparent(0)
        palette[1] = fill

        # these them so fill can be adjusted later
        self._palette = palette
        self._shape = shape

        # clamp a too large radius to the max allowed
        radius = min(radius, round(width / 2), round(height / 2))

        # calculate and apply the radius row by row
        rsqrd = radius ** 2
        for row_offset in range(0, radius):
            left_indent = radius - int(math.sqrt(rsqrd - (row_offset - radius) ** 2))
            right_indent = width - left_indent - 1

            shape.set_boundary(
                row_offset,
                left_indent,
                right_indent,
            )

        # store for read only access later
        self._radius = radius
        self._width = width
        self._height = height

    @property
    def fill(self):
        return self._palette[1]

    @fill.setter
    def fill(self, value):
        self._palette[1] = value

    # @property
    # def width(self):
    #     return self._width
    #
    # @property
    # def height(self):
    #     return self._height
    #
    # @property
    # def radius(self):
    #     return self._radius
    #


class Label(displayio.Group):
    def __init__(
        self,
        *,
        coord,
        dims,
        alignment=align.center,
        text="<text>",
        color=0xFFFFFF,
        scale=1,
    ):
        super().__init__(
            max_size=1,
            x=coord[0],
            y=coord[1],
        )

        self._coord = coord
        self._dims = dims

        self._text = text
        self._scale = scale
        self._color = color
        self._alignment = alignment

        self.append(displayio.Group())
        # self._new_native()
        self._native = Dispio_Label(terminalio.FONT, text=" ")

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._native.color = value
        self._color = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):

        if len(value) < len(self._text):
            self._text = value
            self._native._update_text(value)
            self._position_native()
        else:
            self.pop(0)
            self._text = value

            # make new native display group item
            self._native = native = Dispio_Label(
                terminalio.FONT,
                text=self._text,
                scale=self._scale,
                color=self._color,
            )
            self._position_native()
            # swap out for the new one (relies on being the last more item)

            self.append(native)

    def _position_native(self):
        global align
        width, height = self._dims
        native = self._native
        alignment = self._alignment
        native.y = height // 2
        if alignment is align.center:
            native.x = (width // 2) - (self._scale * native.bounding_box[2] // 2)
        elif alignment is align.leading:
            native.x = 0
        elif alignment is align.trailing:
            native.x = width - (self._scale * native.bounding_box[2])
        else:
            raise ValueError(
                f"{alignment} is not a valid value, must be `align.center`, `align.leading`, or `align.trailing`"
            )


class ProgressBar(displayio.TileGrid):
    def __init__(self, pos, dims, *, bar_color, progress=0.0):
        x, y = pos
        width, height = dims
        palette = displayio.Palette(2)
        shape = displayio.Shape(
            width,
            height,
            # mirror_x is False due to a core displayio bug
            mirror_x=False,
            mirror_y=True,
        )

        super().__init__(shape, pixel_shader=palette, x=x, y=y)

        self._dims = dims
        self._palette = palette
        self._shape = shape

        palette[1] = bar_color

        self.progress = progress

    bar_color = property(lambda self: self._palette[1])

    @bar_color.setter
    def bar_color(self, value):
        self._palette[1] = value

    def set_progress(self, value):
        self._progress = value
        dist = self._dims[0] - 1 if value == 1.0 else int(self._dims[0] * value)
        shape = self._shape
        for y in range(self._dims[1] // 2):
            shape.set_boundary(y, 0, dist)
