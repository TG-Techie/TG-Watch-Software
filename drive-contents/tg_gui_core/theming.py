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

# TODO: re-write to use descriptors for color and attributes
#   where @styled formats the Style subclass


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
        "body",
        "footnote",
    ),
)


def _find_theme_if_widget(attr_spec, obj):
    if isinstance(obj, Widget):
        decld_cntr = _find_declared_superior(attr_spec, obj)
        return decld_cntr._theme_
    elif isinstance(obj, Theme):
        return obj
    else:
        raise TypeError(
            "`theme.<some attr>` cannot be refenced to objects of "
            + f"type {type(obj)}, found {obj}"
        )


class ThemeAttributeSpecifier(AttributeSpecifier):
    __call__ = None
    __getattr__ = None


theme = SpecifierReference(
    "theme",  # palettes are specified realtive to a theme thus
    resolver=_find_theme_if_widget,
    constructs=ThemeAttributeSpecifier,
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
    __call__ = None
    __getattr__ = None


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
        # name,
        # requirted overides
        accent: Color,
        accenttext: Color,
        active: Color,
        activetext: Color,
        _base_palette_=None,
        **kwargs,
    ):
        self._id_ = uid()
        self._name = None
        self._registered = {}
        self._base_palette_ = None
        self._colors = dict(
            accent=accent,
            accenttext=accenttext,
            active=active,
            activetext=activetext,
            **kwargs,
        )

    def _resolve_colors_(self, base_pal):
        raise FUCK

    def __getattr__(self, name):
        assert (
            self._base_palette_ is not None
        ), f"{self} not given base palette, be sure to use it in a Theme"
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
    _style_colors_ = None  # tuple in subclasses
    _style_attrs_ = None  # tuple in subclasses

    def __init__(self, pal_spec, **kwargs):
        self._id_ = uid()
        # make sure the class was inited correctly
        assert isinstance(self._style_colors_, tuple), (
            f"{type(self)}'s ._style_colors_ not set in subclass, "
            + f"subclesses of Style must set ._style_colors_ to a tuple of "
            + "the required color names"
        )

        assert isinstance(self._style_attrs_, tuple), (
            f"{type(self)}'s ._style_attrs_ not set in subclass, "
            + f"subclesses of Style must set ._style_attrs_ to a tuple of "
            + "the required style attributes"
        )

        # parse the arguments and check for completion and extras
        color_specs = []
        attrs = []

        for color_name in self._style_colors_:
            assert color_name in kwargs, f"{type(self)} missing kwarg '{color_name}'"
            color_specs.append(kwargs.pop(color_name))
            # attr_specs[attrname] = kwargs.pop(attrname)
        for attr_name in self._style_attrs_:
            assert attr_name in kwargs, f"{type(self)} missing kwarg '{attr_name}'"
            attr = kwargs.pop(attr_name)
            assert not isinstance(attr, AttributeSpecifier), (
                "style attributes cannot be Attribute specifiers "
                + f"{attrname}={attr}, passed to {self} on init"
            )
            attrs.append(attr)

        # make sure there are not any extra kwargs
        assert len(kwargs) == 0, (
            f"unexpected keyword argument{'s' if len(kwargs) > 1 else ''} "
            + f"{', '.join(repr(kw) for kw in kwargs)} for {type(self)}"
        )

        self._pal_spec = pal_spec
        self._color_specs = tuple(color_specs)
        self._colors = None
        self._attrs = tuple(attrs)

        # it is possible these are not necesarry in the future
        self._theme = None
        self._palette = None

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def _is_resolved(self):
        return self._colors is not None

    def _resolve_style_(self, ref):
        if self._is_resolved():
            assert (
                self._find_theme(ref) is self._theme
            ), f"styles cannot be double resolved"
            return

        self._theme = theme = self._find_theme(ref)
        self._palette = palette = self._find_palette(self._pal_spec, theme, ref)

        self._colors = tuple(_specify(spec, palette) for spec in self._color_specs)

    def _register_handler_(self, widget, handler):
        pass

    def _deregister_handler_(self, widget):
        pass

    def _get_colors_(self, ref):
        return iter(self._colors)

    def __getattr__(self, name):
        assert self._colors is not None, f"TODO: better error, {self} not resolved"

        if name in self._style_colors_:
            return self._colors[self._style_colors_.index(name)]
        elif name in self._style_attrs_:
            return self._attrs[self._style_attrs_.index(name)]
        else:
            raise AttributeError(f"{self} has not attribute `.{name}`")

    def _find_theme(pal_spec, ref):
        return _find_declared_superior(None, ref)._theme_

    def _find_palette(self, palette, theme, ref):

        print(f"{self}._resolve_style_({ref}): theme={theme}")

        if isinstance(palette, ThemeAttributeSpecifier):
            palette = palette._resolve_specified_(theme)

        assert isinstance(palette, Palette), f"found {palette}"

        return palette


class SubStyle(Style):
    def __init__(self, pal_spec=None, **kwargs):
        self._id_ = uid()
        assert pal_spec is None or isinstance(
            palette_spec, (Palette, ThemeAttributeSpecifier)
        ), f"TODO: better error, found {pal_spec}"

        for color_name, color_spec in kwargs.items():
            assert isinstance(color_spec, (Color, ColorSpecifier)), (
                f"{self} `color_name=...` must be a color or ColorSpecifier, "
                + f"found {color_spec}"
            )

        self._pal_spec = pal_spec
        self._color_specs = kwargs
        self._base_style = None
        self._color_names = None
        self._colors = None

        # it is possible these are not necesarry in the future
        self._theme = None
        self._palette = None

        self._registered_handlers = {}

    def _resolve_style_(self, ref):
        if self._is_resolved():
            assert (
                self._find_theme(ref) is self._theme
            ), f"styles cannot be double resolved"
            return

        assert isinstance(ref, StyledWidget), f"expecting a StledWidget, found {ref}"

        self._theme = theme = self._find_theme(ref)
        self._base_style = base_style = getattr(theme, ref._style_name_)

        # make sure it is resolved...
        base_style._resolve_style_(ref)

        self._palette = palette = self._find_palette(
            base_style._palette if self._pal_spec is None else self._pal_spec,
            theme,
            ref,
        )

        color_specs = self._color_specs
        # resolves so it uses base style
        self._color_names = base_style._style_colors_
        self._colors = tuple(
            _specify(self._color_specs[color_name], palette)
            if color_name in color_specs
            else getattr(base_style, color_name)
            for color_name in base_style._style_colors_
        )

    def _register_handler_(self, widget, handler):
        assert widget._id_ not in self._registered_handlers
        self._registered_handlers[widget._id_] = handler

    def _deregister_handler_(self, widget):
        assert widget._id_ in self._registered_handlers
        self._registered_handlers.pop(widget._id_)

    def __getattr__(self, name):
        if name in self._color_names:
            return self._colors[self._color_names.index(name)]
        else:
            return getattr(self._base_style, name)


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
        if style is None:
            style = getattr(self._superior_._theme_, self._style_name_)

        assert isinstance(style, Style), f"TODO: error message"

        style._resolve_style_(self)
        style._register_handler_(self, self._update_color_)
        self._style_ = style

    def _unnest_from_(self, superior=None):
        super()._unnest_from_(superior)
        self._style_._deregister_handler_(self)

    # def _resolve_style_(self):
    #     print(self._style_)
    #     FUCK
    #     return self._style_

    def _update_color_(self, *_):
        raise NotImplementedError(
            "subclasses of StyledWidget must implement the "
            + f"`._update_color_ method, {type(self)} does not"
        )
