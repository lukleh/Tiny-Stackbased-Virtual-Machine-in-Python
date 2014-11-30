# -*- coding: utf-8  -*-
from vm.exceptions import ValueException, RuntimeException


class Value():
    vtype = None
    ex_message = 'base value'
    is_string = False
    is_int = False
    is_float = False

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


class ValueString(Value):
    vtype = str
    ex_message = 'value not an string'
    is_string = True


class ValueInt(Value):
    vtype = int
    ex_message = 'value not an int'
    is_int = True


class ValueFloat(Value):
    vtype = float
    ex_message = 'value not an float'
    is_float = True


types = {
    'int': ValueInt,
    'float': ValueFloat
}