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


class SpecifierReference:
    def __init__(
        self,
        name,
        resolver=(lambda attr_spec, given_ref: given_ref),
        constructs=None,
    ):
        self._name_ = name
        self._resolver = resolver
        self._constructs_type = AttributeSpecifier if constructs is None else constructs

    def __repr__(self):
        return f"<{type(self).__name__} '{self._name_}'>"

    def __getattr__(self, name):
        assert name.startswith("_") == name.endswith(
            "_"
        ), f"cannot specify private atrributes, found .{name}"
        return self._constructs_type(self, (name,))

    def _resolve_reference_(self, attr_spec, ref):
        return self._resolver(attr_spec, ref)


def _specify(spec, ref):
    return spec._resolve_specified_(ref) if isinstance(spec, Specifier) else spec


class Specifier:  # protocol
    def _resolve_specified_(self, _):
        raise NotImplementedError

    def _code_str_(self):
        raise NotImplementedError

    def __str__(self):
        return self._code_str_()

    def __repr__(self):
        return f"<{type(self).__name__}: `{self._code_str_()}`>"


class AttributeSpecifier(Specifier):
    def _code_str_(self):
        return f"{self._spec_ref_._name_}.{'.'.join(self._attr_path)}"

    def __init__(self, spec_ref, attr_path):
        if isinstance(attr_path, str):
            attr_path = (attr_path,)
        assert isinstance(attr_path, tuple), f"found {attr_path}, expected tuple"
        assert isinstance(
            spec_ref, SpecifierReference
        ), f"found {attr_path}, expected SpecifierReference"
        self._attr_path = attr_path
        self._spec_ref_ = spec_ref

    def __getattr__(self, name):
        assert name.startswith("_") == name.endswith(
            "_"
        ), f"cannot specify private atrributes, found .{name}"
        return type(self)(
            self._spec_ref_,
            self._attr_path + (name,),
        )

    def __call__(self, *args, **kwargs):
        return ForwardMethodCall(self, args, kwargs)

    def _resolve_specified_(self, ref):
        attr = self._spec_ref_._resolve_reference_(self, ref)
        for attrname in self._attr_path:
            attr = getattr(attr, attrname)
        return attr

    def _set_specified_(self, *_, **__):
        raise NotImplementedError


class ForwardMethodCall(Specifier):
    def __init__(self, method_spec, args, kwargs):
        assert isinstance(method_spec, AttributeSpecifier)
        self._method_spec = method_spec
        self._args = args
        self._kwargs = kwargs
        self._code_str = None

    def _code_str_(self):
        if self._code_str is None:
            args = tuple(str(arg) for arg in self._args)
            kwargs = tuple(f"{kw}={str(arg)}" for kw, arg in self._kwargs.items())

            self._code_str = (
                f"{self._method_spec._code_str_()}({', '.join(args+kwargs)})"
            )
        return self._code_str

    def _resolve_specified_(self, ref):
        # find method
        method = self._method_spec._resolve_specified_(ref)
        # assemble args and kwargs if they are specifiers
        # these will be re-used so are not interators
        args = tuple(_specify(arg, ref) for arg in self._args)
        kwargs = {kw: _specify(arg, ref) for kw, arg in self._kwargs.items()}
        return lambda: method(*args, **kwargs)
