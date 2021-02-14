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

"""
This file is under active development.
"""


def isvariant(obj, cls):
    if obj._is_single_varnt:
        return obj is cls
    else:
        print(f"(obj, cls)={(obj, cls)}")
        return isinstance(obj, cls)


def _enum_single_varnt(outercls):
    def _enum_nester(subcls):
        assert issubclass(subcls, outercls)
        subcls._is_single_varnt = True
        inst = subcls()
        setattr(outercls, subcls.__name__, inst)
        return inst

    return _enum_nester


def _enum_data_varnt(outercls):
    def _enum_nester(subcls):
        assert issubclass(subcls, outercls)
        subcls._is_single_varnt = False
        setattr(outercls, subcls.__name__, subcls)
        return subcls

    return _enum_nester


# puedo enums
class SizeClass:
    pass


@_enum_single_varnt(SizeClass)
class regular(SizeClass):
    pass


@_enum_single_varnt(SizeClass)
class compact(SizeClass):
    pass


class LayoutCls:
    pass


@_enum_single_varnt(LayoutCls)
class wearable(LayoutCls):
    pass


@_enum_data_varnt(LayoutCls)
class mobile(LayoutCls):
    # width: SizeClass
    # height: SizeClass

    def __init__(self, width, height):
        global SizeClass
        assert isinstance(width, SizeClass)
        assert isinstance(height, SizeClass)
        self.width = width
        self.height = height


# others
