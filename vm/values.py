# -*- coding: utf-8  -*-
from vm.exceptions import ValueException


class Value():
    vtype = lambda x: x
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

    def copy(self):
        return self.__class__(self.value)

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.value)

    def __repr__(self):
        return self.__str__()


class ValueString(Value):
    vtype = str
    ex_message = 'value not an string'


class ValueInt(Value):
    vtype = int
    ex_message = 'value not an int'


class ValueFloat(Value):
    vtype = float
    ex_message = 'value not an float'
