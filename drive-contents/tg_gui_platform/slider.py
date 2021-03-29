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

from tg_gui_core import State, StyledWidget, Style, StyledAttribute, styled, clamp
from . import _imple as imple


class SliderStyle(Style):
    _style_colors_ = ("bar", "knob_border", "knob")
    _style_elements_ = ("bar_thickness", "radius", "border_thickness")


@styled(slider_style=SliderStyle)
class Slider(StyledWidget):

    _radius = StyledAttribute("_radius", "radius")
    _bar_thickness = StyledAttribute("_bar_thickness", "bar_thickness")
    _border_thickness = StyledAttribute("_border_thickness", "border_thickness")

    def __init__(self, value, *, _debug=False, **kwargs):
        super().__init__(**kwargs)
        self._state = value  # the state object to update
        assert isinstance(value, State)

        self._debug = _debug

        self._start_coord = None
        self._started_in_limits = None
        self._selected = False
        self._radius = None
        self._bar_thickness = None
        # self._bar_thickness = None

    def _build_(self):
        super()._build_()

        screen = self._screen_
        style = self._style_

        sx, sy = self._coord_
        sw, sh = self._size_
        rx, ry = self._rel_coord_
        rw, rh = self._phys_size_

        knob_dim = min(rh, screen.min_size)

        self._group = group = imple.Group(
            x=rx, y=ry, max_size=(4 if self._debug else 3)
        )
        h = self._bar_thickness
        self._bar = bar = imple.ProgressBar(
            (1, rh // 2 - h // 2),
            (rw - 2, h),
            # stroke=0,
            bar_color=0xFF0000,
        )

        self._knob_outline = knob_outline = imple.SimpleRoundRect(
            0,
            rh // 2 - knob_dim // 2,
            width=knob_dim,
            height=knob_dim,
            radius=self._radius,
            fill=0xFF0000,
            # stroke=knob_dim // 10,
            # outline=color.gray,
        )

        self._stroke = stroke = knob_dim // 10
        self._knob_fill = knob_fill = imple.SimpleRoundRect(
            stroke,
            (rh // 2 - knob_dim // 2) + stroke,
            width=knob_dim - 2 * stroke,
            height=knob_dim - 2 * stroke,
            radius=self._radius - stroke,
            fill=0xFF0000,
        )

        group.append(bar)
        group.append(knob_outline)
        group.append(knob_fill)

        self._knob_dim = knob_dim
        self._span = value_range = rw - knob_dim
        self._position = pos = int(value_range * self._state.value(self))
        self._y_limits = (sh // 2 - knob_dim // 2, sh // 2 + knob_dim // 2)
        self._value = pos / value_range
        self._pos_on_prev_update = -10000
        self._update_position(pos)

        self._update_colors_(**self._style_._colors_)

        self._state._register_handler_(self, self._update_value_from_state)

        if self._debug:
            self._mark = mark = imple.RoundRect(
                0,
                rh // 2 - knob_dim // 2,
                width=knob_dim * 2,
                height=knob_dim,
                r=0,
                fill=color.red,
                stroke=0,
            )
            group.append(mark)

    def _demolish_(self):
        self._state._deregister_handler_(self)
        super()._demolish_()

    def _start_coord_(self, coord):
        # TODO: ADD EXPLANATION
        self._initial_position = init_pos = self._position
        knob_dim = self._knob_dim
        x_limits = xmin, xmax = (init_pos - knob_dim // 2, init_pos + 3 * knob_dim // 2)
        ymin, ymax = self._y_limits
        x, y = coord
        self._init_x = init_x = clamp(knob_dim // 2, x, self._span + knob_dim // 2)

        self._selected = bool((ymin <= y <= ymax) and (xmin <= x <= xmax))

        if self._debug:
            self._mark.x = xmin

    def _last_coord_(self, coord):
        self._selected = False

    def _update_coord_(self, coord):
        if self._selected:
            pixel_value = coord[0] - self._init_x + self._initial_position
            pixel_value = clamp(0, pixel_value, self._span)
            self._update_position(pixel_value)

    def _update_value_from_state(self, value):
        self._update_position(
            clamp(
                0,
                int(value * self._span),
                self._span,
            )
        )

    def _update_position(self, new_pos):
        self._position = new_pos
        value = new_pos / self._span

        prev_pos = self._pos_on_prev_update
        if abs(prev_pos - new_pos) > 3:  # only update when moved 3 + pixels

            # knob = self._knob
            # bar = self._bar

            self._state.update(self, value)
            self._value = value

            self._knob_outline.x = new_pos
            self._knob_fill.x = new_pos + self._stroke
            self._bar.set_progress(value)
            self._pos_on_prev_update = new_pos

    def _update_colors_(self, *, bar, knob_border, knob):
        self._knob_fill.fill = knob
        self._knob_outline.fill = knob_border
        self._bar.bar_color = bar  # hack
