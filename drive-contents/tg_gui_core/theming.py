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

from .base import Widget
from ._shared import uid, ConstantGroup
from .specifiers import SpecifierReference, AttributeSpecifier, _specify
from .container import _find_declared_superior
from sys import version_info as _version_info

align = ConstantGroup(
    "align",
    (
        "leading",
        "center",
        "trailing",
        "justify",
    ),
)


def _find_theme_if_widget(attr_spec, obj):
    if isinstance(obj, Widget):
        decld_cntr = _find_declared_superior(attr_spec, obj)
        return decld_cntr._theme_
    elif isinstance(obj, Theme):
        return Theme
    else:
        raise TypeError(
            "`theme.<some attr>` cannot be refenced to objects of "
            + f"type {type(obj)}, found {obj}"
        )


theme = SpecifierReference(
    "theme",  # palettes are specified realtive to a theme thus
    resolver=_find_theme_if_widget,
)


def _verify_is_palette(attr_spec, obj):
    assert isinstance(obj, Palette), (
        f"`palette.<some attr>` cannot be refenced to objects of "
        + f"type {type(obj)}, found {obj}"
    )
    return obj


def _find_palette_if_widget(attr_spec, obj):
    if isinstance(obj, Widget):
        theme = _find_theme_if_widget(attr_spec, obj)
    elif isinstance(obj, Palette):
        return obj
    else:
        raise TypeError(
            "`palette.<some attr>` cannot be refenced to objects of "
            + f"type {type(obj)}, found {obj}"
        )


class ColorSpecifier(AttributeSpecifier):
    pass


palette = SpecifierReference(
    "palette",  # colors are specified relative to palettes
    resolver=_find_palette_if_widget,
    constructs=ColorSpecifier,
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


Color = int


class Palette:
    def __init__(
        self,
        *,
        name,
        # Color used form composing ui shapes
        foregnd: Color,
        pregnd: Color,
        midgnd: Color,
        postgnd: Color,
        backgnd: Color,
        # text for contrasing each ground
        foretext: Color,
        pretext: Color,
        midtext: Color,
        posttext: Color,
        text: Color,
        # here are the attributes that are normally sub-styled
        # for the base Style object they should be the 'plain'
        accent: Color,
        accenttext: Color,
        active: Color,
        activetext: Color,
        **kwargs,
    ):
        self._id_ = uid()
        self._name = name
        self._registered = {}
        self._colors = dict(
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
            **kwargs,
        )

    def __repr__(self):
        return f"<{type(self).__name__}:{self._id_} {self._name}>"

    def __getattr__(self, name, sub_pal=None):
        assert isinstance(name, str)
        if name in self._colors:
            return self._colors[name]
        else:
            if sub_pal is None:
                raise AttributeError(f"'{self}' has no color '{name}'")
            else:
                raise AttributeError(f"'{sub_pal}' has no color '{name}'")

    def _set_specified_(self, *_, **__):
        raise NotImplementedError


class SubPalette(Palette):
    def __init__(
        self,
        *,
        name,
        # requirted overides
        accent: Color,
        accenttext: Color,
        active: Color,
        activetext: Color,
        _base_palette_=None,
        **kwargs,
    ):
        self._id_ = uid()
        self._name = name
        self._registered = {}
        self._base_palette_ = None
        self._colors = dict(
            accent=accent,
            accenttext=accenttext,
            active=active,
            activetext=activetext,
            **kwargs,
        )

    def __getattr__(self, name):
        assert isinstance(name, str)
        assert (
            self._base_palette_ is not None
        ), f"{self} not given base palette, be sure to use it ina Theme"
        # print(f"SubPalette:{self}._get_color_({reader}, {name})")
        if name in self._colors:
            return self._colors[name]
        else:
            return self._base_palette_.__getattr__(name, sub_pal=self)


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

    def __getattr__(self, name):
        attr = self._widget_styles.get(name, None)
        if attr is None:
            raise AttributeError(f"{self} has not attribute `.{name}`")
        else:
            return attr


class SubTheme:
    def __init__(
        self,
    ):
        FUCK


# libtool
def styled(**kwarg):
    assert len(kwarg) == 1, (
        f"@styled(...) only takes one keyword argument, "
        + f"found {','.join(repr(kw) for kw in kwarg)}"
    )
    (pair,) = kwarg.items()
    stylename, stylecls = pair

    def _add_style_for(cls):
        assert isinstance(cls, type) and issubclass(
            cls, StyledWidget
        ), f"found {cls}, expecting a subcalss of StyledWidget"

        Theme._add_style(stylename, stylecls)
        cls._style_name_ = stylename
        return cls

    return _add_style_for


class Style:
    _style_attrs_ = None  # tuple in subclasses

    def __init__(self, theme_spec, **kwargs):
        self._id_ = uid()
        # make sure the class was inited correctly
        assert isinstance(self._style_attrs_, tuple), (
            f"{type(self)}'s ._style_attrs_ not set in subclass, "
            + f"subclesses of Style must set ._style_attrs_ to a tuple of "
            + "the desired attr mapping names"
        )

        global theme
        self._pal_spec = theme_spec

        FUCK(REFACTOR_INTO_TUPLE_TO_DEFINE_ORDERING)
        # find the required stylr attribute
        self._attr_specs = attr_specs = dict.fromkeys(self._style_attrs_)
        for attrname in attr_specs:
            assert attrname in kwargs, f"{type(self)} missing kwarg '{attrname}'"
            attr_specs[attrname] = kwargs.pop(attrname)
        else:
            # make sure there are not any extra kwargs
            assert len(kwargs) == 0, (
                f"unexpected keyword argument{'s' if len(kwargs) > 1 else ''} "
                + f"{', '.join(repr(kw) for kw in kwargs)} for {type(self)}"
            )

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def _get_colors_(self, widget):
        # find palette:
        palette = _specify(self._pal_spec, widget)
        # specs = self._attr_specs
        # return (_specify(specs[attrname]) for attrname in self._style_attrs_)\
        attr_specs = self._attr_specs
        return FUCK


class SubStyle(Style):
    def __init__(self, palette_spec=None, **kwargs):
        self._id_ = uid()
        if palette_spec is not None:
            assert isinstance(palette_spec, ThemeAttributeSpecifier)
        FUCK


class StyledWidget(Widget):
    _style_name_ = None

    def __init__(self, style=None, **kwargs):
        super().__init__(**kwargs)

        assert style is None or isinstance(style, Style), f"TODO: error message"

        self._given_style = style
        self._style_ = None

        # check subclass inited properly
        assert self._style_name_ is not None, (
            f"subclasses of StyleWidget must be decorated with @styled(...), "
            + f"seems like {type(self)} was not"
        )

    def _nest_in_(self, superior):
        super()._nest_in_(superior)

        # resolve style
        style = self._given_style
        if style is None:  #
            style = getattr(self._superior_._theme_, self._style_name_)
        assert isinstance(style, Style), f"TODO: error message"
        self._style_ = style

    # def _resolve_style_(self):
    #     print(self._style_)
    #     FUCK
    #     return self._style_

    def _update_style_(self, *_):
        raise NotImplementedError(
            "subclasses of StyledWidget must implement "
            + "`._update_style_(...)` method"
        )
