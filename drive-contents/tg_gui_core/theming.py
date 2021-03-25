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
        # requirted overides
        accent: color,
        accenttext: color,
        active: color,
        activetext: color,
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

    @classmethod
    def _add_stylecls(cls, stylekey, styletype):
        assert stylekey not in cls._styles_
        assert isinstance(styletype, type)
        assert issubclass(styletype, Style)
        cls._styles_[stylekey] = styletype

    def __init__(
        self,
        *,
        margin,
        radius,
        border,
        plain: Palette,
        action: SubPalette,
        warning: SubPalette,
        alert: SubPalette,
        **kwargs,
    ):
        self._id_ = uid()

        self._palettes = dict(
            plain=plain,
            action=action,
            warning=warning,
            alert=alert,
        )

        self._attrs = dict(
            margin=margin,
            radius=radius,
            border=border,
        )

        # here we use a widget_styles dict because it can be pre-allocated
        #    unlike setting attributes on self
        self._widget_styles = widget_styles = dict.fromkeys(self._styles_)
        for stylename, stylecls in self._styles_.items():
            widget_styles[stylename] = widget_style = kwargs.pop(stylename, None)

            # check after (for clarity)
            assert widget_style is not None, (
                f"{type(self)} expecting keyword argument '{stylename}' of "
                + f"type {stylecls}"
            )
            assert isinstance(widget_style, stylecls), (
                f"expecting argument of type {stylecls} for keyword "
                + f"argument '{stylename}', given {repr(widget_style)}"
            )

        else:
            # make sure there are no extra kwargs
            assert len(kwargs) == 0, (
                "unexpected keyword arguments "
                + f"{', '.join(repr(kw) for kw in kwargs)} passed to "
                + f"{type(self)}"
            )

    def _setup_(self, widget):
        # init the palettes, be sure to setup plain first
        self.plain._setup_(self, "plain")
        self.action._setup_(self, "action")
        self.warning._setup_(self, "warning")
        self.alert._setup_(self, "alert")

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def __getattr__(self, name):
        # attr = self._widget_styles.get(name, None)
        if name in self._styles_:
            return self._widget_styles.get(name, None)
        else:
            raise AttributeError(f"{self} has not attribute `.{name}`")


class SubTheme(Theme):
    def __init__(self):
        FUCK


def styled(**kwarg):
    """
    associates a Style subclass with a StyledWidget and adds it as a
    named default for the Theme class
    """

    assert len(kwarg) == 1, (
        "@styled(...) takes only one argument, "
        + f"found {', '.join(repr(kw) for kw in kwarg.keys())}"
    )

    # get the name and style class (now that we know it is 1 arg long)
    (stylename,) = kwarg.keys()
    (stylecls,) = kwarg.values()

    return lambda widgetcls: _add_styleclass_to_styledwidgetclass(
        stylename,
        stylecls,
        widgetcls,
    )


def _add_styleclass_to_styledwidgetclass(name, stylecls, widgetcls):
    assert isinstance(name, str)
    assert isinstance(stylecls, type) and issubclass(stylecls, Style)
    assert isinstance(widgetcls, type) and issubclass(widgetcls, StyledWidget)

    stylecls._init_style_subclass()
    Theme._add_stylecls(name, stylecls)
    widgetcls._theme_style_name_ = name
    widgetcls._style_type_ = widgetcls
    return widgetcls  # part of a decorator


class Style:
    _style_colors_ = None  # can be colors, specs, or states
    _style_elements_ = None  # radius, font, etc

    @classmethod
    def substyle(cls, palette_spec=None, **kwargs):
        return None

    def __init__(self, palette_spec, **kwargs):

        assert isinstance(palette_spec, (Palette, ThemeAttributeSpecifier)), (
            f"found {palette_spec}, expecing an object of type {Palette} or "
            + f"`theme.<some palette>`"
        )
        self._palette_spec = palette_spec

        self._color_specs = color_specs = dict.fromkeys(self._style_colors_)
        self._elems = elems = dict.fromkeys(self._style_elements_)

        # make sure all the style colors are specified
        for colorname in self._style_colors_:
            assert (
                colorname in kwargs
            ), f"{type(self).__name__}(...) expecting keyword argument '{colorname}'"
            color_specs[colorname] = kwargs.pop(colorname)

        for colorname in self._style_elements_:
            assert (
                colorname in kwargs
            ), f"{type(self).__name__}(...) expecting keyword argument '{colorname}'"
            elems[colorname] = kwargs.pop(colorname)

        # check there are no extra keyword arguments
        assert len(kwargs) == 0, (
            "unexpected keyword argument(s) "
            + f"{', '.join(repr(kw) for kw in kwargs.keys())}"
        )

    @classmethod
    def _init_style_subclass(cls):
        # check was initied correctly
        if not isinstance(cls._style_colors_, tuple):
            raise TypeError(
                f"{cls} incorrectly subclassed from Style, the ._style_colors_ "
                + "class variable should be a tuple of color names,"
                + f" found {repr(cls._style_colors_)}"
            )
        if not isinstance(cls._style_elements_, tuple):
            raise TypeError(
                f"{cls} incorrectly subclassed from Style, the ._style_elements_ "
                + "class variable should be a tuple of style element names,"
                + f" found {repr(cls._style_elements_)}"
            )


class StyledWidget(Widget):
    pass


class StyledAttribute:
    def __init__(self, attrname, style_attr_name):
        self._attrname = attrname
        self._priv_attrname = f"_styled_{attrname}_attr_"
        self._style_attr_name = style_attr_name

    def __repr__(self):
        return (
            f"<{type(self).__name__} .{_attrname} "
            + f"<- <style>.{self._style_attr_name}>"
        )

    def __get__(self, owner, ownertype):
        assert hasattr(owner, self._priv_attrname), (
            f"``{owner}.{self._attrname}`` attribute not initialized, "
            + f"styled `{type(owner).__name__}.{self._attrname}` attributes must be "
            + f"initialized to `None` or some value"
        )

        privattr = getattr(owner, self._priv_attrname)
        if privattr is None:  # resolve the attr form style
            styledattr = owner._style_._get_attr_(self._style_attr_name)
            if isinstance(styledattr, Specifier):
                styledattr = styledattr._resolve_specified_(owner)
            setattr(owner, self._priv_attrname, styledattr)
            return styledattr
        else:
            return privattr

    def __set__(self, owner, value):
        setattr(owner, self._priv_attrname, value)
