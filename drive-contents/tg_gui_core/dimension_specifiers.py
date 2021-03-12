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
This file is under active development. (it also requires some docs and commentsm, blame TG-Techie)
"""

from .constant_groups import ConstantGroup


class DimensionSpecifier:
    def _calc_dim_(self, inst):
        raise NotImplementedError("cannot use a bare DimensionSpecifier")


_operations = ConstantGroup(
    "operation",
    ("add", "sub", "rsub", "mul", "floordiv"),
)

_dimensions = ConstantGroup(
    "dimension_specifiers",
    ("horizontal", "vertical"),
)

# maually inline this
def _op_fn(operator):
    # used to define the dunder methods in the DimensionExpression
    def _op_fn_(self, other):
        op = (operator, other)
        dims = _dimensions
        return DimensionExpression(
            self._operation_sequence + (op,),
            dims.horizontal if self._is_horizontal else dims.vertical,
        )

    return _op_fn_


class DimensionExpression:

    operations = _operations

    _dimensions = _dimensions

    def __init__(self, operations, dimension):
        self._is_horizontal = bool(dimension is _dimensions.horizontal)
        self._operation_sequence = operations

    def __repr__(self):
        dimension = "width" if self._is_horizontal else "height"
        return f"<DimensionExpression:{dimension} {id(self)}>"

    # TODO: add prety repr version.
    # tho it is a but expensive and possible large for regular repr
    __floordiv__ = _op_fn(_operations.floordiv)

    __add__ = _op_fn(_operations.add)
    __radd__ = _op_fn(_operations.add)

    __mul__ = _op_fn(_operations.mul)
    __rmul__ = _op_fn(_operations.mul)

    __sub__ = _op_fn(_operations.sub)
    __rsub__ = _op_fn(_operations.rsub)

    def _calc_dim(self, dims):
        ops = _operations
        running_value = dims[0] if self._is_horizontal else dims[1]
        for op, value in self._operation_sequence:
            # if it is also a DimExpr, simplify it
            if isinstance(value, DimensionExpression):
                value = value._calc_dim(dims)
            assert isinstance(value, int), f"found `{repr(value)}`"
            # apply the operation
            if op is ops.floordiv:
                running_value //= value
            elif op is ops.mul:
                running_value *= value
            elif op is ops.add:
                running_value += value
            elif op is ops.sub:
                running_value -= value
            elif op is ops.rsub:
                running_value = value - running_value
            else:
                raise ValueError(f"unknown operator {repr(op)}")
        else:
            return running_value


# maually inline this
def _op_constr_fn(operator):
    def _op_constr_fn_(self, value):
        op = (operator, value)
        return DimensionExpression((op,), self._dim)

    return _op_constr_fn_


class DimensionExpressionConstructor:
    def __init__(self, *, name, dimension):
        self._name = name
        self._dim = dimension

    def __repr__(self):
        return f"<DimensionExpressionConstructor '{self._name}'>"

    __floordiv__ = _op_constr_fn(_operations.floordiv)

    __add__ = _op_constr_fn(_operations.add)
    __radd__ = _op_constr_fn(_operations.add)

    __mul__ = _op_constr_fn(_operations.mul)
    __rmul__ = _op_constr_fn(_operations.mul)

    __sub__ = _op_constr_fn(_operations.sub)
    __rsub__ = _op_constr_fn(_operations.rsub)


# for import
class ratio(DimensionSpecifier):
    def __init__(self, expr):
        self._base_expr = expr

    def _calc_dim_(self, inst):
        return self._base_expr._calc_dim(inst.dims)


height = DimensionExpressionConstructor(
    name="height",
    dimension=_dimensions.vertical,
)

width = DimensionExpressionConstructor(
    name="width",
    dimension=_dimensions.horizontal,
)
