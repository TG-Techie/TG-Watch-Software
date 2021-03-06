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

from .base import *
from .attribute_specifier import AttributeSpecifier


def _not(obj):
    return not obj


class State:
    def __init__(self, value, repr=repr):
        self._id_ = uid()
        self._value = value

        self._registered = {}
        self._single_upate_handlers = []

        self._repr = repr

    def update(self, value):
        if value != self._value:
            self._value = value
            self._alert_registered()

    def value(self):
        return self._value

    def __repr__(self):
        return f"<{type(self).__name__}:{self._id_} ({self._repr(self._value)})>"

    def __get__(self, owner, ownertype):
        """
        For using states as values in functions, great for button actions.
        """
        return self._value

    def __set__(self, owner, value):
        """
        For using states as values in functions, great for button actions.
        """
        self.update(value)

    def _register_handler_(self, key, handler):
        if key is None:
            self._single_upate_handlers.append(handler)
        elif key not in self._registered:
            if hasattr(key, "_id_"):
                key = key._id_
            self._registered[key] = handler
        else:
            raise ValueError(f"{self} already has a handler registered for  {key}")

    def _deregister_handler_(self, key):
        registered = self._registered
        if hasattr(key, "_id_"):
            key = key._id_
        if key in registered:
            registered.pop(key)

    def _alert_registered(self):
        value = self._value
        for handler in self._single_upate_handlers:
            handler(value)
        for handler in self._registered.values():
            handler(value)

    def __rshift__(self, fn):
        return DerivedState(self, fn)

    @classmethod
    def __bool__(cls):
        raise TypeError(f"'{cls.__name__}' objects cannot be cast to bools")

    def __invert__(self):
        return DerivedState(self, _not)


class DerivedState(State):
    def __init__(self, states, fn):
        if isinstance(states, State):
            states = (states,)
        elif isinstance(states, tuple):
            pass
        else:
            raise ValueError(f"argument states must be a State or tuple of States")

        self._states = states
        self._fn = fn

        super().__init__(
            value=self,
        )

        self._register_with_sources()
        self._update_from_sources(None)

    def update(self, value):
        raise TypeError(f"you cannot set the state of {self}, tried to set to {value}")

    def __repr__(self):
        return f"<DerivedState:{self._id_} {self._states}>"

    def _update_from_sources(self, _):
        value = self._derive_new_state()
        super().update(value)

    def _derive_new_state(self):
        substates = [state.value() for state in self._states]
        return self._fn(*substates)

    def _register_with_sources(self):
        for state in self._states:
            state._register_handler_(self, self._update_from_sources)

    def _deregister_from_sources(self):
        for state in self._states:
            state._deregister_handler_(self)


class StatefulAttribute:
    def __init__(self, initfn, *, private_name=None, _updatefn=None):
        global uid

        self._id_ = id = uid()

        if private_name is None:
            private_name = f"_stateful_attr_{id}_"

        self._initfn = initfn
        self._privname = private_name
        self._updatefn = _updatefn

    def __call__(self, fn):
        if self._updatefn is None:
            self._updatefn = fn
            self._privname = f"_stateful_attr_{fn.__name__}"
        else:
            raise ValueError(
                f"{self} alreayd has an update function {self._updatefn}, got {fn}"
            )
        return self

    def __get__(self, owner, ownertype):
        return self._get_val(owner)

    def _get_val(self, owner):
        privname = self._privname
        if not hasattr(owner, privname):
            value = self._initfn(owner)
            setattr(owner, privname, value)
        else:
            value = getattr(owner, privname)
        return value

    def __set__(self, owner, value):
        # print('__set__', self, owner, value)
        if value != self._get_val(owner):
            setattr(owner, self._privname, value)
            if self._updatefn is not None:
                self._updatefn(owner)


def src_to_value(*, src, widget, handler, default):
    if src is None:
        val = default
    elif isinstance(src, State):
        val = src.getvalue(widget, handler)
    else:
        val = src
    return val


def unlink_from_src(*, src, widget):
    if isinstance(src, State):
        src._deregister_handlers_(widget)
