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

# from . import dimension_specifiers
# from . import position_specifiers


class SpecifierConstructor:  # AttributeSpecifier constructor, basically syntactic suger
    def __repr__(self):
        return "<SpecifierConstructor 'self'>"

    def __getattr__(self, attrname):
        global AttributeSpecifier
        return AttributeSpecifier(attrname)


class AttributeSpecifier:
    def __init__(self, attr_name, *, _previous_spec=None):
        # make sure it does not specify private methods
        assert attr_name.startswith("_") == attr_name.endswith(
            "_"
        ), f"you cannot specify private attributes, found `.{attr_name}`"
        self._attr_name = attr_name
        self._previous_spec = _previous_spec

    def __repr__(self):
        return f"<AttributeSpecifier `{self._source_repr()}`>"

    def _source_repr(self):
        return f"self.{self._attr_name_chain()}"

    def _attr_name_chain(self):
        if self._previous_spec is None:
            return self._attr_name
        else:
            return f"{self._previous_spec._attr_name_chain()}.{self._attr_name}"

    def _get_attribute_(self, src_thing):
        global AttributeSpecifier

        is_first = self._previous_spec is None

        if is_first and isinstance(src_thing, Widget):
            fromthis = src_thing
            # account for non containers
            if not hasattr(fromthis, "_decalrable_"):
                fromthis = src_thing._superior_
            # find the nearest superior that is declarable
            while fromthis._decalrable_ is False:
                fromthis = fromthis._superior_
                if fromthis is None:
                    raise TypeError(f"{self} not used in a declaration")
        elif is_first:
            # get it directly from here
            fromthis = src_thing
        else:  # get it from up the attrspec tree
            assert isinstance(
                self._previous_spec, AttributeSpecifier
            ), f"found {src_thing}"
            fromthis = self._previous_spec._get_attribute_(src_thing)
        # do not store the attr in self b/c widget it could change on a re-place
        return getattr(fromthis, self._attr_name)

    def __getattr__(self, attr_name):
        # chain constructor
        return AttributeSpecifier(attr_name, _previous_spec=self)

    def __call__(self, *args, **kwargs):
        return ForwardMethodCall(self, args, kwargs)


class ForwardMethodCall:
    def __init__(self, attr_spec, args, kwargs):
        self._attr_spec = attr_spec
        self._args = args
        self._kwargs = kwargs

    def __repr__(self):
        arg_stings = tuple(str(arg) for arg in self._args) + tuple(
            f"{kw}={arg}" for kw, arg in self._kwargs.items()
        )
        return (
            f"<ForwardMethodCall `{self._attr_spec._source_repr()}("
            + f"{', '.join(repr(s) for s in arg_stings)}"
            + ")`>"
        )

    def _get_method_(self, widget):
        assert isinstance(widget, Widget)
        bound_method = self._attr_spec._get_attribute_(widget)

        # if there are any attribute or method specifiers pased they need to
        #   be prcessed at the same nest level so they will be processed here
        args = []
        for arg in self._args:
            if isinstance(arg, AttributeSpecifier):
                args.append(arg._get_attribute_(widget))
            elif isinstance(arg, ForwardMethodCall):
                args.append(arg._call_method_(widget))
            else:
                args.append(arg)
        kwargs = {}
        for kw, arg in self._kwargs.items():
            if isinstance(arg, AttributeSpecifier):
                kwargs[kw] = arg._get_attribute_(widget)
            elif isinstance(arg, ForwardMethodCall):
                kwargs[kw] = arg._call_method_(widget)
            else:
                kwargs[kw] = arg

        return lambda: bound_method(*args, **kwargs)

    def _call_method_(self, widget):
        self._get_method_(widget)()


# for import
self = SpecifierConstructor()
self._superior_ = AttributeSpecifier("_superior_")
