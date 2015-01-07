# -*- coding: utf-8  -*-

from .exceptions import ValueException
from . import value_types


class Value():
    vtype = None

    def __init__(self, value=None):
        self.value = value

    def __eq__(self, other):
        return self.vtype == other.vtype and self.value == other.value

    @property
    def is_none(self):
        return self.value is None

    def set_value(self, v):
        self.value = v

    def copy(self):
        return self.__class__(self.value)

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.value)

    def __repr__(self):
        return self.__str__()


class ValueInt(Value):
    vtype = value_types.INT

    def __add__(self, other):
        return ValueInt(self.value + other.value)

    def __sub__(self, other):
        return ValueInt(self.value - other.value)

    def __mul__(self, other):
        return ValueInt(self.value * other.value)

    def __floordiv__(self, other):
        return ValueInt(self.value // other.value)


class ValueFloat(Value):
    vtype = value_types.FLOAT

    def __add__(self, other):
        return ValueFloat(self.value + other.value)

    def __sub__(self, other):
        return ValueFloat(self.value - other.value)

    def __mul__(self, other):
        return ValueFloat(self.value * other.value)

    def __truediv__(self, other):
        return ValueFloat(self.value / other.value)


class ValueReference(Value):
    pass


class ArrayObjectRef(ValueReference):
    vtype = value_types.ARRAY
    _size = 0

    def __init__(self, value=None):
        super().__init__(value)
        if value is not None:
            self._size = len(value)

    def allocate(self, asize=None):
        if asize < 1:
            raise ValueException('arrayobject must have size more than 0')
        if self.value is not None:
            raise ValueException('arrayobject already initialized')
        self._size = asize

    def __getitem__(self, i):
        return self.value[i]

    def __setitem__(self, k, v):
        self.value[k] = v

    def set_value(self, v):
        super().set_value(v)
        if self.value is not None:
            self._size = len(self.value)

    @property
    def length(self):
        return self._size


class ValueIntArrayRef(ArrayObjectRef):
    vtype = value_types.INT_ARRAY

    def allocate(self, asize=None):
        super().allocate(asize)
        self.value = [ValueInt()] * asize


class ValueFloatArrayRef(ArrayObjectRef):
    vtype = value_types.FLOAT_ARRAY

    def allocate(self, asize=None):
        super().allocate(asize)
        self.value = [ValueFloat()] * asize


types = {
    'int': ValueInt,
    'float': ValueFloat,
    'intarray': ValueIntArrayRef,
    'floatarray': ValueFloatArrayRef
}


def convert_values(container_class, value):
    if container_class.vtype == value_types.INT:
        return int(value)
    elif container_class.vtype == value_types.FLOAT:
        return float(value)
    elif container_class.vtype == value_types.INT_ARRAY:
        return [ValueInt(int(v)) for v in value]
    elif container_class.vtype == value_types.FLOAT_ARRAY:
        return [ValueFloat(float(v)) for v in value]
    else:
        raise ValueException('cannot convert type %s value %s' % (container_class.vtype, value))
