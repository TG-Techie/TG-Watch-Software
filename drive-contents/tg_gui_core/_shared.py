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

import random as _random


_next_id = _random.randint(0, 11)
del _random


def uid():
    global _next_id
    id = _next_id
    _next_id += 1
    return id


def clamp(lower, value, upper):
    return min(max(lower, value), upper)


# TODO: refactor into pigeon enums with sub-typing
class Constant:
    def __init__(self, outer, name):
        self._name = name
        self._outer = outer

    def __repr__(self):
        return f"<Constant {self._outer._name}.{self._name}>"


class ConstantGroup:
    def __init__(self, name, subs):
        self._name = name
        self._subs = subs_dict = {
            sub_name: Constant(self, sub_name) for sub_name in subs
        }
        for name, sub in subs_dict.items():
            setattr(self, name, sub)

    def __repr__(self):
        return f"<ConstantGroup {self._name}>"
