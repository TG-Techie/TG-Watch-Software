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

# TODO: make SubTheme

from .base import Widget
from ._shared import uid, ConstantGroup
from .specifiers import SpecifierReference, Specifier, AttributeSpecifier, _specify

align = ConstantGroup(
    "align",
    (
        "leading",
        "center",
        "trailing",
        "justify",
    ),
)

font = ConstantGroup(
    "font",
    (
        "largetitle",
        "title",
        "heading",
        "subheading",
        "label",
        "body",
        "footnote",
    ),
)


class color(int):
    # in the future consider adding other init/etc

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

    @classmethod
    def fromfloats(cls, r, g, b):
        r = round(255 * r ** 1.125)
        g = round(255 * g ** 1.125)
        b = round(255 * b ** 1.125)
        return cls((r << 16) | (g << 8) | (b << 0))

    @classmethod
    def fromints(cls, r, g, b):
        assert isinstance(r, int) and r < 256
        assert isinstance(g, int) and g < 256
        assert isinstance(b, int) and b < 256
        return cls((r << 16) | (g << 8) | (b << 0))


def _resolve_assert_is(attr_sepc, ref, types):
    if isinstance(ref, types):
        return ref
    else:
        raise TypeError(
            f"{repr(attr_spec)} cannot be referenced from an object "
            + f"of type {type(obj)}, found {obj}"
        )


class ThemeAttributeSpecifier(AttributeSpecifier):
    pass


class PaletteAttributeSpecifier(AttributeSpecifier):
    pass

    def __getattr__(self, _):
        raise TypeError(
            f"{type(self).__name__}s cannot be used to specify past one level, "
            + f"attempted `{str(self)}.{name}`"
        )


theme = SpecifierReference(
    "theme",  # palettes are specified realtive to a theme thus
    resolver=lambda attr_spec, ref: _resolve_assert_is(attr_spec, ref, Theme),
    constructs=ThemeAttributeSpecifier,
)

palette = SpecifierReference(
    "palette",  # colors are specified relative to palettes
    resolver=lambda attr_spec, ref: _resolve_assert_is(attr_spec, ref, Palette),
    constructs=PaletteAttributeSpecifier,
)


class Palette:
    _default_color_set = {
        "foregnd",
        "pregnd",
        "midgnd",
        "postgnd",
        "backgnd",
        "foretext",
        "pretext",
        "midtext",
        "posttext",
        "text",
        "accent",
        "accenttext",
        "active",
        "activetext",
    }

    def __init__(
        self,
        *,
        # Colors used for composing ui shapes
        foregnd: color,
        pregnd: color,
        midgnd: color,
        postgnd: color,
        backgnd: color,
        # text for contrasing each ground
        foretext: color,
        pretext: color,
        midtext: color,
        posttext: color,
        text: color,
        # here are the attributes that are normally sub-styled
        # for the base Style object they should be the 'plain'
        accent: color,
        accenttext: color,
        active: color,
        activetext: color,
        # **kwargs, # diabled for now
    ):
        self._id_ = uid()
        self._name = None
        self._color_specs = dict(
            foregnd=foregnd,
            pregnd=pregnd,
            midgnd=midgnd,
            postgnd=postgnd,
            backgnd=backgnd,
            # text for contrasing each ground
            foretext=foretext,
            pretext=pretext,
            midtext=midtext,
            posttext=posttext,
            text=text,
            # here are the attributes that are normally sub-styled
            # for the base Style object they should be the 'plain'
            accent=accent,
            accenttext=accenttext,
            active=active,
            activetext=activetext,
            # **kwargs, # diabled for now
        )

    def __repr__(self):
        if self.__name is not None:
            return f"<{type(self).__name__} {self._id_}: {self._name}>"
        else:
            return f"<{type(self).__name__} {self._id_}>"

    def _setup_(self, theme: "Theme", name):
        assert isinstance(name, str)
        self._name = name

    def __getattr__(self, name):
        maybe_color = self._colors.get(name, None)
        if maybe_color is not None:
            return maybe_color
        else:
            raise AttributeError(f"{self} has no attribute `.{name}`")


class SubPalette(Palette):
    def __init__(
        self,
        base_palette_spec,  # Union[Palette, AttributeSpecifier]
        *,
        # name,
        # requirted overides
        accent: Color,
        accenttext: Color,
        active: Color,
        activetext: Color,
        **kwargs,
    ):
        assert isinstance(base_palette_spec, ThemeAttributeSpecifier)

        self._id_ = uid()
        self._name = None
        self._base_palette_spec = base_palette_spec
        self._color_specs = specs = dict.fromkeys(Palette._default_color_set)

        specs.update(
            dict(
                accent=accent,
                accenttext=accenttext,
                active=active,
                activetext=activetext,
            )
        )

        specs.update(kwargs)

    def _setup_(self, theme: "Theme", name):
        assert isinstance(name, str)
        assert isinstance(theme, Theme)
        self._name = name

        base_pal = _specify(self._base_palette_spec, theme)

        specs = self._color_specs
        base_specs = base_pal._color_specs
        for name, value in specs.items():
            if value is None:
                specs[name] = base_specs[name]


class Theme:
    _styles_ = {}

    _default_attr_set = {
        "plain",
        "action",
        "warning",
        "alert",
        "indicator",
        "margin",
        "radius",
    }

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

        self._palettes = dict(
            plain=plain,
            action=action,
            warning=warning,
            alert=alert,
            indicator=indicator,
        )

        self._attrs = dict(
            margin=margin,
            radius=radius,
        )

        # here we use a widget_styles dict because it can be pre-allocated
        #    unlike setting attributes on self
        style_names = self._styles_
        self._widget_styles = widget_styles = dict.fromkeys(style_names)
        for stylename, stylecls in style_names.items():
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
