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

from tg_gui_core import Widget, StyledWidget, Style, State, align, styled, font
from . import _imple as imple


class LabelStyle(Style):
    _style_colors_ = ("text",)
    _style_attrs_ = ("alignment", "font")


FIXME = lambda v: v


@styled(label_style=LabelStyle)
class Label(StyledWidget):
    def __init__(
        self,
        text,
        _alignment=None,
        _font=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._text_state = text
        self._font = _font
        self._alignment = _alignment

    def _pickup_(self):
        unlink_from_src(widget=self, src=self._text_state)
        super()._pickup_()

    def _on_nest_(self):
        """
        Resolve defaults for any inputs if no input was provided.
        """

        print(self, self._style_)

        if self._font is None:
            self._font = self._style_.font

        if self._alignment is None:
            self._alignment = self._style_.alignment

    def _build_(self):
        global imple

        super()._build_()

        print(f"self._style_={self._style_}")
        # (text_color,) = self._resolve_style_()
        self._group = group = imple.Label(
            text="___",
            color=0xFF0000,
            coord=self._rel_coord_,
            dims=self._phys_size_,
            alignment=self._alignment,
            scale=FIXME(2),
        )

        # self._update_color()
        text_state = self._text_state
        if isinstance(text_state, State):
            text_state._register_handler_(self, self._update_text)
            self._update_text(text_state.value(self))
        else:
            self._update_text(text_state)

        self._update_color_(*self._style_._get_colors_(self))

    def _demolish_(self):
        if isinstance(self._text_state, State):
            self._text_state._deregister_handler_(self)
        super()._demolish_()

    def _update_text(self, text):
        # hot patch for a cp library bug
        global align
        alignment = self._alignment
        if alignment is align.center:
            padding = " {} "
        elif alignment is align.leading:
            padding = "{} "
        else:  # alignment is align.trailing:
            padding = " {}"

        while len(text) <= 3:
            text = padding.format(text)

        self._group.text = text

    def _update_color_(self, text):
        print("asdfasdf", text, type(text), repr(text))
        print(f"asdf{self}._update_color_(text={text})")
        self._group.color = text


from tg_gui_core import Theme

print(Theme._styles_)
