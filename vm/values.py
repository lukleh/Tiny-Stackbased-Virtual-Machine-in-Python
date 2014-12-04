# -*- coding: utf-8  -*-
from types import MethodType

from vm.exceptions import ValueException


class Value():
    vtype = None
    ex_message = 'base value'

    def __init__(self, value=None):
        if value is None or self.validatevalue(value):
            self.value = value
        else:
            raise ValueException(self.ex_message)

    def __eq__(self, other):
        return self.value == other.value

    @classmethod
    def validatevalue(cls, value):
        return isinstance(value, cls.vtype)

    @classmethod
    def convertvalue(cls, value):
        return cls.vtype(value)

    @property
    def is_none(self):
        return self.value is None

    @classmethod
    def is_type(cls, o):
        return cls is o.__class__

    def copy(self):
        return self.__class__(self.value)

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.value)

    def __repr__(self):
        return self.__str__()


class ValueInt(Value):
    vtype = int
    ex_message = 'value not an int'


class ValueFloat(Value):
    vtype = float
    ex_message = 'value not an float'


class ValueReference(Value):
    pass


class ArrayObjectRef(ValueReference):
    _array = None
    _size = 0

    def __init__(self, value=None):
        super().__init__(value)
        if value is not None:
            self._array = self.value
            self._size = len(self.value)

    def allocate(self, asize=None):
        if asize < 1:
            raise ValueException('arrayobject must have size more than 0')
        if self._array is not None:
            raise ValueException('arrayobject already initialized')
        self._array = [None] * asize
        self._size = asize

    def __getitem__(self, i):
        v = self._array[i]
        if v is not None:
            return v
        else:
            return self.atype()

    def __setitem__(self, k, v):
        if not isinstance(v, self.atype):
            raise ValueException('%s not type of %s' % (v, self.atype))
        self._array[k] = v

    @classmethod
    def is_type(cls, o):
        return issubclass(o.__class__, cls)

    def contains_type(self, t):
        return self.atype is t

    @property
    def is_none(self):
        return self._array is None

    @property
    def length(self):
        return self._size

    @classmethod
    def convertvalue(cls, value):
        return [cls.atype(v) for v in value]

    @classmethod
    def validatevalue(cls, value):
        return all([isinstance(v, cls.atype) for v in value])


class ValueIntArrayRef(ArrayObjectRef):
    atype = ValueInt


class ValueFloatArrayRef(ArrayObjectRef):
    atype = ValueFloat


types = {
    'int': ValueInt,
    'float': ValueFloat,
    'intarray': ValueIntArrayRef,
    'floatarray': ValueFloatArrayRef
}