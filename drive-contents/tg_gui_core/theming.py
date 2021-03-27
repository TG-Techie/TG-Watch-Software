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

# TODO: see list
#   make SubTheme,
#   add deregistering code to StyledWidget,
#   optimized for un-used source_state lists

from .base import Widget
from ._shared import uid, ConstantGroup
from .specifiers import SpecifierReference, Specifier, AttributeSpecifier, _specify
from .stateful import State

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
        "giant",
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
        self._colors_ = dict(
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
        if self.__name__ is not None:
            return f"<{type(self).__name__} {self._id_}: {self._name}>"
        else:
            return f"<{type(self).__name__} {self._id_}>"

    def _setup_(self, theme: "Theme", name):
        assert isinstance(name, str)
        self._name = name
        return self

    def __getattr__(self, name):
        maybe_color = self._colors_.get(name, None)
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
        self._colors_ = specs = dict.fromkeys(Palette._default_color_set)

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

        specs = self._colors_
        base_specs = base_pal._colors_
        for name, value in specs.items():
            if value is None:
                specs[name] = base_specs[name]

        return self


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

        self.plain = plain
        self.action = action
        self.warning = warning
        self.alert = alert

        self.margin = margin
        self.radius = radius
        self.border = border

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

    def _resolve_theme_(self, widget):
        screen = widget._screen_
        self.min_size = screen.min_size
        self.min_visible = screen.min_visible
        self.min_margin = screen.min_margin

        # init the palettes, be sure to setup plain first
        self.plain._setup_(self, "plain")
        self.action._setup_(self, "action")
        self.warning._setup_(self, "warning")
        self.alert._setup_(self, "alert")

        return self

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def __getattr__(self, name):
        # attr = self._widget_styles.get(name, None)
        attr = self._widget_styles.get(name, None)
        if attr is None:
            raise AttributeError(f"{self} has not attribute `.{name}`")
        else:
            return attr


class SubTheme(Theme):
    def __init__(self, *_, **__):
        raise NotImplementedError


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
    stylecls._name_ = name
    widgetcls._style_name_ = name
    widgetcls._style_type_ = stylecls
    Theme._add_stylecls(name, stylecls)
    return widgetcls  # part of a decorator


class StyleConstructor:
    def __init__(self, basetype, palette_spec=None, kwargs={}):
        self._basetype = basetype
        self._palette = palette_spec
        self._kwargs = kwargs
        self._style = None

    def _construct_(self, theme):
        return (
            self._make_and_return_style(theme) if self._style is None else self._style
        )

    def _make_and_return_style(self, theme):

        assert isinstance(theme, Theme)
        basetype = self._basetype
        base_style = getattr(theme, basetype._name_)

        palette = self._palette
        if palette is None:
            palette = base_style._palette

        specs_and_attrs = dict.fromkeys(
            basetype._style_colors_ + basetype._style_elements_
        )

        specs_and_attrs.update(base_style._colors_)
        specs_and_attrs.update(base_style._elems_)
        specs_and_attrs.update(self._kwargs)

        self._basetype = None
        self._palette = None
        self._kwargs = None

        self._style = style = basetype(
            palette,
            **specs_and_attrs,
        )

        return style


class Style:
    _style_colors_ = None  # can be colors, specs, or states
    _style_elements_ = None  # radius, font, etc

    @classmethod
    def substyle(cls, palette_spec=None, **kwargs):
        return StyleConstructor(cls, palette_spec, kwargs)

    def __init__(self, palette_spec, **kwargs):

        assert isinstance(palette_spec, (Palette, ThemeAttributeSpecifier)), (
            f"found {palette_spec}, expecing an object of type {Palette} or "
            + f"`theme.<some palette>`"
        )
        self._id_ = uid()
        self._palette = palette_spec

        # mutates from a dict of color specs to a dict fo colors
        self._colors_ = color_specs = dict.fromkeys(self._style_colors_)
        self._source_states = {}
        self._registered_widgets = {}

        self._elems_ = elems = dict.fromkeys(self._style_elements_)

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

    def _setup_(self, theme):
        global color
        palette = self._palette
        if isinstance(palette, ThemeAttributeSpecifier):
            palette = palette._resolve_specified_(theme)
        assert isinstance(palette, Palette), f"found {repr(palette)}"
        self._palette = palette

        colors = self._colors_
        states = self._source_states
        for name, color_spec in colors.items():

            if isinstance(color_spec, (int, color)):
                color = color_spec
            elif isinstance(color_spec, ThemeAttributeSpecifier):
                color = color_spec._resolve_specified_(theme)
            elif isinstance(color_spec, PaletteAttributeSpecifier):
                color = color_spec._resolve_specified_(palette)
            elif isinstance(color_spec, State):
                states[name] = color_spec
                color_spec._register_handler_(self, self._on_source_color_update)
                color = color_spec.value(self)
            else:
                raise TypeError(
                    f"{type(self).__name__}.{color_name} atttribute must be an int,  "
                    + f"a State object, some `theme.<some attr>`, or `palette.<some attr>`"
                )
            colors[name] = color

        elems = self._elems_
        for name, elem_spec in elems.items():
            if isinstance(elem_spec, ThemeAttributeSpecifier):
                elem = elem_spec._resolve_specified_(theme)
            elif isinstance(elem_spec, PaletteAttributeSpecifier):
                elem = elem_spec._resolve_specified_(palette)
            else:
                elem = elem_spec
            elems[name] = elem

    def _register_handler_(self, widget, handler):
        assert isinstance(widget, StyledWidget), f"found {widget}"
        assert widget._id_ not in self._registered_widgets
        self._registered_widgets[widget._id_] = handler

    def _deregister_handler_(self, widget):
        assert isinstance(widget, StyledWidget), f"found {widget}"
        assert widget._id_ in self._registered_widgets
        self._registered_widgets.pop(widget._id_)

    def _on_source_color_update(self, _):
        colors = self._colors_
        for colorname, state in self._source_states.items():
            colors[colorname] = state.value(self)

        for handler in self._registered_widgets.values():
            handler(**colors)


class StyledWidget(Widget):
    _style_name_ = None
    _style_type_ = None

    def __init__(self, style=None, **kwargs):
        super().__init__(**kwargs)

        self._style_ = style
        assert style is None or isinstance(style, (Style, StyleConstructor))

    def _nest_in_(self, superior):
        super()._nest_in_(superior)

        style = self._style_

        theme = self._superior_._theme_
        if style is None:
            style = getattr(theme, self._style_name_)
        elif isinstance(style, StyleConstructor):
            style = style._construct_(theme)
        assert isinstance(style, self._style_type_), (
            f"{type(self).__name__}(...) style arguement must be a "
            + f"{self._style_type_.__name__}(...) or "
            + f"{self._style_type_.__name__}.subsstyle(...),  found {style}"
        )

        style._setup_(theme)
        style._register_handler_(self, self._update_colors_)

        self._style_ = style


class StyledAttribute:
    def __init__(self, attrname, style_attr_name):
        self._attrname = attrname
        self._priv_attrname = f"_styled_{attrname}_attr_"
        self._style_attr_name = style_attr_name

    def __repr__(self):
        return (
            f"<{type(self).__name__} .{self._attrname} "
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
            styledattr = owner._style_._elems_.get(self._style_attr_name, None)
            if isinstance(styledattr, Specifier):
                styledattr = styledattr._resolve_specified_(owner)
            elif styledattr is None:
                raise AttributeError(
                    f"{owner}'s style has no '{self._style_attr_name}' element.\n"
                    + f"Error occured when trying to fetch the default value for {owner}'s "
                    + f"`.{self._attrname}` StyledAttribute from {owner}'s style"
                    + f", {owner._style_}.\n"
                )
            setattr(owner, self._priv_attrname, styledattr)
            return styledattr
        else:
            return privattr

    def __set__(self, owner, value):
        setattr(owner, self._priv_attrname, value)

    @classmethod
    def _update_colors_(cls, **_):
        raise NotImplementedError(f"._update_colors_ method not defined for {cls}")
